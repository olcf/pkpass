#!/bin/bash

#useful in aborting the pyinstall function 
function invalid(){
    echo "Invalid selection, exiting setup program"
    exit 1
}

#user and groups lists should not have empty values, this removes any trailing whitespace as well as 
#trailing commas mixed in. 
#it will not remove blanks in between though
#arg1 is list of csvs
function csv(){
    csv="$(echo "$1" | tr -d '[:space:]')"
    while [[ $csv =~ (^,.*) || $csv =~ (.*,$) ]]; do
        csv="$(echo "$csv" | sed 's/,$//g' | sed 's/^,//g' | tr -d '[:space:]' )"
    done
    echo "$csv"
}

#handle yes or no user input in pyinstall to make virtualenv installation nicer
#arg1 is prompt
#arg2 is default
function decision(){
    while [[ -z "$chosen" ]]; do
        read -rp "$1" choice
        if [[ -z "$2" ]]; then
            case "$choice" in
                y|Y|yes|Yes|YES ) echo "y" && chosen="true";;
                n|N|no|No|NO ) echo "n" && chosen="true" ;;
                * ) ;;
            esac
        else
            chosen="true"
            choice="${choice:-"$2"}"
            echo "$choice"
        fi
    done
}

#This function installs python dependencies as either root, user level or in a virtualenv
function pyinstall(){
    #method can be root(0), user(1), or virtualenv(2)
    method=$1
    local package=$2
    IFS=' ' 

    read -r -a package <<< "${package[@]}"
    if [[ "$method" == "2" ]]; then
        python -c "import virtualenv" 2>/dev/null

        if [[ "$?" == "1" ]]; then
            installenv="$(decision "virtualenv package not detected would you like to install it? (y/n): ")"

            if [[ "$installenv" == "y" ]]; then
                read -rp "Would you like to install virtualenv as root(0) or user(1)?" vinstall
                pyinstall "$vinstall" "virtualenv"
            elif [[ "$installenv" == "n" ]]; then
                read -rp "how would you like to install the python requirements instead? root(0)/user(1): " preq
                pyinstall "$preq" "${package[@]}"
                return 0
            else
                #This is here in case something weird happens
                invalid
            fi
        fi 

        read -rp "What would you like to call the virtualenv? (Default venv): " venv
        venv="${venv:-"venv"}"

        python -m virtualenv "$venv"
        source "$venv"/bin/activate
        pip install "${package[@]}"

    elif [[ "$method" == "0" ]]; then
        sudo python -m pip install -r requirements.txt
    elif [[ "$method" == "1" ]]; then
        python -m pip install -r requirements.txt --user
    else
        invalid
    fi
}

#we saw a weird path issue during dev, storing now to ensure not modified
OLD_PATH=$PATH

#check if pip exists on the system as it is necessary for setup
python -c "import pip" 2>/dev/null
if [[ "$?" == "1" ]]; then
    echo "python package pip not found, it is required for installation, please install and re-run setup.sh"
    exit 1
fi

#define a home default for passdb
if [ -z ${PREFIX+x} ]; then
    read -rp "PKPass home (defaults to ${HOME}/passdb): " home
    home="${home:-${HOME}/passdb}"
    home="${home/#\~/$HOME}"
else
    home="${PREFIX/#\~/$HOME}"
fi

home=$(sed 's:/*$::' <<< "$home")
rcfile="$HOME/.pkpassrc"
#check for a .pkpassrc file and ask user if they want to overwrite or skip to pyinstall
#This is useful in the event that an error occurred during last setup
skip="n"
if [[ -f "$rcfile" ]]; then
    echo -e ".pkpassrc file detected, you may either overwrite this .pkpassrc file and 
    use the script as normal; or skip setup on the pkpassrc file and continue to 
    the python depedencies"
    skip="$(decision "Would you like to skip the .pkpassrc file setup(defaults n) (y/n): " n)"
fi 

#if skip is no setup .pkpassrc file
if [[ "$skip" == "n" ]]; then
    echo -e "If not using defaults for the following paths please use full filepath
    Or relative to home using ~"

    #Cert path definition
    read -rp "Directory for certpath (defaults to ~/passdb/certs): " certpath

    certpath="${certpath:-${home}/certs}"
    certpath="${certpath/#\~/$HOME}" 
    mkdir -p "${certpath}"

    #Key path definition
    read -rp "Directory for keypath (defaults to ~/passdb/keys): " keypath

    keypath="${keypath:-${home}/keys}"
    keypath="${keypath/#\~/$HOME}"
    mkdir -p "${keypath}"

    #cabundle path definition
    read -rp "Path to cabundle (defaults to ~/passdb/cabundles/ca.bundle): " cabundle

    cabundle="${cabundle:-${home}/cabundles/ca.bundle}"
    cabundle="${cabundle/#\~/$HOME}"
    mkdir -p "$(dirname "${cabundle}")"
    touch "${cabundle}"

    #passwords path definition
    read -rp "Directory for password store (defaults to ~/passdb/passwords): " pwstore

    pwstore="${pwstore:-${home}/passwords}"
    pwstore="${pwstore/#\~/$HOME}"
    mkdir -p "${pwstore}"


    #list available card slots for the user
    pkcs11-tool -L

    read -rp "Available slots listed above, which would you like to use? (defaults to 0): " cardslot
    cardslot="${cardslot:-0}"

    read -rp "What user name would you like to use? (defaults to system user): " identity
    identity="${identity:-$(whoami)}"

    echo -e "Escrow users is a feature of Pkpass. Escrow allows a password to be recovered by
    the majority of the escrow users in the event of an emergency."

    escrow="$(decision "Would you like to setup a group of default escrow users?(y/n)" n)"

    if [[ "$escrow" == "y" ]]; then

        read -rp "Please enter a comma seperated list of usernames: " escrowusers
        escrowusers="$(csv "$escrowusers")"
        count="$(echo "$escrowusers" | sed 's/[^,]//g' | wc -c)"

        echo -e "By Default we require 1 less user than is total in the group to unlock an escrow
        password, your list was $count total users"
        count=$((count-1))

        read -rp "What should be the minimum number of users to unlock escrow passwords? Default($count): " minescrow
        minescrow="${minescrow:-$count}"
    fi

    #overwrite a file .pkpassrc with defined values here
    echo -e "certpath: $certpath 
keypath: $keypath
cabundle: $cabundle
pwstore: $pwstore
card_slot: $cardslot
identity: $identity
escrow_users: $escrowusers
min_escrow: $minescrow" > "$rcfile"

fi

read -rp "Would you like to install the python requirements as root(0),user(1),or venv(2)?" pinstall
#call pyinstall as defined above
pyinstall "$pinstall" '-r requirements.txt'

echo -e "testing versions of openssl and pkcs15-tool
if version numbers return you're probably good
for sanity sake Noah's return values were: 
openssl version: LibreSSL 2.2.7
pkcs15-tool --version: OpenSC-0.18.0, rev: eb60481f, commit-time: 2018-05-16 13:48:37 +0200
------YOUR VALUES BELOW THIS LINE -----------"

openssl version
pkcs15-tool --version

#guess if pyinstall worked properly and if the guess is that it did
#inform user how to activate that virtualenv
if [[ "$pinstall" == "2" ]]; then
    venv="$(find . -mindepth 1 -maxdepth 1 -type d -printf '%T+ %p\n' | sort -r | grep -v git | head -1 | cut -d ' ' -f 2)"
    echo "The following is a guess:"
    echo "you may have installed with a virtual environment if so use"
    echo source "$venv"/bin/activate
fi

#reassign path to ensure nothing strange happened
PATH=$OLD_PATH
