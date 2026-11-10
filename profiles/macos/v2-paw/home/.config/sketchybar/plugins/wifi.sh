#!/bin/bash
source "$CONFIG_DIR/colors.sh"
source "$CONFIG_DIR/icons.sh"
if [ "$SENDER" = mouse.clicked ]; then
  width=$(sketchybar --query "$NAME" | jq -r '.label.width')
  target=0
  [ "$width" = 0 ] && target=dynamic
  sketchybar --animate tanh 12 --set "$NAME" label.width="$target"
  exit
fi
network=$(scutil --nwi)
v4=$(printf '%s' "$network" | sed -n '/IPv4 network interface information/,/IPv6/p')
ip=$(printf '%s' "$v4" | awk '/address/ {print $3; exit}')
icon=$WIFI_DISCONNECTED
label=offline
color=$GREY
if printf '%s' "$v4" | grep -Eq 'utun[0-9]+[[:space:]]*:'; then
  icon=$VPN; label=VPN; color=$BLUE
elif [ -n "$ip" ]; then
  icon=$WIFI_CONNECTED; label=$ip; color=$WHITE
  device=$(networksetup -listallhardwareports | awk '/Hardware Port: (Wi-Fi|AirPort)/ {getline; print $2; exit}')
  if [ -n "$device" ] && printf '%s' "$v4" | awk -v d="$device" '$1 == d {found=1} END {exit !found}'; then
    label="Wi-Fi $ip"
  fi
fi
# An active utun is a tunnel hint, not proof that a VPN protects all traffic.
sketchybar --set "$NAME" icon="$icon" label="$label" icon.color="$color" background.drawing=off
