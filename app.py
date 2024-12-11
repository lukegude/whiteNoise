from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import subprocess, os, signal, time, sys, threading
from flask_wtf.csrf import CSRFProtect



alarm_time = None
alarm_thread_stopped = False
noise_thread_stopped = False
alarm_playing_thread_stopped = False


def start_white_noise():
    global noise_thread_stopped
    noise_thread_stopped = False
    p1 = subprocess.Popen(["./out", "-w"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(
        [
            "sox",
            "-t",
            "raw",
            "-b",
            "32",
            "-c",
            "2",
            "-e",
            "signed",
            "-r",
            "44100",
            "-",
            "-t",
            "raw",
            "-",
            "bass",
            "+20",
            "lowpass",
            "20000",
            "vol",
            "0.35",
        ],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
    )
    p3 = subprocess.Popen(
        [
            "play",
            "-t",
            "raw",
            "-b",
            "32",
            "-c",
            "2",
            "-e",
            "signed",
            "-r",
            "44100",
            "-",
        ],
        stdin=p2.stdout,
        stdout=subprocess.PIPE,
    )
    # Check if the noise thread is false
    while not noise_thread_stopped:
        pass
    print("Noise thread stopped")
    p1.kill()
    p2.kill()
    p3.kill()

    return


def start_brown_noise():
    global noise_thread_stopped
    noise_thread_stopped = False
    p1 = subprocess.Popen(["./out", "-b"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(
        [
            "sox",
            "-t",
            "raw",
            "-b",
            "32",
            "-c",
            "2",
            "-e",
            "signed",
            "-r",
            "44100",
            "-",
            "-t",
            "raw",
            "-",
            "lowpass",
            "300",
        ],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
    )
    p3 = subprocess.Popen(
        [
            "play",
            "-t",
            "raw",
            "-b",
            "32",
            "-c",
            "2",
            "-e",
            "signed",
            "-r",
            "44100",
            "-",
        ],
        stdin=p2.stdout,
        stdout=subprocess.PIPE,
    )
    while not noise_thread_stopped:
        pass
    print("Noise thread stopped")
    p1.kill()
    p2.kill()
    p3.kill()

    return


def play_alarm():
    global alarm_playing_thread_stopped, noise_thread_stopped
    alarm_playing_thread_stopped = False
    noise_thread_stopped = True
    if threading.active_count() > 1:
        for thread in threading.enumerate():
            if thread.name == "noise_thread":
                noise_thread_stopped = True
                if thread.is_alive():
                    thread.join()

    p1 = subprocess.Popen(["play", "alarm/early_riser.mp3"], stdout=subprocess.PIPE)
    while not alarm_playing_thread_stopped:
        pass
    p1.kill()
    threading.Thread(target=start_white_noise, name="noise_thread").start()
    return


def alarm_thread():
    global alarm_time, alarm_thread_stopped, noise_thread_stopped
    alarm_thread_stopped = False
    print("Alarm set for {}".format(alarm_time.strftime("%I:%M %p")))
    while not alarm_thread_stopped:
        now = datetime.now()
        if alarm_time and now >= alarm_time:
            print("Alarm time!")
            play_alarm()
            alarm_time = None
            with open("alarm.txt", "w") as f:
                f.write("")
            alarm_thread_stopped = True
            break
        sleep_time = (alarm_time - now).total_seconds()
        if sleep_time > 0:
            time.sleep(min(sleep_time, 60))


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for development

@app.route("/", methods=["GET", "POST"])
def index():
    global noise_thread_stopped, alarm_playing_thread_stopped

    if request.method == "POST" :
        if "bt" in request.form:
            return redirect(url_for("bluetooth_scan"))

        elif "wn" in request.form or "bn" in request.form:
            noise_thread_stopped = True

            for thread in threading.enumerate():
                if thread.name == "noise_thread":
                    thread.join()
                    break

            if "wn" in request.form:
                threading.Thread(target=start_white_noise, name="noise_thread").start()
            else:
                threading.Thread(target=start_brown_noise, name="noise_thread").start()

        elif "sleep" in request.form:
            subprocess.Popen(["./toggle_touch.sh"], stdout=subprocess.PIPE)

        elif "stop" in request.form:
            alarm_playing_thread_stopped = True
            noise_thread_stopped = True

        else:
            return redirect(url_for("index"))

    formatted_alarm_time = alarm_time.strftime("%I:%M %p") if alarm_time else None

    return render_template("index.html", alarm_time=formatted_alarm_time)


@app.route("/stop_alarm", methods=["GET", "POST"])
def stop_alarm():
    if request.method == "POST":
        global alarm_playing_thread_stopped
        alarm_playing_thread_stopped = True
        if threading.active_count() > 1:
            for thread in threading.enumerate():
                if thread.name == "alarm_playing_thread":
                    alarm_playing_thread_stopped = True
                    if thread.is_alive():
                        try:
                            os.kill(thread.ident, signal.SIGKILL)
                        except OverflowError:
                            print("OverflowError: signed integer is greater than maximum")
        return redirect(url_for("index"))

    return render_template("stop.html")


@app.route("/bluetooth/scan", methods=["GET", "POST"])
def bluetooth_scan():
    subprocess.Popen(["./bt.sh"], stdout=subprocess.PIPE)
    return redirect(url_for("index"))


@app.route("/alarm", methods=["GET", "POST"])
def alarm():
    global alarm_time, alarm_thread_stopped
    if request.method == "POST":
        new_alarm_time = datetime.strptime(request.form["i_time"], "%I:%M %p")
        new_alarm_time = new_alarm_time.replace(
            year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
        )

        if new_alarm_time < datetime.now():
            new_alarm_time += timedelta(days=1)

        if alarm_time:
            alarm_thread_stopped = True
            if threading.active_count() > 1:
                for thread in threading.enumerate():
                    if thread.name == "alarm_thread":
                        if thread.is_alive():
                            thread.join()

        alarm_time = new_alarm_time
        with open("alarm.txt", "w") as f:
            f.write(alarm_time.strftime("%Y-%m-%d %H:%M:%S"))

        threading.Thread(target=alarm_thread, name="alarm_thread").start()
        return redirect(url_for("index"))
    return render_template("alarm.html")


@app.route("/delete_alarm", methods=["GET", "POST"])
def delete_alarm():
    global alarm_time, alarm_thread_stopped
    print("Delete alarm request received")  # Debugging line
    alarm_time = None
    alarm_thread_stopped = True
    if threading.active_count() > 1:
        for thread in threading.enumerate():
            if thread.name == "alarm_thread":
                if thread.is_alive():
                    try:
                        os.kill(thread.ident, signal.SIGKILL)
                    except OverflowError:
                        print("OverflowError: signed integer is greater than maximum")
    with open("alarm.txt", "w") as f:
        f.write("")
    print("Alarm deleted successfully")  # Debugging line
    return redirect(url_for("index"))


if __name__ == "__main__":
    with open("alarm.txt", "r") as f:
        try:
            alarm_time = datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
            threading.Thread(target=alarm_thread).start()
        except ValueError:
            alarm_time = None
    app.run("0.0.0.0",debug=True)