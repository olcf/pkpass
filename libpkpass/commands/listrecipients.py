"""This Module allows for the listing of recipients"""
from sqlalchemy.orm import sessionmaker
from libpkpass.commands.command import Command
from libpkpass.errors import CliArgumentError
from libpkpass.models.cert import Cert
from libpkpass.models.recipient import Recipient

    ####################################################################
class Listrecipients(Command):
    """This class implements the cli functionality to list recipients"""
    ####################################################################
    name = 'listrecipients'
    description = 'List the recipients that pkpass knows about'
    selected_args = Command.selected_args + ['stdin', 'filter']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                  """
        ####################################################################
        session = sessionmaker(bind=self.args['db']['engine'])()
        if self.args['verbosity'] != -1:
            print(f'Certificate store: "{self.args["certpath"]}"')
            print(f'Key store: "{self.args["keypath"]}"')
            print(f'CA Bundle file: "{self.args["cabundle"]}"')
            print(f'Looking for Key Extension: "{self.identities.extensions["key"]}"')
            print(f'Looking for Certificate Extension: "{self.identities.extensions["certificate"]}"')
            print(f"Loaded {len(session.query(Recipient).all())} identities:\n")

        if 'filter' in self.args and self.args['filter']:
            identities = session.query(Recipient).filter(
                Recipient.name.like(self.args['filter'].replace('*', '%'))
            )
        else:
            identities = session.query(Recipient).all()
        for identity in identities:
            self._print_identity(
                identity,
                session.query(Cert).filter(
                    Cert.recipients.contains(identity)
                ).all()
            )

        ####################################################################
    def _print_identity(self, identity, certs):
        """Print off identity"""
        ####################################################################
        print(f"{self.color_print(identity.name, 'first_level')}:")
        print(f"\t{self.color_print('certs', 'second_level')}:")
        for cert in certs:
            for info in ['verified', 'subject', 'subjecthash', 'issuer', 'issuerhash', 'fingerprint', 'enddate']:
                print(f"\t\t{self.color_print(info + ':', 'third_level')} {dict(cert)[info]}")
            print()

        ####################################################################
    def _validate_args(self):
        """ Ensure arguments are appropriate for this command       """
        ####################################################################
        for argument in ['keypath']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

        ####################################################################
    def _validate_identities(self, _=None):
        """ Ensure identities are appropriate for this command       """
        ####################################################################
        return
