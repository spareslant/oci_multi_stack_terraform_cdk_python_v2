import os

unique_id = "cdk"

priv_compartment = "CDK"
priv_user = "cdk-user"
priv_user_profile_name = priv_user
priv_group = "cdk-group"

tenancy_profile_name = "DEFAULT"
oci_config_dir = f"{os.environ['HOME']}/.oci"
tenancy_profile_config_file = f"{oci_config_dir}/config"
group_policy_1 = f"Allow group {priv_group} to manage all-resources in compartment {priv_compartment}"

priv_user_private_key_file = f"{oci_config_dir}/{priv_user}_private_api_key.pem"
oci_config_private_key_filename = f"~/.oci/{priv_user}_private_api_key.pem"
priv_user_public_key_file = f"{oci_config_dir}/{priv_user}_public_api_key.pem"
priv_user_oci_config_file = f"{oci_config_dir}/config.{priv_user}"
