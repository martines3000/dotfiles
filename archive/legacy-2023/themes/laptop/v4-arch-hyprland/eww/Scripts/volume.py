#!/usr/bin/python

import subprocess

icon_muted = "󰖁"

#Get current volume status
volume = subprocess.run("pamixer --get-volume",
                                shell = True,
                                capture_output=True).stdout.decode("utf-8")

#if returned string is 0 means the volume is not muted
if int(volume) == 0:
	print(icon_muted)
else:
	print(f"{volume}")
