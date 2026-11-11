#!/bin/bash
if [ "$SENDER" = mouse.clicked ]; then
  case "$NAME" in
    space_creator) paw workspace new ;;
    paw.state) paw toggle float ;;
    paw.space.*)
      sid=${NAME#paw.space.}
      [[ "$sid" =~ ^([1-9]|1[0-2])$ ]] || exit 1
      if [ "$BUTTON" = right ]; then
        paw "workspace $sid; workspace close"
      else
        paw workspace "$sid"
      fi ;;
  esac
  exit
fi
[ "$NAME" = paw.state ] || exit 0
workspaces=$(paw query --json) || exit 1
source "$CONFIG_DIR/colors.sh"
source "$CONFIG_DIR/icons.sh"
args=()
# Focus changes only redraw the state, not every workspace and app glyph.
if [ "$SENDER" != paw_focus ]; then
  for sid in {1..12}; do args+=(--set paw.space.$sid drawing=off); done
  while IFS=$'\t' read -r sid focused visible display apps; do
    [[ "$sid" =~ ^([1-9]|1[0-2])$ ]] || continue
    [[ "$display" =~ ^[1-9][0-9]*$ ]] || display=active
    label=""
    label_drawing=off
    number_right=10
    if [ -n "$apps" ]; then
      IFS=$'\x1f' read -r -a app_names <<< "$apps"
      for app in "${app_names[@]}"; do
        [ -z "$label" ] || label+=" "
        label+="$("$CONFIG_DIR/plugins/icon_map.sh" "$app")"
      done
      label_drawing=on
      number_right=0
    fi
    color=$TRANSPARENT
    [ "$visible" = true ] && color=$BACKGROUND_2
    args+=(--set paw.space.$sid drawing=on display="$display" \
      icon.highlight="$focused" icon.padding_right="$number_right" \
      label.highlight="$focused" label="$label" label.drawing="$label_drawing" background.color="$color")
  done < <(printf '%s' "$workspaces" | jq -r '.[] | [.name, .focused, .visible, (.arrangement // 0), ([.windows[].app] | unique | .[:4] | join("\u001f"))] | @tsv')
fi
layout=$(printf '%s' "$workspaces" | jq -r 'first(.[] | select(.focused)) | if . == null then "offline" elif any(.windows[]; .focused and .floating) then "float" else .layout end')
case "$layout" in
  float) icon=$YABAI_FLOAT; color=$YELLOW ;;
  stack) icon=$YABAI_STACK; color=$MAGENTA ;;
  *) icon=$YABAI_GRID; color=$BLUE ;;
esac
args+=(--set paw.state icon="$icon" label="$layout" icon.color="$color")
sketchybar "${args[@]}"
