"""This is used to check the os requirements"""
from os import path
from shutil import which
from libpkpass.commands.command import Command

    ####################################################################
class VerifyInstall(Command):
    """This class is used as a command object and parses information passed through
    the CLI to show passwords that have been distributed to users"""
    ####################################################################
    name = 'verifyinstall'
    description = 'verify required software is present'
    selected_args = Command.selected_args + ['pwstore', 'keypath', 'noverify', 'card_slot',
                                             'connect']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                  """
        ####################################################################
        yield from print_messages(check_required_software, "installed software check")
        yield from print_messages(check_passdb, "passdb check",
                       cabundle=path.realpath(self.args['cabundle']),
                       pwstore=path.realpath(self.args['pwstore']),
                       keypath=path.realpath(self.args['keypath']) if self.args['keypath'] else None,
                       certpath=path.realpath(self.args['certpath']) if self.args['certpath'] else None,
                       connect=self.args['connect'])

        ####################################################################
    def _validate_args(self):
        ####################################################################
        pass

    ####################################################################
def check_exists(name):
    """ Check whether a program exists in path"""
    ####################################################################
    return which(name) is not None

    ####################################################################
def print_messages(func, msg, **kwargs):
    ####################################################################
    yield f"Starting {msg}"
    yield func(**kwargs)

    ####################################################################
def check_required_software():
    ####################################################################
    required_tools = {
        'pkcs15-tool (available via opensc)': ['pkcs15-tool'],
        'ssl (openssl or libressl)': ['openssl', 'libressl']
    }
    not_found = []
    for key, value in required_tools.items():
        found_tool = False
        for tool in value:
            if check_exists(tool):
                found_tool = True
        if not found_tool:
            not_found.append(key)
    if not_found:
        return "The following packages were not found: \n\t%s" % "\n\t".join(not_found)
    return "Successful installed software check"

    ####################################################################
def check_passdb(cabundle, pwstore, certpath=None, keypath=None, connect=None):
    ####################################################################
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
