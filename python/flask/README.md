# How to deploy Flask apps repeatably to Digital Ocean with Packer, Ansible, and Terraform.

## Introduction

This tutorial provides everything one needs to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application to Digital Ocean.

## Goals

-   Test [Ansible](http://docs.ansible.com/ansible/latest/index.html) with [Vagrant](https://www.vagrant.io/downloads.html)
-   Build a machine image with [Packer](https://www.packer.io/downloads.html)
-   Deploy the image to a [Digital Ocean](https://www.digitalocean.com/products/compute/) droplet with [Terraform](https://www.terraform.io/downloads.html)
-   Destroy the droplet
-   Repeat

## Prerequisites

-   Install [Vagrant](https://www.vagrant.io/downloads.html) > 2.0
-   Install  [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
-   Install [Packer](https://www.packer.io/downloads.html)
-   Install [Terraform](https://www.terraform.io/downloads.html)
-   [Setup a SSH key in your Digital Ocean account](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets)
-   [Setup an API token in your Digital Ocean account](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2)

## Step 1 - Variables / Configuration

All the tools use the same variables file.

`NUBLAR_VARS`, an env var, is used to control the location of the variables file.

### Step 1a - Create the variables file
-   Set `NUBLAR_VARS`

    ```sh
    export NUBLAR_VARS=digitalocean/nublar.json
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
-   `do_template_image`
    -   Digital Ocean image used by  [Packer](https://www.packer.io/downloads.html) (default = ubuntu-14-04-x64)
-   `do_droplet_name`
    -   hostname for droplet (no underscores allowed)
-   `do_image`
    -   snapshot id used by [Terraform](https://www.terraform.io/downloads.html)
-   `do_ssh_keys`
    -   ssh key ids from Digital Ocean account
-   `do_region`
    -   Digital Ocean region (default = nyc1)
-   `do_size`
    -   Droplet size (default = 512mb)
-   `do_ssh_username`
    -   (default = root)

## Step 2 - test Ansible with Vagrant

Vagrant is useful to make sure the Ansible playbook works before trying Packer.

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

-   provision a new droplet
-   install the Flask app
-   save a snapshot.

[The Packer Ansible Local provisioner](https://www.packer.io/docs/provisioners/ansible-local.html) is configured to run the  [flask-uwsgi-nginx](https://galaxy.ansible.com/lex00/flask-uwsgi-nginx/) role.

-   Change into the packer folder

    ```sh
    cd imaging/packer/digitalocean
    ```

-   Run the [Packer](https://www.packer.io/downloads.html) build, you will need your API token:

    ```sh
    export DIGITALOCEAN_API_TOKEN=...
    packer build -var-file=../../../variables/${NUBLAR_VARS} packer.json
    ```

-   Get the new snapshot ID from the output (or your Digital Ocean web panel):

    ```
    ==> Builds finished. The artifacts of successful builds are:
    --> digitalocean: A snapshot was created: 'nublar-15...' (ID: 29...) in regions ''
    ```

## Step 4 - deploy a droplet with Terraform

Now that we have a snapshot ID, we can use it to create a new droplet.

If you have a domain setup with Digital Ocean, you can use the [digitalocean_domain](https://www.terraform.io/docs/providers/do/r/domain.html) and [digitalocean_record](https://www.terraform.io/docs/providers/do/r/record.html) resources to point at the new droplet ip.  This is not covered here, although Nginx is ready to answer to the domain as configured with `app_domain`.

-   Change into the terraform folder

    ```sh
    cd infrastructure_management/terraform/digitalocean
    ```

#### Terraform setup
-   Initialize [Terraform](https://www.terraform.io/downloads.html) (first time only):

    ```sh
    terraform init
    ```

-   Edit `variables/digitalocean/nublar.json`

    -   `do_image`
        -   set this to the new snapshot id

    -   `do_ssh_keys`
        -   an ssh key id from your DO account


[Tugboat](https://github.com/petems/tugboat) can help you lookup these ssh key and snapshot ids.

#### Terraform plan
-   Try to plan with [Terraform](https://www.terraform.io/downloads.html).  You will need your API token.

    ```sh
    export TF_VAR_DIGITALOCEAN_TOKEN=...
    terraform plan -var-file=../../../variables/${NUBLAR_VARS} -out tfplan
    ```

#### Terraform apply
-   If the plan output looks safe, apply it

    ```sh
    terraform apply tfplan
    ```

-   Delete the old plan, *do not use it again*

    ```sh
    rm tfplan
    ```

## Step 5 - login to your droplet

-   Use Terraform to lookup the ip address

    ```sh
    terraform show

    ...
    ipv4_address = 198.199...
    ...
    ```

-   The default ssh name is `root` (see variables file).  You can now login with your DO ssh private key.

    -   `ssh -i ~/.ssh/do_private_key {{ do_ssh_username }}@{{ droplet_ip_address }}`


-   The app will now answer at the new droplet ip and port configured in `nublar.json`.

    -   `http://{{ droplet_ip_address }}:{{ nublar_port }}/`


-   A firewall has been configured to allow access from anywhere to `22` and `nublar_port`.  This firewall also allows the droplet to reach out to the web and make dns lookups.

## Step 6 - destroy the droplet

-   This will delete your droplet:

    ```sh
    terraform destroy -var-file=../../../variables/${NUBLAR_VARS}
    ```

## Step 8 - do it all again, and again

-   Add a new endpoint to the [Flask](http://flask.pocoo.org/docs/0.12/) app
-   Bump the version in setup.py
-   Repeat steps 2-6

# Conclusion

Congratulations, you are now equipped to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application repeatably to [Digital Ocean](https://www.digitalocean.com/products/compute/).

Now is a great time to try editing the [Ansible](http://docs.ansible.com/ansible/latest/index.html), [Packer](https://www.packer.io/downloads.html), and [Terraform](https://www.terraform.io/downloads.html) configuration to teach yourself a bit more about these tools.
