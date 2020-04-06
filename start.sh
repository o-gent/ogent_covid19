# script for starting the python file with the correct environment while root
export PATH="$HOME/.pyenv/bin:$PATH"
sudo env "PATH=$PATH VIRTUAL_ENV=$VIRTUAL_ENV" python ./start.py 