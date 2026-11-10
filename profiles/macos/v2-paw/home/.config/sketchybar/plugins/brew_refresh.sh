#!/bin/bash
# Run outside Sketchybar's process limits. Preserve stale data on brew failures.
set -eu
umask 077
ulimit -n 65536 2>/dev/null || true
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/sketchybar"
mkdir -p "$cache_dir"
cache="$cache_dir/brew_outdated"
temporary=$(mktemp "$cache_dir/.brew-outdated.XXXXXX")
trap 'rm -f "$temporary"' EXIT
if outdated=$(HOMEBREW_NO_AUTO_UPDATE=1 brew outdated --quiet 2>/dev/null); then
  count=$(printf '%s' "$outdated" | awk 'NF {n++} END {print n+0}')
  printf '%s\n' "$count" > "$temporary"
else
  last=$(cat "$cache" 2>/dev/null || true)
  last=${last%!}
  [[ "$last" =~ ^[0-9]+$ ]] || last='?'
  printf '%s!\n' "$last" > "$temporary"
fi
mv "$temporary" "$cache"
if command -v sketchybar >/dev/null; then sketchybar --trigger brew_update; fi
