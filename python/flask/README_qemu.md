# How to deploy Flask apps repeatably to QEMU with Packer, Ansible, and Terraform.

## Introduction

This tutorial provides everything one needs to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application to QEMU.

These instructions have only been tested on Debian.

The packer template comes from [kaorimatz/packer-templates](https://github.com/kaorimatz/packer-templates).  The 17.04 packer file was pulled and modified to work with the nublar variables file.

## Goals

-   Test [Ansible](http://docs.ansible.com/ansible/latest/index.html) with [Vagrant](https://www.vagrant.io/downloads.html)
-   Build a QCOW image with [Packer](https://www.packer.io/downloads.html)
-   Deploy the image to a [QEMU](https://www.qemu.com/products/compute/) instance with [Terraform](https://www.terraform.io/downloads.html)
-   Destroy the instance
-   Repeat

## Prerequisites

-   Install [QEMU](https://www.qemu.org/download/)
-   Install [Vagrant](https://www.vagrant.io/downloads.html) > 2.0
-   Install  [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
-   Install [Packer](https://www.packer.io/downloads.html)
-   Install [Terraform](https://www.terraform.io/downloads.html)

## Step 1 - Variables / Configuration

All the tools use the same variables file.

`NUBLAR_VARS`, an env var, is used to control the location of the variables file.

### Step 1a - Create the variables file
-   Set `NUBLAR_VARS`

    ```sh
    export NUBLAR_VARS=qemu/nublar.json
    ```

-   Copy the example file to a new file

    ```
    cp variables/${NUBLAR_VARS}.example variables/${NUBLAR_VARS}
    ```

### Step 1b - edit the variables file

-   `app_repo_url`
    -   python repository containing flask application
-   `app_subfolder`
    -   If setup.py is in a subfolder, specify this here (default = '')
-   `app_description`
    -   this will go into the system service script
-   `app_name`
    -   app folders and service name (default = nublar)
-   `app_user`
    -   system user and group will both be this value (default = nublar)
-   `app_domain`
    -   domain that nginx will answer to
-   `app_module`
    -   python module for uwsgi.ini
-   `app_callable`
    -   Flask application object for uwsgi.ini
-   `app_port`
    -   service port (default = 3000)
-   `app_health_ep`
    -   Ansible will check this for a 200 return code as a final step (default = /)
-   `uwsgi_process_count`
    -   number of uwsgi processes (default = 10)
-   `qemu_hostname`
    -   hostname for vm
-   `qemu_cpus`
    -   Number of cpus
-   `qemu_memory`
    -   RAM in MB
-   `qemu_iso_url`
    -   url to iso image
-   `qemu_iso_checksum`
    -   iso checksum value
-   `qemu_iso_checksum_type`
    -   iso checksum type (md5)

## Step 2 - test Ansible with Vagrant

Vagrant is useful to make sure the Ansible playbook works before trying Packer.  You can skip this step if you just want to get straight to packer.

The [Vagrant Ansible provisioner](https://www.vagrantup.com/docs/provisioning/ansible.html) is configured to run the  [flask-uwsgi-nginx](https://galaxy.ansible.com/lex00/flask-uwsgi-nginx/) role.

-   Change into the ansible folder

    ```sh
    cd config_management/ansible
    ```

-   Bring up [Vagrant](https://www.vagrant.io/downloads.html) (this will run [Ansible](http://docs.ansible.com/ansible/latest/index.html) the first time)

    ```sh
    vagrant up
    ```

-   Run [Ansible](http://docs.ansible.com/ansible/latest/index.html)

    ```sh
    vagrant provision
    ```

    WARNING: Vagrant downloads the role from Ansible Galaxy and deletes it after provisioning.  If Packer is bombing in the next step, you can forcefully delete the downloaded role:

    -   `rm -fr config_management/ansible/roles/*`


-   View the Flask app in your browser

    `http://localhost:{app_port}/`

## Step 3 - build the machine image with Packer

[Packer](https://www.packer.io/downloads.html) is going to:

-   create a new QEMU image
-   provision it with Ansible, installing the Flask app
-   save the new QEMU image

[The Packer Ansible Local provisioner](https://www.packer.io/docs/provisioners/ansible-local.html) is configured to run the  [flask-uwsgi-nginx](https://galaxy.ansible.com/lex00/flask-uwsgi-nginx/) role.

-   Change into the packer folder

    ```sh
    cd imaging/packer/qemu
    ```

-   Run the [Packer](https://www.packer.io/downloads.html) build:

    ```sh
    PACKER_CACHE_DIR=~/.packer packer build -var-file=../../../variables/${NUBLAR_VARS} packer.json
    ```

## Step 4 - test boot the machine image

A script is provided to start the instance using `qemu`.

```sh
cd imaging/packer/qemu
./run.sh
```

Check your browser to see the app

`http://localhost:{{ app_port }}`

Test ssh (pw=ubuntu)

`ssh -p22222 ubuntu@localhost`

## Step 5 - setup terraform libvirt provider

-   [dmacvicar/terraform-provider-libvirt](https://github.com/dmacvicar/terraform-provider-libvirt)

    ```sh
    go get github.com/dmacvicar/terraform-provider-libvirt
    cd $GOPATH/src/github.com/dmacvicar/terraform-provider-libvirt/
    go install
    ```

-   Add provider to terraform environment

    ```sh
    cd infrastructure_management/terraform/qemu
    mkdir -p terraform.d/plugins/linux_amd64
    cp ~/.go/bin/terraform-provider-libvirt terraform.d/plugins/linux_amd64/
    ```

## Step 6 - create qemu instance with terraform

After finishing this step, your new instance should be visible in `virt-manager`

-   Initialize [Terraform](https://www.terraform.io/downloads.html) (first time only):

    ```sh
    terraform init
    ```

-   Try to plan with [Terraform](https://www.terraform.io/downloads.html).  You will need your API token.

    ```sh
    export TF_VAR_DIGITALOCEAN_TOKEN=...
    terraform plan -var-file=../../../variables/${NUBLAR_VARS} -out tfplan
    ```

-   If the plan output looks safe, apply it

    ```sh
    terraform apply tfplan
    ```

-   Delete the old plan, *do not use it again*

    ```sh
    rm tfplan
    ```

## Step 7 - login to the instance

-   Use Terraform to lookup the ip address

    ```sh
    terraform show

    ...
    network_interface.0.addresses.0 = 10.0.100.xxx
    ...
    ```

-   The ssh username and password are `ubuntu`

    -   `ssh ubuntu@{{ ip_address }}`


-   The app will now answer at the new ip and port configured in `nublar.json`.

    -   `http://{{ ip_address }}:{{ nublar_port }}/`

## Step 8 - destroy the instance

After finishing this step, your new instance should be gone from `virt-manager`.

-   This will delete your instance:

    ```sh
    terraform destroy -var-file=../../../variables/${NUBLAR_VARS}
    ```

## Step 9 - do it all again, and again

-   Add a new endpoint to the [Flask](http://flask.pocoo.org/docs/0.12/) app
-   Bump the version in setup.py
-   Repeat steps 2-8

# Conclusion

Congratulations, you are now equipped to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application repeatably to QEMU.

Now is a great time to try editing the [Ansible](http://docs.ansible.com/ansible/latest/index.html), [Packer](https://www.packer.io/downloads.html), and [Terraform](https://www.terraform.io/downloads.html) configuration to teach yourself a bit more about these tools.
