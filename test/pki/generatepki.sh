#!/bin/bash

rm -rf ca intermediate

for ca in 'ca' 'intermediate'; do
  mkdir -p $ca/certs $ca/crl $ca/newcerts $ca/private $ca/csr
  chmod 700 $ca/private
  touch $ca/index.txt
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
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
x509_extensions     = v3_ca

[ req_distinguished_name ]
countryName                     = Country Name (2 letter code)
stateOrProvinceName             = State or Province Name
localityName                    = Locality Name
0.organizationName              = Organization Name
organizationalUnitName          = Organizational Unit Name
commonName                      = Common Name
emailAddress                    = Email Address

countryName_default             = UT 
stateOrProvinceName_default     = unittesting
localityName_default            = unittesting
0.organizationName_default      = unittesting
commonName_default              = unittesting

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

EOF
intermediate(){
cat << EOF > intermediate/openssl.cnf
[ca]

default_ca = default

[default]

dir           = intermediate 
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
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
x509_extensions     = v3_ca

[ req_distinguished_name ]
countryName                     = Country Name (2 letter code)
stateOrProvinceName             = State or Province Name
localityName                    = Locality Name
0.organizationName              = Organization Name
organizationalUnitName          = Organizational Unit Name
commonName                      = Common Name
emailAddress                    = Email Address

countryName_default             = UT 
stateOrProvinceName_default     = unittesting
localityName_default            = unittesting
0.organizationName_default      = unittesting
commonName_default              = $cnrecipient

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true, pathlen:0
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

EOF

}
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

for recipient in 'r1' 'r2' 'r3'; do
  export cnrecipient=$recipient
  intermediate
  openssl genrsa -out intermediate/private/${recipient}.key 4096
  chmod 400 intermediate/private/${recipient}.key
  
  echo
  echo
  echo
  echo "!!!! ENTER '$recipient' for Common Name and type 'y' when asked! !!!!"
  echo
  echo
  echo

  openssl req -config intermediate/openssl.cnf -key intermediate/private/${recipient}.key -new -sha256 -out intermediate/csr/${recipient}.csr

  openssl ca -config ca/openssl.cnf -days 600 -in intermediate/csr/${recipient}.csr -out intermediate/certs/${recipient}.cert
  chmod 444 intermediate/certs/${recipient}.cert

done
