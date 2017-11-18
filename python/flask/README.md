# How to deploy Flask apps repeatably to Digital Ocean with Packer, Ansible, and Terraform.

## Introduction

There are many ways to deploy your git repository to the cloud.  Most of them do all the orchestration for you behind the scenes, and this is often exactly what people want.

Here are a few examples:
-   [Heroku](https://www.heroku.com/)
-   [AWS ECS](https://aws.amazon.com/ecs/)
-   [GKE](https://cloud.google.com/container-engine/)

This tutorial provides a local environment to orchestrate a production deployment of your [Flask](http://flask.pocoo.org/docs/0.12/) application, giving you complete control over every step of the process.  All the code is ready to use, and ready for you to customize.

This repository is broken down into two parts:

-   A minimal [Flask](http://flask.pocoo.org/docs/0.12/) example
    -   Everything except for the `nublar` folder
-   Code to package and deploy the [Flask](http://flask.pocoo.org/docs/0.12/) example
    -   The `nublar` folder only

## Goals

-   Deploy a [Flask](http://flask.pocoo.org/docs/0.12/) app to a local vm using [Vagrant](https://www.vagrant.io/downloads.html) and [Ansible](http://docs.ansible.com/ansible/latest/index.html)
-   Build a machine image using [Packer](https://www.packer.io/downloads.html) and [Ansible](http://docs.ansible.com/ansible/latest/index.html)
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

## Step 1 - setup Flask development environment
You can skip this step if you just want to see how the deploy works.

If you would like to test any changes to the [Flask](http://flask.pocoo.org/docs/0.12/) code, perform the following steps.

-   Install [pyenv](https://github.com/pyenv/pyenv)

    Read the docs, *be sure your profile inits pyenv*!

-   Install [pipenv](https://github.com/kennethreitz/pipenv) using the provided convenience script

    `./pipenv_setup.sh`

-   Start the pipenv shell

    `pipenv shell`

-   Run the tests

    `$ python setup.py test`

-   Run [Flask](http://flask.pocoo.org/docs/0.12/) from pipenv shell

    `$ ./runserver.sh`

## Step 2 - create the variables file

All the tools in the `nublar` folder will use the same variables file.

-   Copy the example file to a new file

    ```
    nublar$ cp variables/nublar.json.example variables/nublar.json
    ```


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
    -   service port (default = 80)
-   `app_health_ep`
    -   Ansible will check this for a 200 return code as a final step (default = /)
-   `uwsgi_process_count`
    -   number of uwsgi processes (default = 10)
-   `do_template_image`
    -   Digital Ocean image used by  [Packer](https://www.packer.io/downloads.html) (default = ubuntu-14-04-x64)
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

## Step 3 - test Ansible in Vagrant

There is a `Vagrantfile` in `nublar/config_management/ansible` which is configured to automatically install the [flask-uwsgi-nginx](https://galaxy.ansible.com/lex00/flask-uwsgi-nginx/) role.

Follow these steps in the `nublar/config_management/ansible` folder:

-   Bring up [Vagrant](https://www.vagrant.io/downloads.html) (this will run [Ansible](http://docs.ansible.com/ansible/latest/index.html) the first time)

    ```sh
    nublar/config_management/ansible$ vagrant up
    ```

-   Run [Ansible](http://docs.ansible.com/ansible/latest/index.html)

    ```sh
    nublar/config_management/ansible$ vagrant provision
    ```

## Step 4 - build the machine image

[Packer](https://www.packer.io/downloads.html) will be used to provision a new droplet, install the app, and then take a snapshot which can be used in the next step.

`packer.json` is configured to automatically install the  [flask-uwsgi-nginx](https://galaxy.ansible.com/lex00/flask-uwsgi-nginx/) role.

WARNING: After testing with Vagrant, the galaxy role is  supposed to be cleaned up.  However, if it is present, Packer will try to upload it.  To clean it up:

-   `rm -fr config_management/ansible/roles/*`

Follow these steps in the `nublar` folder:

-   Run the [Packer](https://www.packer.io/downloads.html) build, you will need your API token:

    ```sh
    nublar$ export DIGITALOCEAN_API_TOKEN=...
    nublar$ packer build -var-file=variables/nublar.json imaging/packer/digitalocean/packer.json
    ```

-   Get the new snapshot ID from the output (or your Digital Ocean web panel):

    ```
    ==> Builds finished. The artifacts of successful builds are:
    --> digitalocean: A snapshot was created: 'nublar-15...' (ID: 29...) in regions ''
    ```

## Step 5 - deploy the machine image to a new droplet

Now that we have a snapshot ID, we can use it to create a new droplet.

If you have a domain setup with Digital Ocean, you can use the [digitalocean_domain](https://www.terraform.io/docs/providers/do/r/domain.html) and [digitalocean_record](https://www.terraform.io/docs/providers/do/r/record.html) resources to point at the new droplet ip.  This is not covered here, although Nginx is ready to answer to the domain as configured with `app_domain`.

Follow these steps in the `infrastructure_management/terraform/digitalocean` folder:

#### Terraform setup
-   Initialize [Terraform](https://www.terraform.io/downloads.html) (first time only):

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform init
    ```

-   Edit `variables/nublar.json`

    -   `do_image`
        -   set this to the new snapshot id

    -   `do_ssh_keys`
        -   an ssh key id from your DO account


[Tugboat](https://github.com/petems/tugboat) can help you lookup these ssh key and snapshot ids.

#### Terraform plan
-   Try to plan with [Terraform](https://www.terraform.io/downloads.html).  You will need your API token.

    ```sh
    $ export TF_VAR_DIGITALOCEAN_TOKEN=...
    infrastructure_management/terraform/digitalocean$ terraform plan -var-file ../../../variables/nublar.json -out tfplan
    ```

#### Terraform apply
-   If the plan output looks safe, apply it

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform apply tfplan
    ```

-   Delete the old plan, *do not use it again*

    ```sh
    infrastructure_management/terraform/digitalocean$ rm tfplan
    ```

## Step 6 - login to your droplet

-   Use Terraform to lookup the ip address

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform show

    ...
    ipv4_address = 198.199...
    ...
    ```

-   The default ssh name is `root` (see variables file).  You can now login with your DO ssh private key.

    -   `ssh -i ~/.ssh/do_private_key {{ do_ssh_username }}@{droplet_ip_address}`


-   The app will now answer at the new droplet ip and port configured in `nublar.json`.

    -   `http://{droplet_ip_address}:{nublar_port}/`


-   A firewall has been configured to allow access from `22` and `{nublar_port}`

## Step 7 - destroy the droplet

-   This will delete your droplet:

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform destroy -var-file ../../../variables/nublar.json
    ```

## Step 8 - do it all again, and again

-   Add a new endpoint to the [Flask](http://flask.pocoo.org/docs/0.12/) app
-   Bump the version in setup.py
-   Repeat steps 3-7

# Conclusion

Congratulations, you are now equipped to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application repeatably to [Digital Ocean](https://www.digitalocean.com/products/compute/).

Now is a great time to try editing the [Ansible](http://docs.ansible.com/ansible/latest/index.html), [Packer](https://www.packer.io/downloads.html), and [Terraform](https://www.terraform.io/downloads.html) configuration to teach yourself a bit more about these tools.
