#!/bin/bash

function default(){
    if [ -z "$1" ]; then
        __resultvar=$2
    else
        __resultvar=$1
    fi
    eval __resultvar="$__resultvar"
    echo "$__resultvar"
}

function invalid(){
    echo "Invalid selection, exiting setup program"
    exit 1
}

function pyinstall(){
    #method can be root(0), user(1), or virtualenv(2)
    method=$1
    local package=$2

    IFS=' ' 
    read -r -a package <<< "${package[@]}"

    if [[ "$method" == "2" ]]; then
        python -c "import virtualenv" 2>/dev/null
        if [[ "$?" == "1" ]]; then
            read -rp "virtualenv package not detected would you like to install it? (y/n): " installenv
            installenv="$(echo "$installenv" | tr '[:upper:]' '[:lower:]')"

            if [[ "$installenv" == "y" ]]; then
                read -rp "Would you like to install virtualenv as root(0) or user(1)?" vinstall
                pyinstall "$vinstall" "virtualenv"
            elif [[ "$installenv" == "n" ]]; then
                read -rp "how would you like to install the python requirements instead? root(0)/user(1): " preq
                pyinstall "$preq" "${package[@]}"
                return 0
            else
                invalid
            fi
        fi 
        read -rp "What would you like to call the virtualenv? (Default pkpass): " venv
        if [ -z "${venv}" ]; then
            venv="pkpass"
        fi
        python -m virtualenv "$venv"
        source "$venv"/bin/activate
        pip install "${package[@]}"
        
    elif [[ "$method" == "0" ]]; then
        sudo python -m pip install "${package[@]}"
    elif [[ "$method" == "1" ]]; then
        python -m pip install "${package[@]}" --user
    else
        invalid
    fi
}
OLD_PATH=$PATH
python -c "import pip" 2>/dev/null
if [[ "$?" == "1" ]]; then
    echo "python package pip not found, it is required for installation, please install and re-run setup.sh"
    exit 1
fi
home="$HOME"/passdb
echo "If not using defaults for the following paths please use full filepath"
echo "Or relative to home using ~"
read -rp "Directory for certpath (defaults to ~/passdb/certs): " certpath

certpath="${certpath:-${home}/certs}"
certpath="${certpath/#\~/$HOME}" 
mkdir -p "${certpath}"

read -rp "Directory for keypath (defaults to ~/passdb/keys): " keypath

keypath="${keypath:-${home}/keys}"
keypath="${keypath/#\~/$HOME}"
mkdir -p "${keypath}"

read -rp "Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): " cabundle

cabundle="${cabundle:-${home}/cabundles/ca.bundle}"
cabundle="${cabundle/#\~/$HOME}"
mkdir -p "$(dirname "${cabundle}")"
touch "${cabundle}"

read -rp "Directory for password store (defaults to ~/passdb/passwords): " pwstore

pwstore="${pwstore:-${home}/passwords}"
pwstore="${pwstore/#\~/$HOME}"
mkdir -p "${pwstore}"

pkcs11-tool -L

read -rp "Available slots listed above, which would you like to use? (defaults to 0): " cardslot
cardslot="${cardslot:-0}"

echo -e "certpath: $certpath 
keypath: $keypath
cabundle: $cabundle
pwstore: $pwstore
default_card: $cardslot" > .pkpassrc
 
read -rp "Would you like to install the python requirements as root(0),user(1),or venv(2)?" pinstall

pyinstall "$pinstall" '-r requirements.txt'

echo "testing versions of openssl and pkcs15-tool"
echo "if version numbers return you're probably good"
echo "for sanity sake Noah's return values were: "
echo "openssl version: LibreSSL 2.2.7"
echo "pkcs15-tool --version: OpenSC-0.18.0, rev: eb60481f, commit-time: 2018-05-16 13:48:37 +0200"
echo "------YOUR VALUES BELOW THIS LINE -----------"
openssl version
pkcs15-tool --version

if [[ "$pinstall" == "2" ]]; then
    venv="$(find .. -maxdepth 1 -mindepth 1 -type d -cmin -1 -not -path '*/\.*' | cut -c 4-)"
    echo "you may have installed with a virtual environment if so use"
    echo source "$venv"/bin/activate
fi
PATH=$OLD_PATH
