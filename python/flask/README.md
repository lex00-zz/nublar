# How to deploy Flask apps repeatably to Digital Ocean with Packer, Ansible, and Terraform.

## Introduction

There are many ways to deploy your git repository to the cloud.  Most of them do all the orchestration for you behind the scenes, and this is often exactly what people want.

Here are a few examples:
-   [Heroku](https://www.heroku.com/)
-   [AWS ECS](https://aws.amazon.com/ecs/)
-   [GKE](https://cloud.google.com/container-engine/)

This tutorial provides a local environment to orchestrate a production deployment of your Flask application, giving you complete control over every step of the process.  All the code is ready to use, and ready for you to customize.

This repository is broken down into two parts:

-   1) A minimal Flask example
    -   Everything except for the `nublar` folder
-   2) Code to package and deploy the Flask example
-   -   The `nublar` folder only

## Goals

-   Deploy a Flask app to a local vm using [Vagrant](https://www.vagrant.io/downloads.html) and [Ansible](http://docs.ansible.com/ansible/latest/index.html)
-   Build a machine image using [Packer](https://www.packer.io/downloads.html) and [Ansible](http://docs.ansible.com/ansible/latest/index.html)
-   Deploy the image to a [Digital Ocean](https://www.digitalocean.com/products/compute/) droplet with [Terraform](https://www.terraform.io/downloads.html)
-   Rinse and repeat

## Prerequisites

-   Install [Vagrant](https://www.vagrant.io/downloads.html) > 2.0
-   Install  [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
-   Install [Packer](https://www.packer.io/downloads.html)
-   Install [Terraform](https://www.terraform.io/downloads.html)
-   [Setup an SSH key in your Digital Ocean account](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets)
-   [Setup an API key in your Digital Ocean account](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2)

## Step 1 - setup Flask development environment
You can skip this step if you just want to see how the deploy works.

If you would like to test any changes to the Flask code, perform the following steps.

-   Install [pyenv](https://github.com/pyenv/pyenv)

    Read the docs, *be sure your profile inits pyenv*!

-   Install [pipenv](https://github.com/kennethreitz/pipenv) using the provided convenience script

    `./pipenv_setup.sh`

-   Start the pipenv shell

    `pipenv shell`

-   Run Flask from pipenv shell

    `$ ./runserver.sh`

## Step 2 - create the variables file

All the tools in the `nublar` folder will use the same variables file.

-   Copy the example file to a new file

    ```
    nublar$ cp variables/nublar.json.example variables/nublar.json
    ```

-   `do_ssh_username` (default = root)

     this key designates the username to login with.

## Step 3 - test the Ansible role with Vagrant

This repository comes with an Ansible role called `nublar-ansible-flask`.  It has a separate [README](https://github.com/lex00/nublar/tree/master/python/flask/nublar/config_management/ansible/roles/nublar-ansible-flask).

The Flask app will be deployed using [Uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) and [Nginx](https://nginx.org/en/docs/).

There is a `Vagrantfile` in `nublar/config_management/ansible` which has the Ansible provisioner configured to execute the playbook `nublar.yml`, which will in turn execute the `nublar-ansible-flask` role.

Follow these steps in the `nublar/config_management/ansible` folder:

-   Bring up Vagrant (this will run ansible the first time)

    ```sh
    nublar/config_management/ansible$ vagrant up
    ```

-   Run ansible

    ```sh
    nublar/config_management/ansible$ vagrant provision
    ```

## Step 4 - build the machine image

Packer will be used to provision a new droplet, install the app, and then take a snapshot which can be used in the next step.

Follow these steps in the `nublar` folder:

-   Run the Packer build, you will need your API token:

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

-   Initialize Terraform (first time only):

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform init
    ```

-   Edit `variables/nublar.json`

    -   `do_image` is your desired snapshot id.

    -   `do_ssh_keys` is a comma delimited list of ssh keys ids from your DO account.

    -    [Tugboat](https://github.com/petems/tugboat) can help you lookup these ids easily.

-   Try to plan with Terraform.  You will need your API token.

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

-   The default ssh name is `root` (see variables file).  You should now be able to login with your DO ssh key.

## Step 6 - destroy the droplet

-   This will delete your droplet:

    ```sh
    nublar/terraform$ terraform destroy -var-file ../../../variables/nublar.json
    ```

## Step 7 - do it all again, and again

-   Add a new endpoint to the Flask app
-   Bump the version in setup.py
-   Repeat steps 3-6

# Conclusion

Congratulations, you are now equipped to deploy a Flask application repeatably to digital ocean.

Now is a great time to try editing the Ansible, Packer, and Terraform configuration to teach yourself a bit more about these tools.
