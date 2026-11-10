#!/usr/bin/env bash

STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/yabai-presentation"
ACTIVE="$STATE_DIR/active"

mkdir -p "$STATE_DIR"

if [[ -f "$ACTIVE" ]]; then
    # Presentation OFF
    sketchybar --bar hidden=off

    yabai -m config external_bar all:41:0
    yabai -m config top_padding 2

    rm "$ACTIVE"

    echo "Presentation mode OFF"
else
    # Presentation ON
    sketchybar --bar hidden=on

    yabai -m config external_bar off:0:0
    yabai -m config top_padding 0

    touch "$ACTIVE"

    echo "Presentation mode ON"
fi
