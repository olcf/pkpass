"""This Module allows for the listing of recipients"""
from libpkpass import LOGGER
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
        LOGGER.info('Certificate store: %s', self.args["certpath"])
        LOGGER.info('Key store: %s', self.args["keypath"])
        LOGGER.info('CA Bundle file: %s', self.args["cabundle"])
        LOGGER.info('Looking for Key Extension: %s', self.identities.extensions["key"])
        LOGGER.info('Looking for Certificate Extension: %s', self.identities.extensions["certificate"])
        LOGGER.info("Loaded %s identities", len(self.session.query(Recipient).all()))

        if 'filter' in self.args and self.args['filter']:
            identities = self.session.query(Recipient).filter(
                Recipient.name.like(self.args['filter'].replace('*', '%'))
            )
        else:
            identities = self.session.query(Recipient).all()
        for identity in identities:
            yield self._print_identity(
                identity,
                self.session.query(Cert).filter(
                    Cert.recipients.contains(identity)
                ).all()
            )

        ####################################################################
    def _print_identity(self, identity, certs):
        """Print off identity"""
        ####################################################################
        identity_list = []
        identity_list.append(f"{self.color_print(identity.name, 'first_level')}:")
        identity_list.append(f"\t{self.color_print('certs', 'second_level')}:")
        for cert in certs:
            for info in ['verified', 'subject', 'subjecthash', 'issuer', 'issuerhash', 'fingerprint', 'enddate']:
                identity_list.append(f"\t\t{self.color_print(info + ':', 'third_level')} {dict(cert)[info]}")
            identity_list.append('\n')
        return "\n".join(identity_list)

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
