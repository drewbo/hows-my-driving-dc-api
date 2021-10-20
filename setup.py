"""Setup for hows-my-driving-dc-api"""

from setuptools import find_packages, setup

# Runtime requirements.
inst_reqs = [
    "fastapi",
    "pyppeteer",
    "pyppeteer_stealth",
    "boto3",
]

extra_reqs = {
    "dev": ["pytest"],
    "server": ["uvicorn"],
    "deploy": [
        "docker",
        "aws-cdk.core==1.128.0",
        "aws-cdk.aws_s3==1.128.0",
        "aws-cdk.aws_iam==1.128.0",
        "aws-cdk.aws_lambda==1.128.0",
        "aws-cdk.aws_apigateway==1.128.0",
    ],
    "test": ["pytest"],
}

setup(
    name="hows-my-driving-dc-api",
    version="0.1.0",
    python_requires=">=3",
    description=u"""Find dangerous driving in DC""",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
