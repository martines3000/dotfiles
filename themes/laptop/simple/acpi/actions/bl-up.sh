#!/bin/sh
bl_device=/sys/class/backlight/intel_backlight/brightness
echo $(($(cat $bl_device)+1000)) | sudo tee $bl_device
