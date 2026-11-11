#!/bin/bash
sketchybar --add slider volume right --set volume \
  script="$PLUGIN_DIR/volume.sh" updates=on label.drawing=off icon.drawing=off \
  slider.width=0 slider.highlight_color="$BLUE" slider.background.height=4 \
  slider.background.corner_radius=2 slider.background.color="$BACKGROUND_2" \
  slider.knob=􀀁 slider.knob.drawing=on \
  --subscribe volume volume_change mouse.clicked
sketchybar --add item volume_icon right --set volume_icon \
  click_script="$PLUGIN_DIR/volume_click.sh" icon.drawing=off \
  label="$VOLUME_100" label.width=20 label.font="$FONT:Regular:14.0"
