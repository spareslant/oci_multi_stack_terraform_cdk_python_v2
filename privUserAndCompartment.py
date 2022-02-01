from constructs import Construct, Node
from cdktf import TerraformStack, TerraformOutput
from imports.tls import TlsProvider, PrivateKey
from imports.local import LocalProvider, File
from imports.oci import (
    OciProvider,
    IdentityCompartment,
    IdentityUser,
    IdentityGroup,
    IdentityUserGroupMembership,
    IdentityPolicy,
    IdentityApiKey
    )
from local_utils import (
    user_creds,
    write_oci_config_file)

from common import (
    priv_compartment,
    priv_user,
    priv_group,
    group_policy_1,
    oci_config_private_key_filename,
    priv_user_private_key_file,
    priv_user_public_key_file,
    priv_user_oci_config_file,
    tenancy_profile_name,
    tenancy_profile_config_file
        )

class PrivilegedUser(TerraformStack):

    priv_compartment = None

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        (_, _, region, tenancyID, _) = user_creds(tenancy_profile_name, tenancy_profile_config_file)

        # define resources here
        
        OciProvider(self, "oci",
                config_file_profile=tenancy_profile_name)

        TlsProvider(self, "oci_tls")

        LocalProvider(self, "oci_local_provider")

        api_keys = PrivateKey(self, f"{priv_user}_keys",
                algorithm="RSA")
        
        comp = IdentityCompartment(self, f"{priv_compartment}_compartment",
                name=priv_compartment,
                description=f"{priv_compartment} compartment",
                enable_delete=True,
                compartment_id=tenancyID)
        self.priv_compartment = comp

        user = IdentityUser(self, f"{priv_user}",
                name=priv_user,
                description=f"{priv_user} user",
                compartment_id=tenancyID)
        group = IdentityGroup(self, f"{priv_group}",
                name=priv_group,
                description=f"{priv_group} group",
                compartment_id=tenancyID)
        IdentityUserGroupMembership(self,
                f"{priv_user}_{priv_group}_membership",
                group_id=group.id,
                user_id=user.id)
        IdentityPolicy(self, f"{priv_group}_policy",
                name=f"{priv_group}_policy",
                description=f"{priv_group} policies",
                compartment_id=comp.id,
                statements=[
                   group_policy_1
                ])
        user_api_key = IdentityApiKey(self, f"{priv_user}_api_keys",
                user_id=user.id,
                key_value=api_keys.public_key_pem)

        TerraformOutput(self, f"{priv_compartment}_id",
                value=comp.id).friendly_unique_id

        TerraformOutput(self, f"{priv_user}_id",
                value=user.id)
        TerraformOutput(self, f"{priv_group}_id",
                value=group.id)
        TerraformOutput(self, f"{priv_user}_private_key",
                value=api_keys.private_key_pem,
                sensitive=True)
        TerraformOutput(self, f"{priv_user}_fingerprint",
               value=user_api_key.fingerprint)

        File(self, f"{priv_user}_private_key_file",
                content=api_keys.private_key_pem,
                filename=priv_user_private_key_file,
                file_permission="0600")    
        File(self, f"{priv_user}_public_key_file",
                content=api_keys.public_key_pem,
                filename=priv_user_public_key_file,
                file_permission="0644")    

        priv_user_oci_creds = {}
        priv_user_oci_creds["user"] = user.id
        priv_user_oci_creds["fingerprint"] = user_api_key.fingerprint
        priv_user_oci_creds["tenancy"] = tenancyID
        priv_user_oci_creds["region"] = region
        priv_user_oci_creds["key_file"] = oci_config_private_key_filename

        # We can't write ~/.oci/config file without File terraform resource, because
        # used.id and user_api_key.fingerprint etc will be evaluated only during the
        # File resource call.
        # If we use python file write functions here, it gets executed very first thing
        # in terraform and user.id and user_api_key.fingerprint would NOT have been
        # evaluated.
        File(self, "oci_config_file",
                content=write_oci_config_file(priv_user, priv_user_oci_creds),
                filename=priv_user_oci_config_file,
                file_permission="0600")

    def name(self):
        return Node.of(self).id

    def message(self):
        print(f"WARNING!!!!!!!!: Terraform might have written a new oci config file at {priv_user_oci_config_file}. Terraform will manage this file automatically.")
