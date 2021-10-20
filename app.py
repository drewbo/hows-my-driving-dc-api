#!/usr/bin/env python3
"""Full CDK application for Hows My Driving DC API"""

from aws_cdk import core as cdk

from hows_my_driving_dc_api.stack import HowsMyDrivingDcApiStack

app = cdk.App()
HowsMyDrivingDcApiStack(app, "HowsMyDrivingDcApiStack")

app.synth()
