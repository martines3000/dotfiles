#!/bin/bash
source "$CONFIG_DIR/colors.sh"
source "$CONFIG_DIR/icons.sh"
if [ "$NAME" = vpn ]; then
  case "$SENDER" in
    mouse.entered) sketchybar --set vpn popup.drawing=on ;;
    mouse.exited|mouse.exited.global) sketchybar --set vpn popup.drawing=off ;;
    mouse.clicked) sketchybar --set vpn popup.drawing=toggle ;;
  esac
  exit
fi
if [ "$SENDER" = mouse.clicked ]; then
  width=$(sketchybar --query "$NAME" | jq -r '.label.width')
  target=0
  [ "$width" = 0 ] && target=dynamic
  sketchybar --animate tanh 12 --set "$NAME" label.width="$target"
  exit
fi
network=$(scutil --nwi)
# Interface flags can contain "IPv6" too; only a section header ends IPv4.
v4=$(printf '%s' "$network" | sed -n '/^IPv4 network interface information/,/^IPv6 network interface information/p')
ip=$(printf '%s' "$v4" | awk '/address/ {print $3; exit}')
icon=$WIFI_DISCONNECTED
label=offline
color=$GREY
if [ -n "$ip" ]; then
  icon=$WIFI_CONNECTED; label=$ip; color=$WHITE
  device=$(networksetup -listallhardwareports | awk '/Hardware Port: (Wi-Fi|AirPort)/ {getline; print $2; exit}')
  if [ -n "$device" ] && printf '%s' "$v4" | awk -v d="$device" '$1 == d {found=1} END {exit !found}'; then
    label="Wi-Fi $ip"
  fi
fi
vpn_connections=$(scutil --nc list 2>/dev/null)
vpn_names=$(printf '%s\n' "$vpn_connections" | awk -F '"' '
  /[(]Connected[)]/ && NF >= 3 && !seen[$2]++ { if (n++) printf " · "; printf "%s", $2 }')
vpn=off
# Connected services cover VPNs that do not publish an IPv4 utun in --nwi.
if printf '%s' "$vpn_connections" | grep -Fq '(Connected)' || printf '%s' "$v4" | grep -Eq 'utun[0-9]+[[:space:]]*:'; then
  vpn=on
fi
[ -n "$vpn_names" ] || vpn_names="Connected VPN / active tunnel"
sketchybar --set "$NAME" icon="$icon" label="$label" icon.color="$color" background.drawing=off \
  --set vpn drawing="$vpn" icon.color="$BLUE" --set vpn.connections label="$vpn_names"
if [ "$vpn" = off ]; then sketchybar --set vpn popup.drawing=off; fi
