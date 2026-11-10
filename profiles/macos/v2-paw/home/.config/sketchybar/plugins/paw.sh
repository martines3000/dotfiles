#!/bin/bash

if [ "$SENDER" = "mouse.clicked" ]; then
  case "$NAME" in
    space_creator) paw workspace new ;;
    paw.state) paw toggle float ;;
    paw.space.*)
      sid=${NAME#paw.space.}
      [[ "$sid" =~ ^([1-9]|1[0-2])$ ]] || exit 1
      if [ "$BUTTON" = "right" ]; then
        paw "workspace $sid; workspace close"
      else
        paw workspace "$sid"
      fi
      ;;
  esac
  exit
fi

[ "$NAME" = "paw.state" ] || exit 0
workspaces=$(paw query --json) || exit 1
source "$CONFIG_DIR/colors.sh"
source "$CONFIG_DIR/icons.sh"

args=()
for sid in {1..12}; do
  args+=(--set paw.space.$sid drawing=off)
done

while IFS=$'\t' read -r sid focused visible apps; do
  [[ "$sid" =~ ^([1-9]|1[0-2])$ ]] || continue
  label=""
  if [ -n "$apps" ]; then
    IFS=$'\x1f' read -r -a app_names <<< "$apps"
    for app in "${app_names[@]}"; do
      label+=" $("$CONFIG_DIR/plugins/icon_map.sh" "$app")"
    done
  fi
  color=$BACKGROUND_1
  [ "$visible" = true ] && color=$BACKGROUND_2
  args+=(--set paw.space.$sid drawing=on icon.highlight="$focused"
    label.highlight="$focused" label="$label" background.border_color="$color")
done < <(printf '%s' "$workspaces" | jq -r '.[] | [.name, .focused, .visible, ([.windows[].app] | unique | join("\u001f"))] | @tsv')

layout=$(printf '%s' "$workspaces" | jq -r 'first(.[] | select(.focused)) | if any(.windows[]; .focused and .floating) then "float" else .layout end')
color=$BAR_BORDER_COLOR
case "$layout" in
  float) icon=$YABAI_FLOAT; color=$RED ;;
  stack) icon=$YABAI_STACK; color=$MAGENTA ;;
  *) icon=$YABAI_GRID ;;
esac
args+=(--bar border_color="$color" --set paw.state icon="$icon" label="$layout" icon.color="$color")
sketchybar "${args[@]}"
