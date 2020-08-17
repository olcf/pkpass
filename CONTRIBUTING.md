# Pull Request Process
1. ensure pylint is installed to verify you are coding to our standards as shown in the pylintrc file
2. run the unittests before commit (use tox to ensure python 2 and 3 compatibility)
3. create new unittests as necessary
4. update the README if applicable
5. update the setup script if applicable

# Setting up a development environment
1. After checking out this repository, create a python3 environment (in ./venv) with `python3 venv venv`
2. Install all pkpass prerequisites into that virtual environment by running `pip install -r requirements.txt`
3. You should be able to run the latest checked out pkpass with `./venv/bin/python pkpass`
