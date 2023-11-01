#!/usr/bin/env bash
export AWS_PROFILE="default"
export DEPLOY_AWS_REGIONS=('us-east-1')
npm install

npx cdk synth 

for region in "${DEPLOY_AWS_REGIONS[@]}"
do
  export CDK_DEPLOY_REGION=$region
  npx cdk bootstrap --profile $AWS_PROFILE
  npx cdk synth --profile $AWS_PROFILE
  # npx cdk deploy --profile $AWS_PROFILE
done