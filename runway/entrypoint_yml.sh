#!/bin/bash

# This script exists, because there's no good way to get the current target account into the configuration files otherwise.

# Preflight checks
# Expected Variables;

required_env=(
    GIT_BRANCH
    DEPLOY_ENVIRONMENT
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
# Get Deploy Environment
deploy_env=$DEPLOY_ENVIRONMENT

echo "Runway Version"
runway --version

# Link all globally installed node modules to local
currentdir=`pwd`
for D in `find . -maxdepth 1 -type d`; do
    cd $D
    if [ -f "serverless.yml" ]; then
        npm link `npm list -g --depth=0 --json=true 2>/dev/null | jq '.dependencies | keys[] | select(. != "npm") | select(. != "serverless") | @sh' | sed -e "s/['\"]//g"`
    fi
    cd $currentdir
done

# Iterate through Deployments found in version.yml
for deployment in $(yq r version.yml Deployments[*] | sed 's/- //'); do
    region=$(yq r runway.yml deployments -j | jq --arg DESIRED_DEPLOYMENT "$deployment" '.[] | select(.name==$DESIRED_DEPLOYMENT)' | jq .regions[0] | sed 's/"//g')
	export AWS_DEFAULT_REGION=${region}

    # Cfngin Bucket
    for file in $(find . | grep "${deploy_env}.env$" ); do
        echo "stacker_bucket_name: swa-devops-${target_account_id}-${region}" >> $file
        echo "cfngin_bucket_name: swa-devops-${target_account_id}-${region}" >> $file
        echo "namespace: ${branch_name}" >> $file
        echo "region: ${region}" >> $file
        echo "createDate: remove me" >> $file
    done

    # Serverless Bucket
    for file in $(find . | grep "config-${deploy_env}.yml$" ); do
        # removing old values
        sed -i '/^serverless_bucket_name:/d' $file
        sed -i '/^namespace:/d' $file
        sed -i '/^region:/d' $file
        sed -i '/^createDate:/d' $file
        echo "serverless_bucket_name: swa-devops-${target_account_id}-${region}" >> $file
        echo "namespace: ${branch_name}" >> $file
        echo "region: ${region}" >> $file
        echo "createDate: remove me" >> $file
    done

    # Sanity Check
    runway preflight

    # Run CMD
    "$@" --tag $deployment
    [ $? -eq 0 ]  || exit 1
done