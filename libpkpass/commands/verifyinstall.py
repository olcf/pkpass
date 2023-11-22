"""This is used to check the os requirements"""
from os import path
from platform import python_version
from re import search
from subprocess import check_output, CalledProcessError
from shutil import which
from libpkpass.commands.command import Command
from libpkpass.errors import BadBackendError
from libpkpass._version import get_versions

class VerifyInstall(Command):
    ####################################################################
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    ####################################################################
    name = "verifyinstall"
    description = "verify required software is present"
    selected_args = Command.selected_args + [
        "pwstore",
        "keypath",
        "noverify",
        "card_slot",
        "connect",
    ]

    def _run_command_execution(self):
        ####################################################################
        """Run function for class."""
        ####################################################################
        yield from print_messages(check_required_software, "installed software check", SCBackend=self.args["SCBackend"])
        yield from print_messages(
            check_passdb,
            "passdb check",
            cabundle=path.realpath(self.args["cabundle"]),
            pwstore=path.realpath(self.args["pwstore"]),
            keypath=path.realpath(self.args["keypath"])
            if self.args["keypath"]
            else None,
            certpath=path.realpath(self.args["certpath"])
            if self.args["certpath"]
            else None,
            connect=self.args["connect"],
        )

    def _validate_args(self):
        pass

def get_backend(SCBackend):
    if SCBackend == "opensc":
        return(SCBackend)
    elif SCBackend == "yubi":
        return(SCBackend)
    raise BadBackendError(SCBackend)



def check_exists(name):
    ####################################################################
    """Check whether a program exists in path"""
    ####################################################################
    path=which(name)
    if path is not None:
        return path

def check_exists_brew(name):
    whichcmd="brew --prefix --installed "+ name + " 2> /dev/null"
    try:
        path=check_output(whichcmd, shell=True).decode('utf-8').strip()
        #print(path)
    except CalledProcessError:
        path=None
    return path 

def print_messages(func, msg, **kwargs):
    yield f"Starting {msg}"
    yield func(**kwargs)

def check_brew():
    if which("brew"):
        return True
    else:
        return False
    #may need an exception here to catch which not existing

def check_required_software(**kwargs):
    print("Using Python Version "+python_version())
    print("Using Pkpass Version: "+get_versions()["version"])
    SCBackend=get_backend(kwargs['SCBackend'])
    print("Using SCBackend: "+SCBackend)
    if SCBackend=="yubi":
        required_tools = {
            "ssl (openssl or libressl)": ["openssl", "libressl"],
            "yubico-piv-tool": ["yubico-piv-tool", "libp11"],
        }
    elif SCBackend=="opensc":
        required_tools = {
            "pkcs15-tool (available via opensc)": ["pkcs15-tool", "opensc"],
            "ssl (openssl or libressl)": ["openssl", "libressl"],
        }
    not_found = []
    found = []
    paths = []
    brew=check_brew()
    for key, value in required_tools.items():
        found_tool = False
        for tool in value:
            if brew:
                brewexists=check_exists_brew(tool)
                if brewexists:
                    found.append(tool)
                    found_tool = True
                    print(tool+" is installed with brew")
                    paths.append(brewexists)
            else:
                exists=check_exists(tool)
                if exists:
                    found.append(tool)
                    found_tool = True
                    print(tool+" is installed")
                    paths.append(exists)
        if not found_tool:
            not_found.append(key)
    matches = dict(zip(found,paths))
    if not_found:
        return "The following packages were not found: \n\t%s" % "\n\t".join(not_found)
    if brew and SCBackend=="yubi":
        check_links(matches)
    return "Successful installed software check"

def check_links(software):
    software['local']="/usr/local"
    for package,path in software.items():
        pathlib=path+"/lib"
        needspkcs=["openssl","libp11","local"]
        needslibykcs=["yubico-piv-tool","local"]
        checkdir=check_output(["ls","-l",pathlib]).decode('utf-8').strip()
        if search("engines-3", checkdir):
            if search("pkcs11.dylib", check_output(["ls","-l",pathlib+"/engines-3"]).decode('utf-8').strip()):
                print("pkcs11.dylib exists in "+pathlib+"/engines-3")
            elif package in needspkcs:
                print("Required packages are installed, however no file was detected at "+pathlib+"/engines-3/pkcs11.dylib . A link may be needed.")
        if search("libykcs11.dylib", checkdir):
            print("libykcs11.dylib exists in "+pathlib)
        elif package in needslibykcs:
            print("Required packages are installed, however no file was detected at "+pathlib+"libykcs11.dylib . A link may be needed.")



def check_passdb(cabundle, pwstore, certpath=None, keypath=None, connect=None):
    ret_msg = []
    if not path.isfile(cabundle):
        ret_msg.append("Cabundle is not a file")
    if not path.isdir(pwstore):
        ret_msg.append("pwstore is not a directory")
    if connect and certpath:
        ret_msg.append("certpath or keypath is defined while using a connector")
    if certpath and not path.isdir(certpath):
        ret_msg.append(f"certpath is not a directory {certpath}")
    if keypath and not path.isdir(keypath):
        ret_msg.append(f"Keypath is not a directory: {keypath}")
    ret_msg.append("Completed passdb check")
    return "\n".join(ret_msg)
