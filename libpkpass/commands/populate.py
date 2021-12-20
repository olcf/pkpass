"""This module allows for the population of external password stores"""
from os import path, remove
from re import finditer
from base64 import standard_b64encode
from ruamel.yaml import YAML
from yaml import dump
from libpkpass import LOGGER
from libpkpass.commands.show import Show
from libpkpass.crypto import puppet_password
from libpkpass.password import PasswordEntry
from libpkpass.errors import CliArgumentError
from libpkpass.models.recipient import Recipient

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
            raise CliArgumentError(f"'{pop_type}' is an unsupported population type")

        if pop_type == 'kubernetes':
            yield from self._handle_kubernetes()
        elif self.args['all']:
            for password in self.args['populate'][pop_type]['passwords'].keys():
                pwentry = PasswordEntry()
                self._decrypt_wrapper(
                    self.args['pwstore'],
                    pwentry,
                    password,
                    pop_type
                )

        elif self.args['pwname'] not in self.args['populate'][pop_type]['passwords'].keys():
            raise CliArgumentError(f"'{self.args['pwname']}' doesn't have a mapping in {pop_type}")
        else:
            password = PasswordEntry()
            yield from self._decrypt_wrapper(
                self.args['pwstore'],
                password,
                self.args['pwname'],
                pop_type
            )

        ####################################################################
    def _handle_kubernetes(self):
        """This function creates a file containing kube secrets"""
        ####################################################################
        k_conf = self.args['populate']['kubernetes']
        plaintext = {}
        for password in k_conf['needed']:
            pwentry = PasswordEntry()
            pwentry.read_password_data(path.join(self.args['pwstore'], password))
            plaintext_pw = self._decrypt_password_entry(pwentry)
            plaintext[password] = plaintext_pw
        if 'output' in k_conf:
            if self.args['pwstore'] in k_conf['output']:
                raise CliArgumentError("Kubernetes output file should not exist in password store")
            if path.isfile(k_conf['output']):
                remove(k_conf['output'])
        for args in k_conf['passwords']:
            data = self._kubernetes_match_loop(args, plaintext)
            kube_map = {
                'kind': 'Secret',
                'apiVersion': args['apiVersion'],
                'metadata': args['metadata'],
                'data': data,
                'type': args['type']
            }
            if self.args['value'] or 'output' not in k_conf:
                yield f"---\n{dump(kube_map)}"
            else:
                with open(k_conf['output'], 'a', encoding='ASCII') as fname:
                    print(f"---\n{dump(kube_map)}", file=fname)

        ####################################################################
    def _kubernetes_match_loop(self, args, plaintext):
        """This matches ${example} inside the arg defs and generates a
        dictionary of b64 encoded values with the actual password values
        placed instead of ${}"""
        ####################################################################
        data = {}
        for key, value in args['data'].items():
            new_pw = str(value)
            match_iter = finditer(r'\$\{([^${]*)\}', new_pw)
            if not match_iter:
                data[key] = standard_b64encode(new_pw.encode('ASCII')).decode()
            else:
                for match_values in match_iter:
                    match_value = match_values.group(1)
                    new_pw = new_pw.replace(f"%{{{match_value}}}", plaintext[match_value])
                data[key] = standard_b64encode("".join(new_pw).encode('ASCII')).decode()
        return data

        ####################################################################
    def _handle_puppet(self, plaintext_pw, pwname):
        ####################################################################
        directory = path.expanduser(self.args['populate']['puppet_eyaml']['directory'])
        if not path.isdir(directory):
            raise CliArgumentError(f"'{directory}' is not a directory")
        puppet_bin = path.expanduser(self.args['populate']['puppet_eyaml']['bin'])
        if not path.isfile(puppet_bin):
            raise CliArgumentError(f"'{puppet_bin}' is not a file")
        pkcs7_pass = puppet_password(puppet_bin, plaintext_pw)
        if self.args['value']:
            yield pkcs7_pass
        else:
            for hiera_file, names in self.args['populate']['puppet_eyaml']['passwords'][pwname].items():
                with open(path.join(directory, hiera_file), 'r', encoding='ASCII') as data_file:
                    yield f"Updating: {hiera_file}"
                    yaml = YAML()
                    yaml.indent(mapping=2, sequence=4, offset=2)
                    yaml.preserve_quotes = True
                    hiera_yaml = yaml.load(data_file.read())
                    for name in names:
                        yield f"Updating: {name}"
                        hiera_yaml[name] = pkcs7_pass
                with open(path.join(directory, hiera_file), 'w', encoding='ASCII') as data_file:
                    yaml.dump(hiera_yaml, data_file)

        ####################################################################
    def _validate_args(self):
        ####################################################################
        for argument in ['keypath', 'type']:
            if argument not in self.args or self.args[argument] is None:
                raise CliArgumentError(f"'{argument}' is a required argument")

        ####################################################################
    def _decrypt_wrapper(self, directory, password, pwname, pop_type):
        """Decide whether to decrypt normally or for escrow"""
        ####################################################################
        password.read_password_data(path.join(directory, pwname))
        plaintext_pw = self._decrypt_password_entry(password)
        if pop_type == 'puppet_eyaml':
            yield from self._handle_puppet(plaintext_pw, pwname)

        ####################################################################
    def _decrypt_password_entry(self, password):
        """This decrypts a given password entry"""
        ####################################################################
        plaintext_pw = password.decrypt_entry(
            identity=self.identity, passphrase=self.passphrase, card_slot=self.args['card_slot']
        )
        distributor = password.recipients[self.identity['name']]['distributor']
        if not self.args['noverify']:
            result = password.verify_entry(
                self.identity['uid'],
                self.identities,
                distributor,
                self.session.query(Recipient).filter(Recipient.name==distributor).first().certs,
            )
            if not result['sigOK']:
                LOGGER.warning(
                    "Could not verify that %s correctly signed your password entry.",
                    result['distributor']
                )
            if not result['certOK']:
                LOGGER.warning(
                    "Could not verify the certificate authenticity of user '%s'.",
                    result['distributor']
                )
        return plaintext_pw
