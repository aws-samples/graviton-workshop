# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="graviton",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "graviton2"},
    packages=setuptools.find_packages(where="graviton2"),

    install_requires=[
        "aws-cdk.core==1.99.0",
        "aws-cdk.aws-eks==1.99.0",
        "aws-cdk.aws-ec2==1.99.0",
        "aws-cdk.aws-cloudtrail==1.99.0",
        "aws-cdk.aws-codebuild==1.99.0",
        "aws-cdk.aws-codecommit==1.99.0",
        "aws-cdk.aws-codepipeline==1.99.0",
        "aws-cdk.aws-codepipeline-actions==1.99.0",
        "aws-cdk.aws-ec2==1.99.0",
        "aws-cdk.aws-ecr==1.99.0",
        "aws-cdk.aws-ecs==1.99.0",
        "aws-cdk.aws-eks==1.99.0",
        "aws-cdk.aws-elasticloadbalancingv2==1.99.0",
        "aws-cdk.aws-elasticsearch==1.99.0",
        "aws-cdk.aws-emr==1.99.0",
        "aws-cdk.aws-events==1.99.0",
        "aws-cdk.aws-events-targets==1.99.0",
        "aws-cdk.aws-iam==1.99.0",
        "aws-cdk.aws-lambda==1.99.0",
        "aws-cdk.aws-lambda-python==1.99.0",
        "aws-cdk.aws-rds==1.99.0",
        "aws-cdk.aws-ssm==1.99.0",
        "boto3",
        "awscli",

        # Packages specifically required for the Elasticsearch module
        "elasticsearch",
        "requests",
        "requests-aws4auth",
        "Faker",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
