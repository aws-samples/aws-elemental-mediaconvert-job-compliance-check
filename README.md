# AWS Elemental MediaConvert Complaince Checker
This is a reference implementation on how you could implement compliance checks on transcoding jobs submitted to MediaConvert and report them using CloudWatch metrics.

## Architecture
![Compliance Check Workflow](/images/workflow.png)

## Pre-requisites

1. Install [CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
1. Install [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

## Steps to build

1. Clone this repository and change into `cdk` directory.
1. Set below environment variables in env.sh


```
# Required: set the AWS CLI profile name
export AWS_PROFILE="default"
# Required: specify one or more AWS region to deploy the solution. Use ' ' (space) as delimiter.
export DEPLOY_AWS_REGIONS='us-east-1 us-west-1'
```
3. Run ./deploy.sh

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

