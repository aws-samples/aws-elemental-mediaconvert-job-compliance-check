# AWS Elemental MediaConvert Complaince Checker
This is a reference implementation on how you could implement compliance checks on transcoding jobs submitted to MediaConvert and report them using CloudWatch metrics.

## Architecture
![Compliance Check Workflow](/images/workflow.png)

## Pre-requisites

1. Install [Node.js](https://nodejs.org/en/download/) and [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
1. Install [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)

## Steps to build

1. Clone this repository and change into `aws-elemental-mediaconvert-job-compliance-check-main` directory.
1. Edit deploy.sh file, make changes to AWS_PROFILE and DEPLOY_AWS_REGIONS variable. Make sure AWS CLI is configured with the AWS_PROFILE name and it has the right IAM access role permission to deploy to the AWS regions specified in DEPLOY_AWS_REGIONS.
1. For each region, run `cdk bootstrap aws://<AWS Account#>/<region> --profile <profile name>`
3. Run ./deploy.sh

## Verify the solution

For each region, the solution will deploy the following:
1. A Lambda function starting with name `MediaConvertJobCompliance`
2. An EventBridge rule starting with name `MediaConvertJobCompliance`
3. CloudWatch Dashboards for each region staring with name `MediaConvertJobComplianceStack`

## Run the solution

1. In AWS Console, select the region the solution is deployed.
1. Navigate to the MediaConvert service and create a job.
1. The complaince check Lambda function will check the following conditions for the job.
    1. FileInput URL and make sure it only accept file input from S3 bucket URL
    1. Ensure output encryption setting is enabled and uses Amazon KMS
    1. Ensure output access control is enabled and not using public read policy

If any of these job configurations does not meet the Lambda function check conditions, a noncompliant customized metric will be generated and send to CloudWatch metrics. You will be able to see the noncompliant jobs count in the dashboard deployed.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

