if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
eval /opt/miniconda3/bin/conda "shell.fish" "hook" $argv | source
# <<< conda initialize <<<

export PATH="$PATH:/home/martines/.foundry/bin"

[ -s "/home/martines/.jabba/jabba.fish" ]; and source "/home/martines/.jabba/jabba.fish"

# pnpm
set -gx PNPM_HOME "/home/martines/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end