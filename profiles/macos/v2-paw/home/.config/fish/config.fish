set -gx LANG en_US.UTF-8

if status is-interactive; and type -q starship
    starship init fish | source
end

# Optional toolchains stay local; they are not prerequisites for opening a terminal.
if test -s "$HOME/.jabba/jabba.fish"
    source "$HOME/.jabba/jabba.fish"
end
if test -f "$HOME/.config/tabtab/fish/__tabtab.fish"
    source "$HOME/.config/tabtab/fish/__tabtab.fish"
end
if test -d "$HOME/Library/Android/sdk"
    set -gx ANDROID_HOME "$HOME/Library/Android/sdk"
    fish_add_path "$ANDROID_HOME/platform-tools" "$ANDROID_HOME/emulator"
end
if test -d "$HOME/.foundry/bin"
    fish_add_path "$HOME/.foundry/bin"
end
