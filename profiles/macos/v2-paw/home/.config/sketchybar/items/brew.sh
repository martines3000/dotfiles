#!/bin/bash
sketchybar --add event brew_update --add item brew left --set brew \
  icon=􀐛 label=? padding_left=6 padding_right=6 script="$PLUGIN_DIR/brew.sh" \
  click_script='launchctl kickstart gui/$(id -u)/local.dotfiles.brew-refresh' \
  --subscribe brew brew_update
