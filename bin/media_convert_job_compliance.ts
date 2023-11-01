#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { MediaConvertJobComplianceStack } from '../lib/media_convert_job_compliance-stack';
import { AwsSolutionsChecks } from 'cdk-nag';
import { Aspects } from 'aws-cdk-lib';

const app = new cdk.App();
new MediaConvertJobComplianceStack(app, 'MediaConvertJobComplianceStack', {
  description: "Sample recipe to check compliance on video files (uksb-1tsci8mhd)",
  terminationProtection: true,
  env: { account: process.env.CDK_DEPLOY_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEPLOY_REGION || process.env.CDK_DEFAULT_REGION },
});

Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true }))