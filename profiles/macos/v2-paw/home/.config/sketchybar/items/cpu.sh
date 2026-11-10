#!/bin/bash
sketchybar --add item cpu.percent right --set cpu.percent \
  icon=CPU icon.font="$FONT:Medium:9.0" icon.color="$GREY" \
  label=––% label.width=35 label.align=right padding_left=5 padding_right=8 \
  update_freq=2 mach_helper="$HELPER"
