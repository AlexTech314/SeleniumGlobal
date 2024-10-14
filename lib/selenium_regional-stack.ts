import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { LambdaIntegration, LambdaRestApi, Period } from 'aws-cdk-lib/aws-apigateway';

export class SeleniumRegionalStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const lambdaFunction = new DockerImageFunction(this, `${id}-SeleniumLambda`, {
      code: DockerImageCode.fromImageAsset("./src"),
      timeout: Duration.seconds(900),
      functionName: `${id}-function`,
      memorySize: 2048,
      logRetention: RetentionDays.ONE_WEEK
    });

    const gateway = new LambdaRestApi(this, `${id}-SeleniumGateway`, {
      handler: lambdaFunction,
      proxy: false
    });

    const integration = new LambdaIntegration(lambdaFunction);
    gateway.root.addMethod("GET", integration, {
      apiKeyRequired: false
    });
  }
}
