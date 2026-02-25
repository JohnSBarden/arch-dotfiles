set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" git scripts
Plugin 'tpope/vim-fugitive'

" fzf file finding etc
Plugin 'ctrlpvim/ctrlp.vim'

" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}

" syntax highlighters 
Plugin 'pangloss/vim-javascript'
Plugin 'mxw/vim-jsx'
Plugin 'leshill/vim-json'

" re-eval
" Plugin 'othree/html5-vim'

Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
" let g:airline_theme = 'catppuccin_mocha'
let g:airline_theme = 'everforest'

" linting
Plugin 'w0rp/ale'

" editorconfig
Plugin 'editorconfig/editorconfig-vim'

" themes
" Plugin 'morhetz/gruvbox'
Plugin 'arcticicestudio/nord-vim'
Plugin 'sainnhe/sonokai'
Plugin 'catppuccin/nvim'

" emmet completion
Plugin 'mattn/emmet-vim'

" easy commenting
Plugin 'tomtom/tcomment_vim'

Plugin 'tpope/vim-surround'

Plugin 'vimwiki/vimwiki'
Plugin 'dhruvasagar/vim-table-mode'
Plugin 'jkramer/vim-checkbox'

Plugin 'FooSoft/vim-argwrap'

Plugin 'scrooloose/nerdtree'
Plugin 'Xuyuanp/nerdtree-git-plugin'

Plugin 'machakann/vim-highlightedyank'
Plugin 'airblade/vim-gitgutter'

" TODO - Set up LSP and vim
" Plugin 'autozimu/LanguageClient-neovim'

" (Optional) Multi-entry selection UI.
" Plugin 'junegunn/fzf'

" Plugin 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }


" Ghost text
"
" disabled, py3 problem
"Plugin 'raghur/vim-ghost', {'do': ':GhostInstall'}

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

" set background=dark

" NOTE: These all break if you disable Gruvbox "
"
" nnoremap <silent> [oh :call gruvbox#hls_show()<CR>
" nnoremap <silent> ]oh :call gruvbox#hls_hide()<CR>
" nnoremap <silent> coh :call gruvbox#hls_toggle()<CR>

" nnoremap * :let @/ = ""<CR>:call gruvbox#hls_show()<CR>*
" nnoremap / :let @/ = ""<CR>:call gruvbox#hls_show()<CR>/
" nnoremap ? :let @/ = ""<CR>:call gruvbox#hls_show()<CR>?
" \NOTE "

" enable syntax highlighting
syntax enable

set expandtab
set tabstop=2
set shiftwidth=2
set softtabstop=2
set expandtab
set autoindent

if (has("termguicolors"))
  set termguicolors
endif

" enable line numbers
set number
set relativenumber

autocmd FileType markdown setlocal shiftwidth=4 softtabstop=4 tabstop=4 wrap linebreak nolist wrap lbr colorcolumn=0 synmaxcol=999999

set laststatus=2

set splitbelow
set splitright

" remap split navigation so we can move splits with just CTRL+HJKL instead of
" CTRL+W HJKL
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

" unbind arrow keys so that we are forced to use homerow navigation
"noremap <Up> <NOP>
"noremap <Down> <NOP>
"noremap <Left> <NOP>
"noremap <Right> <NOP>

" editor config plays nicely with fugitive
let g:EditorConfig_exclude_patterns = ['fugitive://.*']

let g:ale_fixers = {
\   'javascript': [
\       'eslint', 'prettier',
\   ],
\}

let g:ale_fix_on_save = 1
let g:ale_sign_column_always = 1
" airline status for ale
let g:airline#extensions#ale#enabled = 1
let g:ale_completion_enabled = 1

" argwrap bind
nnoremap <silent> <leader>a :ArgWrap<CR>
nnoremap <silent> <leader>f :ALEFix<CR>
nnoremap <silent> <leader>w :ALELint<CR>

" start nerdtree if no input file
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif

" nerd tree open
map <C-n> :NERDTreeToggle<CR>

autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" vimiwiki config / overrides
let g:vimwiki_list = [{'syntax': 'markdown', 'ext': '.md'}]

" emmet config
let g:user_emmet_leader_key='<Tab>'
let g:user_emmet_settings = {
  \  'javascript.jsx' : {
    \      'extends' : 'jsx',
    \  },
  \}

" TODO :: LSP config - none of this is working currently
" LSP client config
set hidden

let g:LanguageClient_serverCommands = {
    \ 'rust': ['rustup', 'run', 'nightly', 'rls'],
    \ 'javascript': ['javascript-typescript-stdio'],
    \ 'javascript.jsx': ['tcp://127.0.0.1:2089'],
    \ }

nnoremap <F5> :call LanguageClient_contextMenu()<CR>
" Or map each action separately
nnoremap <silent> K :call LanguageClient#textDocument_hover()<CR>
nnoremap <silent> gd :call LanguageClient#textDocument_definition()<CR>
nnoremap <silent> <F2> :call LanguageClient#textDocument_rename()<CR>

" quicksave
noremap <Leader>s :update<CR>

" quick edit vimrc
nnoremap <leader>ev :vsplit $HOME/.vimrc<cr>

" source vimrc
nnoremap <leader>sv :source $HOME/.vimrc<cr>

if has('termguicolors')
    set termguicolors
endif

let g:ctrlp_custom_ignore = 'node_modules\|DS_Store\|git'


" color scheme shit
let g:sonokai_style = 'maia'
" let g:everforest_background = 'hard'

" set colorscheme
" colorscheme nord
" colorscheme sonokai
" colorscheme catppuccin
colorscheme everforest

hi Normal guibg=NONE ctermbg=NONE


" Vim native package system?"
packadd! everforest
