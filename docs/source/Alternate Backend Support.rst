Alternate Backend Support
============================

A backend of yubico-piv-tool with libp11 is now supported for users as an alternative to opensc. 

The default backend is opensc, but users have the ability to use yubico-piv-tool and libp11 instead.

This can be enabled by adding the following line to the .pkpassrc:

```SCBackend: yubi```

To support this alternate backend, the path to the PCKS11 module is an argument that can be modified by setting PKCS11_module_path in the .pkpassrc.

If not specified, PKCS11_module_path will be set to this default value:

```PKCS11_module_path="/usr/local/lib/libykcs11.dylib"```

This default value is intended for opensc usage. For alternate backend it should be modified. 

To modify PKCS11_module_path to support yubico-piv-tool with libp11, add this line to the .pkpassrc:

```PKCS11_module_path="/path/to/libp11/libpkcs11.dylib"```

