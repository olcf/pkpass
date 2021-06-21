"""This module allows for the population of external password stores"""
from os import path
from ruamel.yaml import YAML
from libpkpass.commands.show import Show
from libpkpass.crypto import puppet_password
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError

    ####################################################################
class Populate(Show):
    """This class implements the CLI functionality of password store integration"""
    ####################################################################
    name = 'populate'
    description = 'Populate external resource with password, currently supports: puppet_eyaml'
    selected_args = ['pwname', 'cabundle', 'card_slot', 'nopassphrase',
                     'certpath', 'color', 'identity', 'keypath',
                     'nocache', 'noverify', 'pwstore', 'quiet',
                     'theme_map', 'type', 'value', 'verbosity']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        # currently only support puppet
        pop_type = self.args['type']
        if pop_type not in ['puppet_eyaml']:
            raise CliArgumentError("'%s' is an unsupported population type" % pop_type)

        if self.args['pwname'] not in self.args['populate'][pop_type]['passwords'].keys():
            raise CliArgumentError("'%s' doesn't have a mapping in %s" % (self.args['pwname'], pop_type))

        password = PasswordEntry()
        myidentity = self.identities.iddb[self.args['identity']]
        plaintext_pw = self._decrypt_wrapper(
            self.args['pwstore'],
            password,
            myidentity,
            self.args['pwname']
        ).strip()
        if pop_type == 'puppet_eyaml':
            self._handle_puppet(plaintext_pw)

        ####################################################################
    def _handle_puppet(self, plaintext_pw):
        ####################################################################
        directory = path.expanduser(self.args['populate']['puppet_eyaml']['directory'])
        if not path.isdir(directory):
            raise CliArgumentError("'%s' is not a directory" % directory)
        puppet_bin = path.expanduser(self.args['populate']['puppet_eyaml']['bin'])
        if not path.isfile(puppet_bin):
            raise CliArgumentError("'%s' is not a file" % puppet_bin)
        pkcs7_pass = puppet_password(puppet_bin, plaintext_pw)
        if self.args['value']:
            print(pkcs7_pass)
        else:
            for hiera_file, names in self.args['populate']['puppet_eyaml']['passwords'][self.args['pwname']].items():
                with open(path.join(directory, hiera_file), 'r') as data_file:
                    print("Updating: %s" % hiera_file)
                    yaml = YAML()
                    yaml.indent(mapping=2, sequence=4, offset=2)
                    yaml.preserve_quotes = True
                    hiera_yaml = yaml.load(data_file.read())
                    for name in names:
                        print("Updating: %s" % name)
                        hiera_yaml[name] = pkcs7_pass
                with open(path.join(directory, hiera_file), 'w') as data_file:
                    yaml.dump(hiera_yaml, data_file)

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['pwname', 'keypath', 'type']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument
                )

        ####################################################################
    def _decrypt_wrapper(self, directory, password, myidentity, pwname):
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        password.read_password_data(path.join(directory, pwname))
        return self._decrypt_password_entry(password, myidentity)

        ####################################################################
    def _decrypt_password_entry(self, password, myidentity):
        """This decrypts a given password entry"""
        ####################################################################
        plaintext_pw = password.decrypt_entry(
            identity=myidentity, passphrase=self.passphrase, card_slot=self.args['card_slot']
        )
        if not self.args['noverify']:
            result = password.verify_entry(
                myidentity['uid'], self.identities
            )
            if not result['sigOK']:
                print("warning: could not verify that '%s' correctly signed your password entry." %
                      result['distributor'])
            if not result['certOK']:
                print("Warning: could not verify the certificate authenticity of user '%s'." %
                      result['distributor'])
        return plaintext_pw
