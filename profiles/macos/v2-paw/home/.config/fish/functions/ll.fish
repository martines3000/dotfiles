function ll --wraps=ls --wraps='exa -l' --description 'alias ll=exa -l'
  eza -l $argv; 
end
