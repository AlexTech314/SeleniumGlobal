import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { SeleniumRegionalStack } from './selenium_regional-stack';

export class SeleniumRegionalStage extends cdk.Stage {
    constructor(scope: Construct, region: string, props?: cdk.StageProps) {
        super(scope, region, props)
        const seleniumRegionalStack = new SeleniumRegionalStack(this, `${region}-SeleniumRegionalStack`)
    }
}