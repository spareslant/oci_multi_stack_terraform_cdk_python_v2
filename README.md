---
title: "(version-2) Multiple Stacks TerraformCDK in Python Oracle Cloud Infrastructure (OCI)"
date: 2022-02-01T19:48:39Z
draft: true
---

# Introduction
Terraform has releases a new version of `cdktf = 0.9.0`. This version makes cross referencing across stacks easy. This document will explore this feature. It is built upon previous version of code mentioned below.

* previous version of code
```bash
https://github.com/spareslant/oci_multi_stack_terraform_cdk_python
```


We will be creating a public facing VM in Oracle Cloud Infrastructure (OCI) using terraform cdk toolkit. We will be writing terraform code in `Python` and we will be using `terraform stacks`. 


## What will be done in terraform stack
* We will create a stack `priv_user_compartment` to create a privileged user `cdk-user` and a compartment `CDK`. This user will have full admin rights in this compartment.
* We will create a stack `network` to create `VCN`, `subnets`, `internet gateway`, `dhcp options`, `route tables` etc. in above created `compartment`. This stack will use above created user's credentials (`cdk-user`) NOT tenancy admin credentials.
* We will create a stack `vm_instance` to create a internet facing VM in above created `VCN` and `compartment` and this stack uses above created user's credentials `cdk-user` to do so.
* Code will be passing information from one stack to another.


## Development Environment
* OS used: MacOS Monterey (12.0.1)
* Python version used: 3.10.0
* Package manager: brew
* Pipenv: We will be using `pipenv`

**Note:** `pipenv` creates python virtual environment behind the scenes. 


### Install `python` via `pyenv`
```bash
brew install pyenv
pyenv install 3.10.0
pyenv global 3.10.0
```

### Install `pipenv`
```bash
pip install pipenv
```

### Install `terraform` using tfenv
```bash
brew install tfenv
tfenv install 1.1.4
tfenv use 1.1.4
```

### Install `node.js` via `nvm`
```bash
brew install nvm
nvm install --lts
nvm use --lts
$ node --version
v16.13.0
nvm alias default 16.13.2
```

### Install `cdktf-cli`
```bash
npm install --global cdktf-cli

$ cdktf --version
0.9.0
```

## Prepare coding directory (if starting from scratch)

### Initiate `cdktf` project
```bash
mkdir oci_multi_stack_terraform_cdk_python
cd oci_multi_stack_terraform_cdk_python
cdktf init --template="python" --local
```
Above command will initiate a `pipenv`. To see the location of virtualenv that pipenv created run this command ` pipenv --venv`.

### Install required packages (`oci sdk` and others) using `pipenv`
```bash
pipenv install pycryptodome oci oci-cli
```

#### Files in current direcotry
```bash
cdktf.json  help  main.py  Pipfile  Pipfile.lock
```

## Prepare coding directory (if cloning the repo)

### Clone repo
```bash
git clone https://github.com/spareslant/oci_multi_stack_terraform_cdk_python_v2.git
cd oci_multi_stack_terraform_cdk_python_v2
```

### Install required pip modules using pipenv
```bash
pipenv sync
```

### Download OCI terraform modules libraries

#### Add terraform provider information in `cdktf.json` file
**Note:** No need for this step if using cloned repo as working directory.
```json
{
  "language": "python",
  "app": "pipenv run python main.py",
  "terraformProviders": [
    "oci@~> 4.61.0",
    "cloudinit@~> 2.2.0",
    "tls@~> 3.1.0",
    "local@~> 2.1.0",
    "external@~> 2.2.0"
  ],
  "terraformModules": [],
  "codeMakerOutput": "imports",
  "context": {
    "excludeStackIdFromLogicalIds": "true",
"allowSepCharsInLogicalIds": "true"
  }
}
```

#### Get terraform libraries
```bash
cdktf get
```

#### Files in current direcotry
```bash
$ /bin/ls
Pipfile                 cdktf.json              imports                 package-lock.json
Pipfile.lock            help                    main.py                 package.json
```

## Prepare OCI environment
* You need an `OCI` account. Its free. SignUp at https://cloud.oracle.com. This sign-up account is called `Tenancy Admin` account.
* Login to this `Tenancy Admin` account. Make sure you have selected `Oracle Cloud Infrastructure Direct Sign-In` option on the login page.
* click hamburger icon on the top-left corner 
    * click `Identity & Security`
    * click `users`
    * click your email ID here (the one you used for sign-up)
    * click `API Keys`
    * click `Add API Key`
    * select `Generate API Key Pair`
    * click `Download private key`
    * click `Add` button
    * Copy the content in `Configuration File Preview` and save it. We need it later on.
    * click `close`


