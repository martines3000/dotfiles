#!/bin/bash

update() {
  IS_VPN=$(scutil --nwi | grep -m1 'utun' | awk '{ print $1 }')
  IP_ADDRESS=$(scutil --nwi | grep address | sed 's/.*://' | tr -d ' ' | head -1)
  source "$CONFIG_DIR/colors.sh"
  source "$CONFIG_DIR/icons.sh"
  # Current macOS restricts SSID access; show interface state without the removed airport tool.
  WIFI_DEVICE=$(networksetup -listallhardwareports | awk '/Hardware Port: (Wi-Fi|AirPort)/ {getline; print $2; exit}')
  INFO=""
  if [ -n "$WIFI_DEVICE" ] && scutil --nwi | awk -v device="$WIFI_DEVICE" '$1 == device {found=1} END {exit !found}'; then
    INFO="Wi-Fi"
  fi
  LABEL="$INFO $IP_ADDRESS"
  COLOR="$BACKGROUND_1"
  if [[ "$IS_VPN" != "" ]]; then
    COLOR=$BLUE
    ICON="$VPN"
    LABEL="VPN"
  elif [ -n "$INFO" ]; then
    ICON="$WIFI_CONNECTED"
    animate_close
  else
    ICON="$WIFI_DISCONNECTED"
    animate_close
  fi
  sketchybar --animate sin 10 --set $NAME icon="$ICON" label="$LABEL" background.color=$COLOR
  if [[ "$IS_VPN" != "" ]]; then
    animate_open
  fi
}

animate_open() {
  WIDTH=dynamic
  sketchybar --animate sin 10 --set $NAME label.width="$WIDTH"
}

animate() {
  CURRENT_WIDTH="$(sketchybar --query $NAME | jq -r .label.width)"
  WIDTH=0
  if [ "$CURRENT_WIDTH" -eq "0" ]; then
    WIDTH=dynamic
  fi
  sketchybar --animate sin 10 --set $NAME label.width="$WIDTH"
}

animate_close() {
  WIDTH=0
  sketchybar --animate sin 10 --set $NAME label.width="$WIDTH"
}

click() {
  IS_VPN=$(scutil --nwi | grep -m1 'utun' | awk '{ print $1 }')
  if [ "$IS_VPN" = "" ]; then
    animate
  fi
}

case "$SENDER" in
  "wifi_change") update
  ;;
  "mouse.clicked") click
  ;;
esac
