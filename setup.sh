#!/bin/bash

function print_seperator(){
    echo "**************************************************"
    echo "**************************************************"
    echo "**************************************************"
    echo "**************************************************"
    echo "$1"
    echo "**************************************************"
    echo "**************************************************"
    echo "**************************************************"
    echo "**************************************************"
}
if [[ -d "./venv" ]]; then
    print_seperator "Removing previous venv exists"
    rm -rf ./venv
fi

print_seperator "Creating python3 virtualenv"
python3 -m venv venv
py3="./venv/bin/python3"
if [[ -f $py3 ]]; then
    print_seperator "Running Python Installation"
    $py3 setup.py install
    print_seperator "Starting RC File Generation"
    $py3 setup.py rcfile
    print_seperator "Running RC File verification"
    $py3 setup.py verify
else
    echo "Python3 venv package not available"
fi
