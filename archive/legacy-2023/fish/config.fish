if status is-login
	ssh-add ~/.ssh/martines_github
end

load_nvm > /dev/stderr

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
eval /home/martines/miniconda3/bin/conda "shell.fish" "hook" $argv | source
# <<< conda initialize <<<
