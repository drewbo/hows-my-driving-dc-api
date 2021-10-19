
# How's My Driving DC API

This API is intended to serve [this Twitter bot](https://github.com/dschep/hows-my-driving-dc) and similar downstream services. It is deployed on AWS via CDK.


## Development

TODO: virtualenv notes

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
