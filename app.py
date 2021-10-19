#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from hows_my_driving_dc_api.hows_my_driving_dc_api_stack import HowsMyDrivingDcApiStack

app = cdk.App()
HowsMyDrivingDcApiStack(app, "HowsMyDrivingDcApiStack")

app.synth()
