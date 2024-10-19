import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { LambdaIntegration, LambdaRestApi, Period, ApiKey, UsagePlan } from 'aws-cdk-lib/aws-apigateway';

export class SeleniumRegionalStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create Lambda function from Docker image
    const lambdaFunction = new DockerImageFunction(this, `${id}-SeleniumLambda`, {
      code: DockerImageCode.fromImageAsset("./src"),
      timeout: Duration.seconds(900),
      functionName: `${id}-function`,
      memorySize: 2048,
      logRetention: RetentionDays.ONE_WEEK
    });

    // Create API Gateway
    const gateway = new LambdaRestApi(this, `${id}-SeleniumGateway`, {
      handler: lambdaFunction,
      proxy: false
    });

    // Create Lambda integration
    const integration = new LambdaIntegration(lambdaFunction);

    // Create an API key
    const apiKey = gateway.addApiKey(`${id}-ApiKey`);

    // Create a Usage Plan
    const usagePlan = gateway.addUsagePlan(`${id}-UsagePlan`, {
      name: `${id}-UsagePlan`,
      throttle: {
        rateLimit: 5,
        burstLimit: 5
      },
      quota: {
        limit: 10000,
        period: Period.MONTH
      }
    });

    usagePlan.addApiKey(apiKey)

    // Associate the Usage Plan with the API Stage
    usagePlan.addApiStage({
      stage: gateway.deploymentStage
    });

    // Add POST method with API key required
    gateway.root.addMethod("POST", integration, {
      apiKeyRequired: true // Require API key
    });
  }
}
