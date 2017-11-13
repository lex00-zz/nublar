This is a one line [Flask](http://flask.pocoo.org/) application.

The example deploys it to [Digital Ocean](https://www.digitalocean.com/products/compute/) using [Ansible](http://docs.ansible.com/ansible/latest/index.html)

## project requirements

-   `.python-version` file

    Your repository needs this file to contain the version of python you are targeting.

-   Install the latest [Packer](https://www.packer.io/downloads.html)

-   Install the latest [Terraform](https://www.terraform.io/downloads.html)

## variables file

-   Copy the example file to a new file

    ```
    nublar$ cp variables/nublar.json.example variables/nublar.json
    ```

-   `do_ssh_username`

     this key designates the username to login with.  default=root.
     
## testing the ansible with Vagrant

When you make edits to the ansible, you can test it locally with Vagrant.

-   Install the latest [Vagrant](https://www.vagrant.io/downloads.html)

-   Bring up the vagrant (this will run ansible the first time)

    ```sh
    nublar/config_management/ansible$ vagrant up
    ```

-   Run ansible

    ```sh
    nublar/config_management/ansible$ vagrant provision
    ```

## build the machine image

-   Run packer to create a new snapshot:

    ```sh
    nublar$ export DIGITALOCEAN_API_TOKEN=...
    nublar$ packer build -var-file=variables/nublar.json imaging/packer/digitalocean/packer.json
    ```

-   Get the new snapshot ID from the output (or your Digital Ocean web panel):

    ```
    ==> Builds finished. The artifacts of successful builds are:
    --> digitalocean: A snapshot was created: 'nublar-15...' (ID: 29...) in regions ''
    ```

## create the droplet

-   Initialize Terraform the first time:

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform init
    ```

-   Update the `do_image` key in `vars.tf` with your desired snapshot id.

-   Update the `do_ssh_keys` key in `vars.tf` with at least one of your ssh keys from your DO account.

-   Try to plan with terraform

    ```sh
    $ export TF_VAR_DIGITALOCEAN_TOKEN=...
    infrastructure_management/terraform/digitalocean$ terraform plan -var-file ../../../variables/nublar.json -out tfplan
    ```

-   If the plan looks ok, create the droplet

    ```sh
    infrastructure_management/terraform/digitalocean$ terraform apply tfplan
    ```

-   Cleanup the old plan, do not use it again

    ```sh
    infrastructure_management/terraform/digitalocean$ rm tfplan
    ```

-   The default ssh name is `root`.  Check packer/digitalocean.json to be sure.

## destroy the droplet

-   This will remove your droplet:

    ```sh
    nublar/terraform$ terraform destroy
    ```

## flask development
-   Install [pyenv](https://github.com/pyenv/pyenv)

    Make sure you get your shell to init properly!

-   Setup [pipenv](https://github.com/kennethreitz/pipenv) using the provided convenience script

    This is going to install a recent version of Python into your pyenv.

    `./pipenv_setup.sh`
