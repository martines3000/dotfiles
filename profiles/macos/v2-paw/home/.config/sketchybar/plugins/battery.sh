#!/bin/bash
source "$CONFIG_DIR/icons.sh"
source "$CONFIG_DIR/colors.sh"
info=$(pmset -g batt)
percentage=$(printf '%s' "$info" | grep -Eo '[0-9]+%' | head -1 | tr -d '%')
if ! [[ "$percentage" =~ ^[0-9]+$ ]]; then
  sketchybar --set "$NAME" drawing=off
  exit
fi
color=$WHITE
case $percentage in
  9[0-9]|100) icon=$BATTERY_100 ;;
  [6-8][0-9]) icon=$BATTERY_75 ;;
  [3-5][0-9]) icon=$BATTERY_50 ;;
  [1-2][0-9]) icon=$BATTERY_25; color=$YELLOW ;;
  *) icon=$BATTERY_0; color=$RED ;;
esac
if [[ "$info" = *'AC Power'* ]]; then icon=$BATTERY_CHARGING; color=$GREEN; fi
sketchybar --set "$NAME" drawing=on icon="$icon" icon.color="$color" label="$percentage%"
