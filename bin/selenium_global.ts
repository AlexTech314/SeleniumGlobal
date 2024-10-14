#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SeleniumGlobalPipeline } from '../lib/selenium_global-pipeline';

const app = new cdk.App();

// Account ID
export const ACCOUNT = '281318412783';
export const REGIONS = [
  'us-east-1', 'sa-east-1'
]

// Iterate through each region and deploy the stack
new SeleniumGlobalPipeline(app, `SeleniumGlobalPipeline`, {
  env: { account: ACCOUNT, region: 'us-east-1' }
});
