import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';
import { EventbridgeToLambdaProps, EventbridgeToLambda } from '@aws-solutions-constructs/aws-eventbridge-lambda';
import { Stack } from 'aws-cdk-lib';
import * as cw from 'aws-cdk-lib/aws-cloudwatch';
import { NagSuppressions } from 'cdk-nag';

export class MediaConvertJobComplianceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    NagSuppressions.addStackSuppressions(this, [
      {
        id: 'AwsSolutions-IAM5',
        reason: 'CDK construct adds the default Lambda function policy for CloudWatch log group',
      },
    ]);
    const constructProps: EventbridgeToLambdaProps = {
      lambdaFunctionProps: {
        code: lambda.Code.fromAsset(path.join(__dirname, '../src/lambda-functions/compliance-checker/')),
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: 'lambda_function.lambda_handler',
      },
      eventRuleProps: {
        eventPattern: {
          detailType: ["AWS API Call via CloudTrail"],
          source: ["aws.mediaconvert"],
          detail: {
            eventSource: ["mediaconvert.amazonaws.com"],
            eventName: ["CreateJob"],
          }
        }
      }
    };

    let eventBridgeLambda = new EventbridgeToLambda(this, 'EMCComplianceEventLambda', constructProps);

    // 👇 Create IAM Permission Policy for TagIngestFunction
    const complianceCWStatement =
      new iam.PolicyStatement({
        resources: [`arn:aws:logs:*:${Stack.of(this).account}:log-group:/aws/lambda/emc_job_compliance_check:*`],
        actions: [
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
        ],
      });
    eventBridgeLambda.lambdaFunction.addToRolePolicy(complianceCWStatement);

    // NagSuppressions.addResourceSuppressions(eventBridgeLambda, [
    //   {
    //     id: 'AwsSolutions-IAM5',
    //     reason: 'CloudWatch Log stream is dynamically created under log group /aws/lambda/emc_job_compliance_check',
    //   },
    // ]);
    // build the CW Dashboard
    const dashboard = new cw.Dashboard(this, 'MediaConvertComplianceDashboard', {
      dashboardName: `${Stack.of(this).stackName}-${Stack.of(this).region}-Dashboard`,
    });

    dashboard.addWidgets(new cw.GraphWidget({
      title: "Non compliance count",
      liveData: true,
      view: cw.GraphWidgetView.TIME_SERIES,
      left: [new cw.Metric({
        namespace: "mediaconvert-compliant-metrics",
        metricName: "none_compliant_count",
        period: cdk.Duration.days(1),
        dimensionsMap: {
          account: Stack.of(this).account
        },
        statistic: "Sum"
      })]
    }))
  }
}
