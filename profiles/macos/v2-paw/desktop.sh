#!/bin/bash
# Desktop appearance only; no files or widget arrangements are deleted.
set -eu
if [ "$(uname -s)" != Darwin ]; then echo "This script requires macOS." >&2; exit 1; fi
defaults write com.apple.finder CreateDesktop -bool false
defaults write com.apple.WindowManager StandardHideWidgets -int 1
defaults write com.apple.WindowManager StageManagerHideWidgets -int 1
killall Finder 2>/dev/null || true
killall Dock 2>/dev/null || true