### Configure Tenancy Admin account to access OCI via APIs
You can run `oci setup config` command to setup the oci config. But we will be following direct manual method as we already have config saved in previous step when we prepared the oci envrionment.
```bash
mkdir ~/.oci
chmod g-rwx,o-rwx /root/.oci

ls -ld /root/.oci/
drwx------ 2 root root 4096 Sep 20 23:36 /root/.oci/

touch ~/.oci/tenancyAdmin_private_api_key.pem
vim ~/.oci/tenancyAdmin_private_api_key.pem
```
Paste the contents from file that you downloaded during the step `download private key` above in file `~/.oci/tenancyAdmin_private_api_key.pem`

```bash
chmod 600 ~/.oci/tenancyAdmin_private_api_key.pem
touch ~/.oci/config
chmod 600 ~/.oci/config
vim  ~/.oci/config
```
Paste the contents from file that you saved during the step `Configuration file preview` above in file `~/.oci/config`

Contents of `~/.oci/config` will be similar to the following.
```ini
[DEFAULT]
user=ocid1.user.oc1..<a very long string>
fingerprint=xx:yy:11:22:33:44:d4:56:b6:67:89:b7:b1:7f:4f:7a
tenancy=ocid1.tenancy.oc1..<a very long string>
region=uk-london-1
key_file=~/.oci/tenancyAdmin_private_api_key.pem
```
Please note `key_file=` above.


### Verify connectivity to OCI
```bash
cd oci_multi_stack_terraform_cdk_python
pipenv shell
oci iam user list
exit
```
Above command (`oci iam user list`) must run successfully.


## Prepare terraform code to execute
Populate following files with contents as mentioned in this git repo.

* `common.py`
* `main.py`
* `local_utils.py`
* `privUserAndCompartment.py`
* `network.py`
* `systemsAndApps.py`
* `cdktf.json`


## Deploy stacks

### list stacks
```
$ cdktf list
WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Stack name                      Path
dummy_hosting_stack             cdktf.out/stacks/dummy_hosting_stack
priv_user_compartment           cdktf.out/stacks/priv_user_compartment
```
**Note-1:** Listing of stacks is not in order. You need to run the each stack separately. Hence if there is depencies among stacks then you need to remember the order of deployment and destruction of stacks.

**Note-2:** Deployment of `priv_user_compartment` creates an oci config file for `cdk-user`. After this deployment, you should see two more stacks.


### Deploy first stack `priv_user_compartment`
```
cdktf deploy priv_user_compartment --auto-approve
WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: priv_user_compartment
Resources
 ✔ LOCAL_FILE           cdk-user_private_ke local_file.cdk-user_private_key_file
                        y_file
 ✔ LOCAL_FILE           cdk-user_public_key local_file.cdk-user_public_key_file
                        _file
 ✔ LOCAL_FILE           oci_config_file     local_file.oci_config_file
 ✔ OCI_IDENTITY_API_KEY cdk-user_api_keys   oci_identity_api_key.cdk-user_api_keys
 ✔ OCI_IDENTITY_COMPART CDK_compartment     oci_identity_compartment.CDK_compartmen
   MENT                                     t
 ✔ OCI_IDENTITY_GROUP   cdk-group           oci_identity_group.cdk-group
 ✔ OCI_IDENTITY_POLICY  cdk-group_policy    oci_identity_policy.cdk-group_policy
 ✔ OCI_IDENTITY_USER    cdk-user            oci_identity_user.cdk-user
 ✔ OCI_IDENTITY_USER_GR cdk-user_cdk-group_ oci_identity_user_group_membership.cdk-
   OUP_MEMBERSHIP       membership          user_cdk-group_membership
 ✔ TLS_PRIVATE_KEY      cdk-user_keys       tls_private_key.cdk-user_keys

Summary: 10 created, 0 updated, 0 destroyed.

Output: CDK_id = ocid1.compartment.oc1..aaaaaaaaaabbbbbbbbbbbbbbbbbbbbbccccccccccccccccc
        cdk-group_id = ocid1.group.oc1..aaaaaaaaebbbbbbbbbbbbbcccccccccccccccdddddd
        cdk-user_fingerprint = aa:bb:cc:11:22:33:44:55:a1:a2:a3:a4:b1:b2:b3:b5
        cdk-user_id = ocid1.user.oc1..aaaaaaaabbbbbbbbccccccccccccccdddddddd
        cdk-user_private_key = <sensitive>
```
**Note:** For unknown reason, perhaps bug, above output is missing an entry. That entry is must exist, otherwise subsequent stack deployments will fail which are dependent on this stack. We will list the stack deployments first in next step and re-run the deployment of `priv_user_compartment` again.

### list stacks again
```
$ cdktf list
WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Stack name                      Path
dummy_hosting_stack             cdktf.out/stacks/dummy_hosting_stack
priv_user_compartment           cdktf.out/stacks/priv_user_compartment
network                         cdktf.out/stacks/network
vm_instance                     cdktf.out/stacks/vm_instance
```
**Note:** Two more stacks have appeared now.

