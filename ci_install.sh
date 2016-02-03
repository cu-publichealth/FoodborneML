# installation script for travis ci

# leave the virtualenv and create a new one with the system packages cached on apt-get
#sudo apt-get install libblas-dev liblapack-dev libatlas-dev gfortran libatlas3gf-base python-numpy python-scipy
deactivate
virtualenv --system-site-packages testvenv
source testvenv/bin/activate

# now install the requirements from pip
pip install -r travis_requirements.txt