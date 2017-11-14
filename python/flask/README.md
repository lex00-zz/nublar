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
    -   Digital Ocean image used by  [Packer](https://www.packer.io/downloads.html) (default = ubuntu-16-04-x64)
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

## Step 3 - test the Ansible role with Vagrant

This repository comes with an [Ansible](http://docs.ansible.com/ansible/latest/index.html) role called `nublar-ansible-flask`.  It has a separate [README](https://github.com/lex00/nublar/tree/master/python/flask/nublar/config_management/ansible/roles/nublar-ansible-flask).

The [Flask](http://flask.pocoo.org/docs/0.12/) app will be deployed using [Uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) and [Nginx](https://nginx.org/en/docs/).

There is a `Vagrantfile` in `nublar/config_management/ansible` which has the [Ansible](http://docs.ansible.com/ansible/latest/index.html) provisioner configured to execute the playbook `nublar.yml`, which will in turn execute the `nublar-ansible-flask` role.

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

Follow these steps in the `infrastructure_management/terraform/digitalocean` folder:

-   Initialize [Terraform](https://www.terraform.io/downloads.html) (first time only):

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform init
    ```

-   Edit `variables/nublar.json`

    -   `do_image` is your desired snapshot id.

    -   `do_ssh_keys` is a comma delimited list of ssh keys ids from your DO account.

    -    [Tugboat](https://github.com/petems/tugboat) can help you lookup these ids easily.

-   Try to plan with [Terraform](https://www.terraform.io/downloads.html).  You will need your API token.

    ```sh
    $ export TF_VAR_DIGITALOCEAN_TOKEN=...
    infrastructure_management/terraform/digitalocean$ terraform plan -var-file ../../../variables/nublar.json -out tfplan
    ```

-   If the plan looks ok, apply it

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform apply tfplan
    ```

-   Delete the old plan, *do not use it again*

    ```sh
    infrastructure_management/terraform/digitalocean$ rm tfplan
    ```

-   The default ssh name is `root` (see variables file).  You can now login with your DO ssh private key.

    -   `ssh -i ~/.ssh/private_key root@{droplet_ip_address}`


-   The app will now answer at the new droplet ip and port configured in `nublar.json`.

    -   `http://{droplet_ip_address}:{nublar_port}/`

## Step 6 - destroy the droplet

-   This will delete your droplet:

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform destroy -var-file ../../../variables/nublar.json
    ```

## Step 7 - do it all again, and again

-   Add a new endpoint to the [Flask](http://flask.pocoo.org/docs/0.12/) app
-   Bump the version in setup.py
-   Repeat steps 3-6

# Conclusion

Congratulations, you are now equipped to deploy a [Flask](http://flask.pocoo.org/docs/0.12/) application repeatably to [Digital Ocean](https://www.digitalocean.com/products/compute/).

Now is a great time to try editing the [Ansible](http://docs.ansible.com/ansible/latest/index.html), [Packer](https://www.packer.io/downloads.html), and [Terraform](https://www.terraform.io/downloads.html) configuration to teach yourself a bit more about these tools.
