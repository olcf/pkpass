"""This module handles the CLI for password recovery"""
from libpkpass.escrow import pk_recover_secret
from libpkpass.commands.command import Command

    ####################################################################
class Recover(Command):
    """This class implements the CLI functionality of recovery for passwords"""
    ####################################################################
    name = 'recover'
    description = 'Recover a password that has been distributed using escrow functions'
    selected_args = Command.selected_args + ['pwstore', 'keypath', 'nosign', 'escrow_users', 'min_escrow']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        yield "If the password returned is not correct, you may need more shares"
        shares = input("Enter comma separated list of shares: ")
        shares = shares.split(",")
        shares = map(str.strip, shares)
        yield pk_recover_secret(shares)

        ####################################################################
    def _validate_args(self):
        ####################################################################
        pass

        ####################################################################
    def _validate_combinatorial_args(self):
        ####################################################################
        pass
