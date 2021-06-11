#!/bin/bash

set -ex

# Preflight checks
# Expected Variables;

required_env=(
    GIT_BRANCH
)

for i in ${required_env[@]}; do
    if [[ ${!i} == "" ]]; then
        echo "Missing Env Var $i"
        exit 1
    fi
done

# Make sure AWS credentials are valid
# Get Account Id
target_account_id=$(aws sts get-caller-identity --output text --query 'Account')

if [[ ${target_account_id} == "" ]]; then
    echo "Missing Aws Credentials"
    exit 1
fi

# Get Branch Name
branch_name=$GIT_BRANCH

for deploy_env in $(cat /work/runway/test_targets.txt); do
    env_name=$(echo $deploy_env | sed 's/-.*//g')
    region=$(echo $deploy_env | sed 's/^.*-//g')
    for file in $(find . | grep "${env_name}-${region}.env$" ); do
        echo "stacker_bucket_name: swa-devops-${target_account_id}-${region}" >> $file
        echo "cfngin_bucket_name: swa-devops-${target_account_id}-${region}" >> $file
        echo "namespace: ${branch_name}" >> $file
    done
    # Preflight check all the potential target environments.
    DEPLOY_ENVIRONMENT=${deploy_env} runway preflight
done
