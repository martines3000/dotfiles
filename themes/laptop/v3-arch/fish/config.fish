if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
eval /home/martines/miniconda3/bin/conda "shell.fish" "hook" $argv | source
# <<< conda initialize <<<


export PATH="$PATH:/home/martines/.foundry/bin"
set -gx VOLTA_HOME "$HOME/.volta"
set -gx PATH "$VOLTA_HOME/bin" $PATH