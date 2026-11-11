#!/bin/bash
sketchybar --add item battery right --set battery \
  script="$PLUGIN_DIR/battery.sh" icon.font="$FONT:Regular:17.0" \
  label.drawing=on label.color="$GREY" update_freq=120 updates=on \
  --subscribe battery power_source_change system_woke
