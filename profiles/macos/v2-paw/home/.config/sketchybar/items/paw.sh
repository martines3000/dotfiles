#!/bin/bash

sketchybar --add event paw_changed

# shortcut: show numbered workspaces 1–12, use dynamic items if you need more or named workspaces.
for sid in {1..12}; do
  sketchybar --add item paw.space.$sid left \
    --set paw.space.$sid \
      drawing=off icon="$sid" icon.padding_left=10 icon.padding_right=10 \
      padding_left=2 padding_right=2 label.padding_right=20 \
      icon.highlight_color="$BLUE" label.color="$GREY" label.highlight_color="$WHITE" \
      label.font="sketchybar-app-font:Regular:16.0" label.y_offset=-1 \
      background.color="$BACKGROUND_1" background.border_color="$BACKGROUND_2" \
      script="$PLUGIN_DIR/paw.sh" \
    --subscribe paw.space.$sid mouse.clicked
done

sketchybar --add item space_creator left \
  --set space_creator icon=􀆊 icon.font="$FONT:Heavy:16.0" \
    padding_left=10 padding_right=8 label.drawing=off display=active \
    icon.color="$WHITE" script="$PLUGIN_DIR/paw.sh" \
  --subscribe space_creator mouse.clicked

sketchybar --add item paw.state left \
  --set paw.state display=active label.font="$FONT:Bold:12.0" \
    icon.font="$FONT:Bold:16.0" script="$PLUGIN_DIR/paw.sh" \
  --subscribe paw.state paw_changed system_woke display_change mouse.clicked
