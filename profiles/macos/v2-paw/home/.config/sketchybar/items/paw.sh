#!/bin/bash
sketchybar --add event paw_changed --add event paw_focus
# shortcut: numbered workspaces 1–12; add named/dynamic items before using a side workspace.
for sid in {1..12}; do
  sketchybar --add item paw.space.$sid left --set paw.space.$sid \
    drawing=off icon="$sid" icon.padding_left=5 icon.padding_right=3 \
    padding_left=1 padding_right=1 label.padding_right=5 \
    icon.highlight_color="$YELLOW" label.color="$GREY" label.highlight_color="$WHITE" \
    label.font="sketchybar-app-font:Regular:13.0" \
    background.color="$TRANSPARENT" script="$PLUGIN_DIR/paw.sh" \
    --subscribe paw.space.$sid mouse.clicked
done
sketchybar --add item space_creator left --set space_creator \
  icon=􀆊 icon.font="$FONT:Regular:12.0" icon.color="$GREY" \
  padding_left=4 padding_right=4 label.drawing=off display=active \
  script="$PLUGIN_DIR/paw.sh" --subscribe space_creator mouse.clicked
sketchybar --add item paw.state left --set paw.state \
  display=active label.font="$FONT:Medium:10.0" label.color="$GREY" \
  icon.font="$FONT:Regular:13.0" padding_right=7 script="$PLUGIN_DIR/paw.sh" \
  --subscribe paw.state paw_changed paw_focus system_woke display_change
