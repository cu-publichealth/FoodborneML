# installation script for travis ci

# leave the virtualenv and create a new one with the system packages cached on apt-get
deactivate
virtualenv --system-site-packages
source testvenv/bin/activate

# now install the requirements from pip
pip install -r deploy_requirements.txt