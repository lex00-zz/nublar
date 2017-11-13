# Nublar Ansible Flask role

This role for Ansible deploys your Flask application on Ubuntu.

It allows you to easily configure Nginx and Uwsgi.

## project requirements

-   `.python-version` file

    Your repository needs this file to contain the version of python you are targeting.  The role will install that version of python using pyenv.

## example

```yml
- hosts: all
  tasks:
  - import_role:
       name: nublar-ansible-flask
    vars:
      # python repository containing flask application
      app_repo_url: 'https://github.com/lex00/nublar'

      # if your project is in a subfolder in the repo, specify this here, otherwise set blank
      app_subfolder: 'python/flask'

      # this will go into the system service script
      app_description: 'A nublar example in Flask'

      # app folders and service name
      app_name: 'nublar'

      # system user and group will both be this value
      app_user: 'nublar'

      # domain that nginx will answer to
      app_domain: 'notarealdomain.com'

      # python module for uwsgi.ini
      app_module: 'nublar_example_python_flask'

      # python callable for uwsgi.ini
      app_callable: 'app'

      # service port
      app_port: '80'

      # health endpoint
      app_health_ep: '/'

      # number of uwsgi processes
      uwsgi_process_count: '10'
  ```