### re-run `priv_user_compartment` deployment again
```
$ cdktf deploy priv_user_compartment --auto-approve
WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: priv_user_compartment

Output: CDK_id = ocid1.compartment.oc1..aaaaaaaaaabbbbbbbbbbbbbbbbbbbbbccccccccccccccccc
        cdk-group_id = ocid1.group.oc1..aaaaaaaaebbbbbbbbbbbbbcccccccccccccccdddddd
        cdk-user_fingerprint = aa:bb:cc:11:22:33:44:55:a1:a2:a3:a4:b1:b2:b3:b5
        cdk-user_id = ocid1.user.oc1..aaaaaaaabbbbbbbbccccccccccccccdddddddd
        cdk-user_private_key = <sensitive>
        cross-stack-output-oci_identity_compartmentCDK_compartmentid = <sensitive>
```
**Note:** A new entry has come up in above output.


### Deploy second stack `network`
```
$ cdktf deploy network --auto-approve
WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: network
Resources
 ✔ OCI_CORE_DHCP_OPTION DHCP_OPTIONS        oci_core_dhcp_options.DHCP_OPTIONS
   S
 ✔ OCI_CORE_INTERNET_GA cdk_internet_gatewa oci_core_internet_gateway.cdk_internet_
   TEWAY                y                   gateway
 ✔ OCI_CORE_ROUTE_TABLE cdk_route_table     oci_core_route_table.cdk_route_table
 ✔ OCI_CORE_ROUTE_TABLE cdk_route_attachmen oci_core_route_table_attachment.cdk_rou
   _ATTACHMENT          t                   te_attachment
 ✔ OCI_CORE_SUBNET      cdk_public_subnet   oci_core_subnet.cdk_public_subnet
 ✔ OCI_CORE_VCN         cdk_vcn             oci_core_vcn.cdk_vcn

Summary: 6 created, 0 updated, 0 destroyed.

Output: cdk_network_public_subnet = ocid1.subnet.oc1.uk-london-1.aaaaaaaabbbbbbbbbbbbccccccccccdddddddddddddd
        cross-stack-output-oci_core_subnetcdk_public_subnetid = <sensitive>
```


### Deploy third stack `vm_instance`
```
$ cdktf deploy vm_instance --auto-approve


WARNING!!!!!!!!: Terraform might have written a new oci config file at ~/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: vm_instance
Resources
 ✔ LOCAL_FILE           cdk_vm_private_key_ local_file.cdk_vm_private_key_file
                        file
 ✔ OCI_CORE_INSTANCE    cdk_vm_instance     oci_core_instance.cdk_vm_instance
 ✔ TLS_PRIVATE_KEY      cdk_vm_keys         tls_private_key.cdk_vm_keys

Summary: 3 created, 0 updated, 0 destroyed.

Output: cdk_vm_public_ip = xxx.yyy.zzz.vvv
```
**Note:** Above deployment has created a `keys/private_key.pem` for above created VM.


### Test the deployment
Login to VM
```bash
ssh -i keys/private_key.pem opc@IP_Address_of_above_created_VM
```

### destroy stacks (reverse order of deployment)
```bash
cdktf destroy vm_instance --auto-approve
cdktf destroy network --auto-approve
cdktf destroy priv_user_compartment --auto-approve
```

## How is passing information among stacks working

### In file `main.py`
```python
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
```

### In file `privUserAndCompartment.py`
* `priv_user_compartment` stack is exposing `priv_compartment` using `TerraformOutput`

```python
class PrivilegedUser(TerraformStack):

    priv_compartment = None

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        comp = IdentityCompartment(self, f"{priv_compartment}_compartment",
                name=priv_compartment,
                description=f"{priv_compartment} compartment",
                enable_delete=True,
                compartment_id=tenancyID)
        self.priv_compartment = comp
```

### In file `network.py`
* `network` stack is using exposed `priv_compartment` from `priv_user_compartment` stack.
* `network` stack is also exposing `network_public_subnet`

```python
class Network(TerraformStack):

    network_public_subnet = None

    def __init__(self, scope: Construct, ns: str, priv_compartment):
        super().__init__(scope, ns)

        priv_compartment_id = priv_compartment.id

        public_subnet = CoreSubnet(self, f"{unique_id}_public_subnet",
                cidr_block="10.0.0.0/24",
                vcn_id=vcn.id,
                compartment_id=priv_compartment_id,
                display_name="public_subnet",
                dhcp_options_id=dhcp_options.id)

        self.network_public_subnet = public_subnet
```

### In file `systemsAndApps.py`
* `vm_instance` instance stack is using exposed `priv_compartment` from `priv_user_compartment` stack
* `vm_instance` instance stack is using exposed `network_public_subnet` from `network` stack

```python
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
```

## Observations
* Passing information among stack has become much easier now.
