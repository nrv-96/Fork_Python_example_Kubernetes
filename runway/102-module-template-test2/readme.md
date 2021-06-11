# SWA Cloud Common Platform Module Template

The `template` module should be cloned when creating a new module.

### Purpose
The purpose of this repository is to give a starting point for create a new module.

It comes with the following placeholders:

* stacker hooks - for writing custom scripts
* stacker lookups - for writing custom lookups
* stacker - for using cloudformation templates
* integration - for testing full deployments with dependencies
* lambdas - for adding lambda functions which will be automatically uploaded to s3
* test - for creating unit tests on hooks and lookups
* .gitignore - for containing all files that should be commonly ignored
* Dockerfile - for packaging the stacker code
* Jenkinsfile - for building the repository
* local-setup.sh - for setting up each repository with common files across all modules
* setup.py - for installing dependencies onto the docker image
* stacker.yaml - for deploying cloudformation and running hooks / lookups

### Benefits
Cloning this repo will give developers a solid foundation for creating an AWS SWA approved module.

For more information, visit https://confluence-tools.swacorp.com/display/EC/Contribution+Guide.

