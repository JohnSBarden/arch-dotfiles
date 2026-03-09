# .zshrc config
#
# basic zsh/antigen, vim, golang, nvm, setup
#
if [[ -e "${HOME}/.zprofile" ]]; then
  source "${HOME}/.zprofile"
fi

# Grab antigen if we dont have it
if [[ ! -e $HOME/.antigen/antigen.zsh ]]; then
  git clone https://github.com/zsh-users/antigen.git ~/.antigen
fi

# source antigen now
source $HOME/.antigen/antigen.zsh

# grab our aliases if they exist
if [[ -e "${HOME}/.aliases" ]]; then
  # echo "sourcing aliases"
  source "${HOME}/.aliases"
fi

#default folder our NVM install goes to
export NVM_DIR="$HOME/.nvm"

# Load the oh-my-zsh's library.
antigen use oh-my-zsh >/dev/null 2>&1

# Bundles from the default repo (robbyrussell's oh-my-zsh).
antigen bundle git >/dev/null 2>&1
antigen bundle pip >/dev/null 2>&1
antigen bundle command-not-found >/dev/null 2>&1

# vim package manager
antigen bundle vundle >/dev/null 2>&1

#
antigen bundle wd >/dev/null 2>&1

# https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/yarn
antigen bundle yarn >/dev/null 2>&1

# deno
antigen bundle deno >/dev/null 2>&1

# auto suggestions
antigen bundle zsh-users/zsh-autosuggestions >/dev/null 2>&1

# highlighting
antigen bundle zsh-users/zsh-syntax-highlighting >/dev/null 2>&1

# aws auto completions
# https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/aws
antigen bundle aws >/dev/null 2>&1

# kubernetes
antigen bundle kubectl >/dev/null 2>&1
antigen bundle ahmetb/kubectx >/dev/null 2>&1

# always get more efficient
antigen bundle djui/alias-tips >/dev/null 2>&1

# preload nvm for node version management
antigen bundle lukechilds/zsh-nvm >/dev/null 2>&1

#override ctrl to use peco for fuzzy searching of history
antigen bundle jimeh/zsh-peco-history >/dev/null 2>&1

#load up teiler for imagie / screencasting
# todo ::
# antigen bundle carnage/teiler > /dev/null 2>&1

# choose a theme
#antigen theme agnoster > /dev/null 2>&1
antigen theme gallois >/dev/null 2>&1

# Tell antigen that you're done. > /dev/null 2>&1
antigen apply >/dev/null 2>&1

autoload -U +X compinit && compinit
autoload -U +X bashcompinit && bashcompinit

# stern completion
# source <(stern --completion=zsh)

# add our personal bin to path
export PATH=$HOME/.bin/:$PATH

#powerline?
export POWERLINE_CONFIG_COMMAND=$HOME/.local/bin/powerline-config

# add composer to path
export PATH=$PATH:~/.config/composer/vendor/bin/

#golang
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export GOBIN=$GOPATH/bin
export PATH=$PATH:$GOBIN

# rust / cargo
export PATH=$HOME/.cargo/bin:$PATH

# add yarn to bin
# export PATH=$PATH:`yarn global bin`

# add asdf shims
export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"

# configure editors
export VISUAL=vim
export EDITOR="$VISUAL"

# configure browser
export BROWSER="zen"
export PATH=$PATH:/Applications/Firefox.app/Contents/MacOS/firefox-bin
# run this if it stops opening links correctly
#$ xdg-mime default zen-alpha.desktop x-scheme-handler/https x-scheme-handler/http
# and this can check the default
#$ xdg-settings get default-web-browser

# add krew
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

export PATH="$HOME/.config/yarn/global/node_modules/.bin:$PATH"


# place this after nvm initialization!
autoload -U add-zsh-hook
load-nvmrc() {
  local node_version="$(nvm version)"
  local nvmrc_path="$(nvm_find_nvmrc)"

  if [ -n "$nvmrc_path" ]; then
    local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

    if [ "$nvmrc_node_version" = "N/A" ]; then
      nvm install
    elif [ "$nvmrc_node_version" != "$node_version" ]; then
      nvm use
    fi
  elif [ "$node_version" != "$(nvm version default)" ]; then
    echo "Reverting to nvm default version"
    nvm use default
  fi
}
add-zsh-hook chpwd load-nvmrc
load-nvmrc

export PATH=$PATH:$HOME/.spicetify

# Created by `pipx` on 2024-08-01 03:10:34
export PATH="$PATH:$HOME/.local/bin"
alias dotfiles=/usr/bin/git --git-dir=$HOME/workspace/arch-dotfiles --work-tree=$HOME

export RANGER_LOAD_DEFAULT_RC=false
