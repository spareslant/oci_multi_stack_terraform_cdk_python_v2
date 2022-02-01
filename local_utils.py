#! /usr/bin/env python

import configparser
import os, io

tenancy_profile_name = "DEFAULT"

def get_local_oci_config_value(profile_name, config_field, profile_config_file):
    c = configparser.ConfigParser()
    c.read(profile_config_file)
    return c[profile_name][config_field]

def write_oci_config_file(user, oci_user_creds):
    oci_user_config_file = os.environ['HOME'] + '/.oci/config'
    c = configparser.ConfigParser()
    c.read(oci_user_config_file)

    c[user] = oci_user_creds
    with io.StringIO() as oci_config_string:
        c.write(oci_config_string)
        oci_config = oci_config_string.getvalue()
    return oci_config

def user_creds(profile_name, oci_config_file):
    fingerprint = get_local_oci_config_value(profile_name, "fingerprint", oci_config_file)
    private_key_path = get_local_oci_config_value(profile_name, "key_file", oci_config_file)
    region = get_local_oci_config_value(profile_name, "region", oci_config_file)
    tenancy_ocid = get_local_oci_config_value(profile_name, "tenancy", oci_config_file)
    user_ocid = get_local_oci_config_value(profile_name, "user", oci_config_file)
    return (fingerprint,
            private_key_path,
            region,
            tenancy_ocid,
            user_ocid)


if __name__ == '__main__':
    oci_user_config_file = os.environ['HOME'] + '/.oci/config'
    print(f"root_compartment_id = {get_local_oci_config_value(tenancy_profile_name, 'tenancy', oci_user_config_file)}")
