#!/bin/bash
source "$CONFIG_DIR/colors.sh"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/sketchybar/brew_outdated"
count=$(cat "$cache" 2>/dev/null)
color=$GREY
label="?"
if [[ "$count" =~ ^[0-9]+$ ]]; then
  label=$count
  color=$WHITE
  if [ "$count" -eq 0 ]; then color=$GREEN; label=􀆅
  elif [ "$count" -ge 30 ]; then color=$RED
  elif [ "$count" -ge 10 ]; then color=$YELLOW; fi
elif [[ "$count" =~ ^([0-9]+|\?)!$ ]]; then
  label=$count
  color=$ORANGE
fi
sketchybar --set "$NAME" label="$label" icon.color="$color"
