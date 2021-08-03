"""This module allows for the population of external password stores"""
from os import path, remove
from base64 import standard_b64encode
from ruamel.yaml import YAML
from yaml import dump
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
                     'all', 'certpath', 'color', 'identity', 'keypath',
                     'nocache', 'noverify', 'pwstore', 'quiet',
                     'theme_map', 'type', 'value', 'verbosity']

        ####################################################################
    def _run_command_execution(self):
        """ Run function for class.                                      """
        ####################################################################
        # currently only support puppet
        pop_type = self.args['type']
        if pop_type not in ['puppet_eyaml', 'kubernetes']:
            raise CliArgumentError("'%s' is an unsupported population type" % pop_type)

        myidentity = self.identities.iddb[self.args['identity']]
        if self.args['all']:
            for password in self.args['populate'][pop_type]['passwords'].keys():
                pwentry = PasswordEntry()
                self._decrypt_wrapper(
                    self.args['pwstore'],
                    pwentry,
                    myidentity,
                    password,
                    pop_type
                )

        elif self.args['pwname'] not in self.args['populate'][pop_type]['passwords'].keys():
            raise CliArgumentError("'%s' doesn't have a mapping in %s" % (self.args['pwname'], pop_type))
        else:
            password = PasswordEntry()
            self._decrypt_wrapper(
                self.args['pwstore'],
                password,
                myidentity,
                self.args['pwname'],
                pop_type
            )

        ####################################################################
    def _handle_kubernetes(self, plaintext_pw, pwname):
        """This function creates a file containing kube secrets"""
        ####################################################################
        k_conf = self.args['populate']['kubernetes']
        password = k_conf['passwords'][pwname]
        if 'output' in k_conf:
            if self.args['pwstore'] in k_conf['output']:
                raise CliArgumentError("Kubernetes output file should not exist in password store")
            if path.isfile(k_conf['output']):
                remove(k_conf['output'])
        for args in password:
            data = {}
            for key, value in args['data'].items():
                if value == pwname:
                    data[key] = standard_b64encode(plaintext_pw.encode('ASCII')).decode()
                else:
                    data[key] = standard_b64encode(value.encode('ASCII')).decode()
            kube_map = {
                'kind': 'Secret',
                'apiVersion': args['apiVersion'],
                'metadata': args['metadata'],
                'data': data,
                'type': args['type']
            }
            if self.args['value'] or 'output' not in k_conf:
                print("%s\n%s" % ("---", dump(kube_map)))
            else:
                with open(k_conf['output'], 'a') as fname:
                    print("%s\n%s" % ("---", dump(kube_map)), file=fname)


        ####################################################################
    def _handle_puppet(self, plaintext_pw, pwname):
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
            for hiera_file, names in self.args['populate']['puppet_eyaml']['passwords'][pwname].items():
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
        for argument in ['keypath', 'type']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(
                    "'%s' is a required argument" % argument
                )

        ####################################################################
    def _decrypt_wrapper(self, directory, password, myidentity, pwname, pop_type):
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        password.read_password_data(path.join(directory, pwname))
        plaintext_pw = self._decrypt_password_entry(password, myidentity)
        if pop_type == 'puppet_eyaml':
            self._handle_puppet(plaintext_pw, pwname)
        elif pop_type == 'kubernetes':
            self._handle_kubernetes(plaintext_pw, pwname)

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
