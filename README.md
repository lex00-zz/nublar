# nublar

Repeatable [Flask](http://flask.pocoo.org/) deployments to [Digital Ocean](https://www.digitalocean.com/products/compute/) from your desktop.

## project name

[Wiktionary definition of nublar](https://en.wiktionary.org/wiki/nublar):
```
Verb
nublar (first-person singular present indicative nublo, past participle nublado)
-   (intransitive) to become cloudy
```

## overview

nublar provides a [Vagrant](https://www.vagrantup.com/intro/index.html) environment equipped for:
-   machine image creation with [Packer](https://www.packer.io/intro/index.html)
-   configuration management with [Ansible](https://www.ansible.com/configuration-management)
-   infrastructure management with [Terraform](https://www.terraform.io/intro/index.html)

## installation

-   [Install Vagrant](https://www.vagrantup.com/downloads.html)
-   Install nublar from PyPI
    ```python
    pip install nublar
    ```

## running nublar
Nublar is designed to be run from within your projects root folder.

```python
python -m nublar
```

This will create the following files:

```
nublar
├── ansible
├── packer
├── terraform
└── Vagrantfile
```
