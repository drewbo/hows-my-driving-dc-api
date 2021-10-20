"""cdk stack from hows-my-driving-dc-api"""
import os

from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda
from aws_cdk import core as cdk

import docker


class HowsMyDrivingDcApiStack(cdk.Stack):
    """HowsMyDrivingDcApiStack Class"""

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        """init"""
        super().__init__(scope, id, **kwargs)

        lambda_function = aws_lambda.Function(
            self,
            f"{id}-lambda",
            code=self.create_package("./"),
            handler="handler.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            memory_size=2048,
            reserved_concurrent_executions=5,
            timeout=cdk.Duration.seconds(30),
            environment=dict(),
        )

        apigw.LambdaRestApi(self, f"{id}-api", handler=lambda_function)

    def create_package(self, code_dir: str) -> aws_lambda.Code:
        """Build docker image and create package."""
        print("building lambda package via docker")
        client = docker.from_env()
        print("docker client up")
        client.images.build(
            path=code_dir,
            dockerfile="docker/Dockerfile",
            tag="lambda:latest",
        )
        print("docker image built")
        client.containers.run(
            image="lambda:latest",
            command="/bin/sh -c 'cp /tmp/package.zip /local/package.zip'",
            remove=True,
            volumes={os.path.abspath(code_dir): {"bind": "/local/", "mode": "rw"}},
            user=0,
        )

        return aws_lambda.Code.asset(os.path.join(code_dir, "package.zip"))