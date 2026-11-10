#!/bin/bash
sketchybar --add item wifi right --set wifi \
  label.width=0 label.color="$GREY" icon="$WIFI_DISCONNECTED" \
  script="$PLUGIN_DIR/wifi.sh" --subscribe wifi wifi_change system_woke mouse.clicked
