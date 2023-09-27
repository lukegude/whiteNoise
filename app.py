from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import subprocess, os, signal, time, sys, threading


alarm_time = None
alarm_thread_stopped = False
noise_thread_stopped = False
alarm_playing_thread_stopped = False


def start_white_noise():
    global noise_thread_stopped
    noise_thread_stopped = False
    p1 = subprocess.Popen(["./out", "-w"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sox", "-t", "raw", "-b", "32", "-c", "2", "-e", "signed", "-r", "44100", "-", "-t", "raw", "-", "bass", "+20", "lowpass","20000"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["play", "-t", "raw", "-b", "32", "-c", "2", "-e", "signed", "-r", "44100", "-"], stdin=p2.stdout, stdout=subprocess.PIPE)
    # Check if the noise thread is false
    while not noise_thread_stopped:
        pass
    print('Noise thread stopped')
    p1.kill()
    p2.kill()
    p3.kill()

    return



def start_brown_noise():
    global noise_thread_stopped
    noise_thread_stopped = False
    p1 = subprocess.Popen(["./out", "-b"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["sox", "-t", "raw", "-b", "32", "-c", "2", "-e", "signed", "-r", "44100", "-", "-t", "raw", "-", "lowpass", "300"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["play", "-t", "raw", "-b", "32", "-c", "2", "-e", "signed", "-r", "44100", "-"], stdin=p2.stdout, stdout=subprocess.PIPE)
    # Check if the noise thread is false
    while not noise_thread_stopped:
        pass
    print('Noise thread stopped')
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
            if thread.name == 'noise_thread':
                noise_thread_stopped = True
                if thread.is_alive():
                    thread.join()

    p1 = subprocess.Popen(["play", "alarm/early_riser.mp3"], stdout=subprocess.PIPE)
    while not alarm_playing_thread_stopped:
        pass
    p1.kill()
    threading.Thread(target=start_white_noise, name='noise_thread').start()
    return



def alarm_thread():
    global alarm_time, alarm_thread_stopped, noise_thread_stopped
    alarm_thread_stopped = False
    # Print alarm time
    print('Alarm set for {}'.format(alarm_time.strftime('%I:%M %p')))
    while not alarm_thread_stopped:
        if alarm_time and datetime.now() >= alarm_time:
            print('Alarm time!')
            play_alarm()
            alarm_time = None  # Reset the alarm
            with open('alarm.txt', 'w') as f:
                f.write('')
                alarm_thread_stopped = True
        time.sleep(10)  # Check every 10 seconds

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form)
        if 'bt' in request.form:
            return redirect(url_for('bluetooth_scan'))
        if 'wn' in request.form or 'bn' in request.form:
            global noise_thread_stopped
            if threading.active_count() > 1:
                print(threading.active_count(),'\n' ,threading.enumerate())
                for thread in threading.enumerate():
                    if thread.name == 'noise_thread' or thread.name == 'process_request_thread':
                        noise_thread_stopped = True
                        if thread.is_alive():
                            thread.join()
            if 'wn' in request.form:
                print('Starting white noise')
                threading.Thread(target=start_white_noise, name='noise_thread').start()
            if 'bn' in request.form:
                print('Starting brown noise')
                threading.Thread(target=start_brown_noise, name='noise_thread').start()


        if 'stop' in request.form:
            global alarm_playing_thread_stopped
            if not alarm_playing_thread_stopped:
                alarm_playing_thread_stopped = True
            else:
                noise_thread_stopped = True
    if alarm_time:
        formatted_alarm_time = alarm_time.strftime('%I:%M %p')
    else:
        formatted_alarm_time = None
    return render_template('index.html', alarm_time=formatted_alarm_time)


@app.route('/stop_alarm', methods=['GET', 'POST'])
def stop_alarm():
    if request.method == 'POST':
        global alarm_playing_thread_stopped
        alarm_playing_thread_stopped = True
        if threading.active_count() > 1:
            for thread in threading.enumerate():
                print(thread.name)
                if thread.name == 'alarm_playing_thread':
                    alarm_playing_thread_stopped = True
                    if thread.is_alive():
                        thread.join()
        return redirect(url_for('index'))

    return render_template('stop.html')


@app.route('/bluetooth/scan', methods=['GET', 'POST'])
def bluetooth_scan():
    subprocess.Popen(["./bt.sh"], stdout=subprocess.PIPE)
    return redirect(url_for('index'))

@app.route('/alarm', methods=['GET', 'POST'])
def alarm():
    if request.method == 'POST':
        global alarm_time
        alarm_time = datetime.strptime(request.form['i_time'], '%I:%M %p')
        alarm_time = alarm_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        if alarm_time < datetime.now():
            alarm_time += timedelta(days=1)

        # Write the alarm time to a file so the background thread can access it
        with open('alarm.txt', 'w') as f:
            f.write(alarm_time.strftime('%Y-%m-%d %H:%M:%S'))

        if threading.active_count() > 1:
            for thread in threading.enumerate():
                print(thread.name)
                if thread.name == 'alarm_thread':
                    alarm_thread_stopped = True
                    if thread.is_alive():
                        thread.join()
        print(threading.enumerate())
        threading.Thread(target=alarm_thread, name='alarm_thread').start()
        return redirect(url_for('index'))
    return render_template('alarm.html')


if __name__ == '__main__':
    with open('alarm.txt', 'r') as f:
        try:
            alarm_time = datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S')
            threading.Thread(target=alarm_thread).start()
        except ValueError:
            alarm_time = None
    app.run(debug=True)





