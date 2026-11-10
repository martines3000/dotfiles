#!/bin/bash
sketchybar --add item vpn right --set vpn drawing=off icon=VPN \
  icon.font="$FONT:Semibold:11.0" label.drawing=off popup.align=center \
  script="$PLUGIN_DIR/wifi.sh" \
  --subscribe vpn mouse.entered mouse.exited mouse.exited.global mouse.clicked
sketchybar --add item vpn.connections popup.vpn --set vpn.connections \
  icon.drawing=off label="Connected VPN" label.max_chars=60 \
  padding_left=8 padding_right=8
sketchybar --add item wifi right --set wifi \
  label.width=0 label.color="$GREY" icon="$WIFI_DISCONNECTED" \
  update_freq=30 \
  script="$PLUGIN_DIR/wifi.sh" --subscribe wifi wifi_change system_woke mouse.clicked
