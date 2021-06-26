dir="$HOME/.config/polybar/rofi"
uptime=$(uptime -p | sed -e 's/up //g')

rofi_command="rofi -config $dir/powermenu.rasi"

# Options
shutdown=""
reboot="勒"
lock=""
suspend="鈴"
logout=""

# Confirmation
confirm_exit() {
	rofi -dmenu\
		-i\
		-no-fixed-num-lines\
		-p "Are You Sure? : "\
		-config $dir/confirm.rasi
}

# Variable passed to rofi
options="$lock\n$suspend\n$logout\n$reboot\n$shutdown"

chosen="$(echo "$options" | $rofi_command -dmenu -selected-row 0)"
case $chosen in
    $shutdown)
		systemctl poweroff
        ;;
    $reboot)
		systemctl reboot
        ;;
    $lock)
		i3lock
        ;;
    $suspend)
        amixer set Master mute
        systemctl suspend
        ;;
    $logout)
		i3-msg exit
        ;;
esac