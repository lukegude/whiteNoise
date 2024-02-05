#!/bin/sh
bluetoothctl -- scan on & sleep 5 && bluetoothctl -- scan off & sleep 5
bluetoothctl -- remove B8:F6:53:9B:56:43
bluetoothctl -- pair B8:F6:53:9B:56:43
echo Pairing...
sleep 5
bluetoothctl -- trust B8:F6:53:9B:56:43
echo Trusting...
bluetoothctl -- connect B8:F6:53:9B:56:43
echo Connecting...

sleep 5
ps | grep bluetoothctl | awk '{print $1;}'| xargs kill
exit
