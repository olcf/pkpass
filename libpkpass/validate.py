#!/usr/bin/python
"""This Module validates password objects"""


    #############################################################################
def validate_password(password_obj):
    """ Run through password object and validate everything that needs it """
    ##############################################################################

    # Validate that required fields exist
    # Validate that certificate signatures are valid
    # Validate that password length meets whatever
    # Validate that escrow password is there if needed
    # Validate that things encrypted/decrypted successfully
    return


    #############################################################################
def validate_passwords(password_objs):
    """ Run through password object and validate everything that needs it """
    ##############################################################################

    for password_obj in password_objs:
        validate_password(password_obj)
