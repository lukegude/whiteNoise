#!/bin/bash

# Turn off the display
vcgencmd display_power 0

# Wait for the specific touch event to turn on the display
while true; do
    # Capture the output of evtest for a limited time. Adjust the time if needed.
    output=$(timeout 1s evtest /dev/input/by-path/platform-fe205000.i2c-event  | grep "type 1 (EV_KEY), code 330 (BTN_TOUCH), value 1")
    if [ ! -z "$output" ]; then
        # Turn on the display and exit
        vcgencmd display_power 1 && sudo sh -c "echo 25 > /sys/class/backlight/10-0045/brightness"
#        vcgencmd display_power 1         

	exit 0

    fi
done

