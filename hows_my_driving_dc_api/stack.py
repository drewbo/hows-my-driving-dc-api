"""cdk stack from hows-my-driving-dc-api"""
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk

BUCKET = "hows-my-driving-dc-bucket"


class HowsMyDrivingDcApiStack(cdk.Stack):
    """HowsMyDrivingDcApiStack Class"""

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        """init"""
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket.from_bucket_name(self, f"{id}-bucket", BUCKET)

        s3_access_policy = iam.PolicyStatement(
            actions=["s3:*"],
            resources=[
                bucket.bucket_arn,
                f"{bucket.bucket_arn}/*",
            ],
        )

        tesseract_layer = aws_lambda.LayerVersion(
            self,
            "tesseract-layer",
            code=aws_lambda.Code.from_asset("./layer"),
            description="Tesseract Layer",
        )

        lambda_function = aws_lambda.Function(
            self,
            f"{id}-lambda",
            code=aws_lambda.Code.from_asset(
                "./",
                bundling=dict(
                    image=cdk.BundlingDockerImage.from_registry(
                        "lambci/lambda:build-python3.6"
                    ),
                    command=[
                        "/bin/bash",
                        "-c",
                        " && ".join(
                            [
                                "pip install -r requirements.txt -t /asset-output/",
                                "cp lambda/handler.py /asset-output",
                            ]
                        ),
                    ],
                ),
            ),
            handler="handler.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_6,
            layers=[tesseract_layer],
            memory_size=2048,
            reserved_concurrent_executions=5,
            timeout=cdk.Duration.seconds(30),
            environment=dict(BUCKET=BUCKET),
        )
        lambda_function.add_to_role_policy(s3_access_policy)

        apigw.LambdaRestApi(self, f"{id}-api", handler=lambda_function)
