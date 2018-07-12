#!/bin/bash

function makeDir(){
    if [ ! -d "$1" ]; then
       mkdir -p "$1"
    fi
} 

function default(){
    if [ -z "$1" ]; then
        __resultvar=$2
    else
        __resultvar=$1
    fi
    eval __resultvar="$__resultvar"
    echo "$__resultvar"
}

home=~
eval home=$home/passdb
echo "If not using defaults for the following paths please use full filepath"
echo "Or relative to home using ~"
read -rp "Directory for certpath (defaults to ~/passdb/certs): " certpath

certpath=$(default "$certpath" $home/certs)
makeDir "$certpath"

read -rp "Directory for keypath (defaults to ~/passdb/keys): " keypath

keypath=$(default "$keypath" $home/keys)
makeDir "$keypath"

read -rp "Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): " cabundle

cabundle=$(default "$cabundle" $home/cabundles/ca.bundle)
makeDir "$(dirname "$cabundle")"
touch "$cabundle"

read -rp "Directory for password store (defaults to ~/passdb/passwords): " pwstore

pwstore=$(default "$pwstore" $home/passwords)
makeDir "$pwstore"

#/dev/null > pkrc
/dev/null .pkpassrc
echo -e "certpath: $certpath 
keypath: $keypath
cabundle: $cabundle
pwstore: $pwstore" >> .pkpassrc

read -rp "Would you like to install the python requirements as root(0),user(1),or venv(2)?" pinstall

case "$pinstall" in
"0")
    sudo python -m pip install -r requirements.txt
    ;;
"1")
    python -m pip install -r requirements.txt --user
    ;;
"2")
    read -rp "What would you like to call the venv? (Default pkpass): " venv
    if [ -z "$venv" ];then
        venv="pkpass"
    fi
    python -m virtualenv "$venv"
    source "$venv"/bin/activate
    pip install -r requirements.txt
    ;;
esac

echo "testing versions of openssl and pkcs15-tool"
echo "if version numbers return you're probably good"
echo "for sanity sake Noah's return values were: "
echo "openssl version: LibreSSL 2.2.7"
echo "pkcs15-tool --version: OpenSC-0.18.0, rev: eb60481f, commit-time: 2018-05-16 13:48:37 +0200"
echo "------YOUR VALUES BELOW THIS LINE -----------"
openssl version
pkcs15-tool --version
