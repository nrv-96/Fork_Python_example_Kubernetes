#!/bin/bash

# This script exists, because there's no good way to get the current target account into the configuration files otherwise.

# Preflight checks
# Expected Variables;

required_env=(
    AWS_DEFAULT_REGION
    GIT_BRANCH
    DEPLOY_ENVIRONMENT
)

for i in ${required_env[@]}; do
    if [[ ${!i} == "" ]]; then
        echo "Missing Env Var $i"
        exit 1
    fi
done

if [ -z "$DESIRED_DEPLOYMENT" ]; then
    DESIRED_DEPLOYMENT=00-main
fi

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

# Cfngin Bucket
for file in $(find . | grep "${deploy_env}.env$" ); do
    if grep -E "cfngin_bucket_name|stacker_bucket_name" $file; then
        echo "cfngin_bucket_name or stacker_bucket_name is already present in the env file. Skipping update of env file."
    else
        echo "stacker_bucket_name: swa-devops-${target_account_id}-${AWS_DEFAULT_REGION}" >> $file
        echo "cfngin_bucket_name: swa-devops-${target_account_id}-${AWS_DEFAULT_REGION}" >> $file
        echo "namespace: ${branch_name}" >> $file
        echo "region: ${AWS_DEFAULT_REGION}" >> $file
        echo "createDate: remove me" >> $file
    fi
done

# Serverless Bucket
for file in $(find . | grep "config-${deploy_env}.yml$" ); do
    if fgrep "serverless_bucket_name" $file; then
        echo "serverless_bucket_name is already present. Skipping update of config file."
    else
        echo "serverless_bucket_name: swa-devops-${target_account_id}-${AWS_DEFAULT_REGION}" >> $file
        echo "namespace: ${branch_name}" >> $file
        echo "region: ${AWS_DEFAULT_REGION}" >> $file
        echo "createDate: remove me" >> $file        
    fi
done

# Link all globally installed node modules to local
currentdir=`pwd`
for D in `find . -maxdepth 1 -type d`; do
    cd $D
    if [ -f "serverless.yml" ]; then
        npm link `npm list -g --depth=0 --json=true 2>/dev/null | jq '.dependencies | keys[] | select(. != "npm") | select(. != "serverless") | @sh' | sed -e "s/['\"]//g"`
    fi
    cd $currentdir
done

# Update runway.yml for correct region targeting
if [ "$AWS_DEFAULT_REGION" != "us-east-1" ]; then
    sed -i "s/us-east-1/${AWS_DEFAULT_REGION}/" runway.yml
fi
echo "Runway Version"
runway --version

# Sanity Check
runway preflight

# Export env vars to child shell
for i in $(env); do
    export ${i}
done

# Run CMD
exec "$@" --tag $DESIRED_DEPLOYMENT