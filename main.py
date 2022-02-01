#!/usr/bin/env python
from cdktf import App
from constructs import Construct
from cdktf import TerraformStack

from privUserAndCompartment import PrivilegedUser
from network import Network
from systemsAndApps import VmInstance
import os

app = App()

class RunStack(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        priv_user = PrivilegedUser(self, "priv_user_compartment")
        priv_user.message()

        if os.path.exists(f"{os.environ['HOME']}/.oci/config.cdk-user"):

            network = Network(self, "network",
                    priv_user.priv_compartment)

            VmInstance(self, "vm_instance",
                   priv_user.priv_compartment,
                   network.network_public_subnet)


RunStack(app, "dummy_hosting_stack")
app.synth()
