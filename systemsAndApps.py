import os
from constructs import Construct, Node
from cdktf import TerraformStack, TerraformOutput
from imports.tls import TlsProvider, PrivateKey
from imports.local import LocalProvider, File
from imports.oci import (
    OciProvider,
    CoreInstance,
    CoreInstanceCreateVnicDetails,
    DataOciIdentityAvailabilityDomain
    )

from local_utils import (
        user_creds)

from common import (
        priv_user_profile_name,
        priv_user_oci_config_file,
        unique_id
        )

class VmInstance(TerraformStack):
    def __init__(self, scope: Construct, ns: str,
            priv_compartment,
            public_subnet):
        super().__init__(scope, ns)

        (fingerprint,
            private_key_path,
            region,
            tenancy_ocid,
            user_ocid) = user_creds(priv_user_profile_name, priv_user_oci_config_file)

        priv_compartment_id = priv_compartment.id
        public_subnet_id = public_subnet.id

        image_id = "ocid1.image.oc1.uk-london-1.aaaaaaaa7p27563e2wyhmn533gp7g3wbohrhjacsy3r5rpujyr6n6atqppuq"

        # define resources here
        OciProvider(self, "oci",
                fingerprint=fingerprint,
                private_key_path=private_key_path,
                region=region,
                tenancy_ocid=tenancy_ocid,
                user_ocid=user_ocid)

        TlsProvider(self, "oci_tls")

        LocalProvider(self, "oci_local_provider")

        avail_domain = DataOciIdentityAvailabilityDomain(self, f"{unique_id}_availability_domain",
                compartment_id=priv_compartment_id,
                ad_number=1)

        vm_keys = PrivateKey(self, f"{unique_id}_vm_keys",
                algorithm="RSA")

        vm = CoreInstance(self, f"{unique_id}_vm_instance",
                compartment_id=priv_compartment_id,
                shape="VM.Standard.E2.1.Micro",
                availability_domain=avail_domain.name,
                image=image_id,
                create_vnic_details=CoreInstanceCreateVnicDetails(
                        subnet_id=public_subnet_id),
                metadata={
                    "ssh_authorized_keys": vm_keys.public_key_openssh,
                    }
                    
                )
        TerraformOutput(self, f"{unique_id}_vm_public_ip",
                value=vm.public_ip)

        File(self, f"{unique_id}_vm_private_key_file",
                content=vm_keys.private_key_pem,
                filename=f"{os.path.dirname(os.path.abspath(__file__))}/keys/private_key.pem",
                file_permission="0600")    


    def name(self):
        return Node.of(self).id

