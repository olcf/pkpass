Alternate Backend Support
============================

A backend of yubico-piv-tool with libp11 is now supported for users as an alternative to opensc. 

The default backend is opensc, but users have the ability to use yubico-piv-tool and libp11 instead.

The alternate backend is intended to be used primarily by users on MacOs, where packages can be most easily installed with brew.

This can be enabled by adding the following line to the .pkpassrc:

``SCBackend: yubi``

To support this alternate backend, the path to the PCKS11 module is an argument that can be modified by setting PKCS11_module_path in the .pkpassrc.

If not specified, PKCS11_module_path will be set to this default value:

``PKCS11_module_path="/usr/local/lib/libykcs11.dylib"``

This default value is intended for opensc usage. For alternate backend it should be modified. 

To modify PKCS11_module_path to support yubico-piv-tool with libp11, add this line to the .pkpassrc:

``PKCS11_module_path="/path/to/libp11/libpkcs11.dylib"``

The alternate backend is also supported by the verify install command.

To confirm that the alternate backend is configured correctly run:

``pkpass verifyinstall``

If the alternate backend support is enabled and a brew installation is found, the verifyinstall function will attempt to check if the dependencies have been installed through brew or through other means. If packages are installed through brew, checks will be done to confirm the presence of required .dylib files. If a .dylib file is not found a warning will be displayed. A warning may be displayed if there is no .dylib file in the default PKCS11_module_path, but if PKCS11_module_path is NOT set to the default path then this can be ignored.
