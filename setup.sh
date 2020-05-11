#!/bin/bash
# Dummy helper script to do local install

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
else
    echo "Python3 venv package not available"
fi
