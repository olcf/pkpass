#!/bin/bash
set -euxo pipefail
rm -rf ca intermediate

for ca in 'ca' 'intermediate'; do
  mkdir -p $ca/certs $ca/crl $ca/newcerts $ca/private $ca/csr
  chmod 700 $ca/private
  touch $ca/index.txt
  touch $ca/index.txt.attr
  echo '1000' > $ca/serial
done

cat << EOF > ca/openssl.cnf
[ca]
default_ca = default

[default]
dir           = ca
certs         = \$dir/certs
new_certs_dir = \$dir/newcerts
database      = \$dir/index.txt
serial        = \$dir/serial
RANDFILE      = \$dir/private/.rand
certificate = \$dir/certs/ca.cert
private_key = \$dir/private/ca.key
default_days     = 605
default_crl_days = 30
default_md       = sha256
preserve         = no
policy           = default_policy


[default_policy]
countryName            = optional
stateOrProvinceName    = optional
localityName           = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional


[ req ]
prompt = no
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
req_extensions     = v3_ca

[ req_distinguished_name ]
C = UT 
ST = unittesting
L = unittesting
O = unittesting
CN = unittesting

[ v3_ca ]
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

EOF
intermediate(){
cat << EOF > intermediate/openssl.cnf
[ca]
default_ca = default

[default]
dir           = ca
certs         = \$dir/certs
new_certs_dir = \$dir/newcerts
database      = \$dir/index.txt
serial        = \$dir/serial
RANDFILE      = \$dir/private/.rand
certificate = \$dir/certs/ca.cert
private_key = \$dir/private/ca.key
default_days     = 605
default_crl_days = 30
default_md       = sha256
preserve         = no
policy           = default_policy


[default_policy]
countryName            = optional
stateOrProvinceName    = optional
localityName           = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional


[ req ]
prompt = no
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
req_extensions     = v3_ca

[ req_distinguished_name ]
C = UT 
ST = unittesting
L = unittesting
O = unittesting
CN = $carecipient

[ v3_ca ]
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

EOF

}
export carecipient=unitt
intermediate

# Create Root CA
openssl genrsa -out ca/private/ca.key 4096
openssl req -config ca/openssl.cnf -key ca/private/ca.key -new -x509 -days 600 -out ca/certs/ca.cert
chmod 400 ca/private/ca.key

# Create Intermediate CA
openssl genrsa -out intermediate/private/ca.key 4096
chmod 400 ca/private/ca.key

openssl req -config intermediate/openssl.cnf -key intermediate/private/ca.key -new -x509 -days 600 -out intermediate/certs/ca.cert
cat ca/certs/ca.cert intermediate/certs/ca.cert > intermediate/certs/ca-bundle
chmod 444 intermediate/certs/ca-bundle

for recipient in 'r1' 'r2' 'r3' 'r4' 'r5'; do
  export carecipient="$recipient"
  intermediate
  openssl genrsa -out intermediate/private/${recipient}.key 4096
  chmod 400 intermediate/private/${recipient}.key

  openssl req -config intermediate/openssl.cnf -key intermediate/private/${recipient}.key -new -sha256 -out intermediate/csr/${recipient}.csr

  openssl ca -config ca/openssl.cnf -days 600 -in intermediate/csr/${recipient}.csr -out intermediate/certs/${recipient}.cert -batch
  chmod 444 intermediate/certs/${recipient}.cert

done
