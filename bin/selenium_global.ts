#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SeleniumGlobalStack } from '../lib/selenium_global-stack';
import { SeleniumGlobalPipeline } from '../lib/selenium_global-pipeline';

const app = new cdk.App();

// List of all AWS regions
// const regions = [
//   'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
//   'af-south-1', 'ap-east-1', 'ap-south-2', 'ap-southeast-3',
//   'ap-south-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-southeast-1',
//   'ap-southeast-2', 'ap-northeast-1', 'ca-central-1', 'eu-central-1', 'eu-west-1', 'eu-west-2', 
//   'eu-south-1', 'eu-west-3', 'eu-south-2', 'eu-north-1', 'me-central-1', 'sa-east-1'
// ];

// Account ID
const account = '281318412783';

// Iterate through each region and deploy the stack
new SeleniumGlobalPipeline(app, `SeleniumGlobalPipeline`, {
  env: { account: account, region: 'us-east-1' }
});
