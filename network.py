from constructs import Construct, Node
from cdktf import TerraformStack, TerraformOutput
from imports.oci import (
    OciProvider,
    CoreVcn,
	CoreSubnet,
	CoreDhcpOptions,
	CoreInternetGateway,
	CoreInternetGateway,
	CoreRouteTable,
	CoreDhcpOptionsOptions,
	CoreRouteTableRouteRules,
	CoreRouteTableAttachment
    )
from local_utils import (
        user_creds)

from common import (
        priv_user_profile_name,
        priv_user_oci_config_file,
        unique_id
        )

class Network(TerraformStack):

    network_public_subnet = None

    def __init__(self, scope: Construct, ns: str, priv_compartment):
        super().__init__(scope, ns)

        (fingerprint,
            private_key_path,
            region,
            tenancy_ocid,
            user_ocid) = user_creds(priv_user_profile_name, priv_user_oci_config_file)

        priv_compartment_id = priv_compartment.id

        # define resources here
        OciProvider(self, "oci",
                fingerprint=fingerprint,
                private_key_path=private_key_path,
                region=region,
                tenancy_ocid=tenancy_ocid,
                user_ocid=user_ocid)

        vcn = CoreVcn(self, f"{unique_id}_vcn",
                cidr_block="10.0.0.0/16",
                display_name=f"{unique_id}_vcn",
                compartment_id=priv_compartment_id)

        dhcp_options = CoreDhcpOptions(self, "DHCP_OPTIONS",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id,
                options=[
                    CoreDhcpOptionsOptions(
                    type="DomainNameServer",
                    server_type="VcnLocalPlusInternet")
                ]
            )

        public_subnet = CoreSubnet(self, f"{unique_id}_public_subnet",
                cidr_block="10.0.0.0/24",
                vcn_id=vcn.id,
                compartment_id=priv_compartment_id,
                display_name="public_subnet",
                dhcp_options_id=dhcp_options.id)
        self.network_public_subnet = public_subnet

        internet_gateway = CoreInternetGateway(self, f"{unique_id}_internet_gateway",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id)

        route_table = CoreRouteTable(self, f"{unique_id}_route_table",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id,
                route_rules=[
                    CoreRouteTableRouteRules(
                        network_entity_id=internet_gateway.id,
                        destination="0.0.0.0/0"
                        )
                    ])
        CoreRouteTableAttachment(self, f"{unique_id}_route_attachment",
                subnet_id=public_subnet.id,
                route_table_id=route_table.id)

        TerraformOutput(self, f"{unique_id}_network_public_subnet",
                value=public_subnet.id).friendly_unique_id

    def name(self):
        return Node.of(self).id
