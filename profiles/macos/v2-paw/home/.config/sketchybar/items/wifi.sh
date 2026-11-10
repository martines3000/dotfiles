#!/bin/bash
sketchybar --add item vpn right --set vpn drawing=off icon="$VPN" label.drawing=off
sketchybar --add item wifi right --set wifi \
  label.width=0 label.color="$GREY" icon="$WIFI_DISCONNECTED" \
  update_freq=30 \
  script="$PLUGIN_DIR/wifi.sh" --subscribe wifi wifi_change system_woke mouse.clicked
