# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3

import aws_cdk as cdk
from graviton.rds_graviton.rds_mysql_5 import CdkRds5Stack
from graviton.rds_graviton.rds_mysql_8 import CdkRds8Stack
from graviton.rds_graviton.rds_restore import CdkRdsRestoreStack
from graviton.vpc_base.vpc import CdkVpcStack
from graviton.cs_graviton.eks_graviton import CdkEksStack
from graviton.cs_graviton.ecs_graviton import CdkEcsStack
from graviton.cs_graviton.pipeline_graviton import CdkPipelineStack
from graviton.cs_graviton.pipeline_netcore_graviton import CdkPipelineDotNetStack
from graviton.opensearch_graviton.open_search import CdkOpenSearchStack
from graviton.perf_graviton.perf import CdkPerfStack
from graviton.ec2_graviton.ec2 import CdkEC2Stack
from graviton.aurora_graviton.aurora import CdkAuroraStack


class GravitonID(cdk.App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.stack_name = "GravitonID"
        self.base_module = CdkVpcStack(self, self.stack_name + "-base")
        self.rds_5_module = CdkRds5Stack(
            self, self.stack_name + "-rds-5", self.base_module.vpc
        )
        self.rds_8_module = CdkRds8Stack(
            self, self.stack_name + "-rds-8", self.base_module.vpc
        )
        self.restore_module = CdkRdsRestoreStack(
            self, self.stack_name + "-rds-restore", self.base_module.vpc
        )
        self.eks_module = CdkEksStack(
            self, self.stack_name + "-eks", self.base_module.vpc
        )
        self.ecs_module = CdkEcsStack(
            self, self.stack_name + "-ecs", self.base_module.vpc
        )
        self.pipeline_module = CdkPipelineStack(
            self, self.stack_name + "-pipeline", self.base_module.vpc
        )
        self.pipeline_dotnet_module = CdkPipelineDotNetStack(
            self, self.stack_name + "-pipeline-dotnet", self.base_module.vpc
        )
        #            self.emr_module = CdkEmrStack(self, self.stack_name + "-emr", self.base_module.vpc)
        self.es_module = CdkOpenSearchStack(
            self, self.stack_name + "-os", self.base_module.vpc
        )
        self.perf_module = CdkPerfStack(
            self, self.stack_name + "-perf", self.base_module.vpc
        )
        self.ec2_module = CdkEC2Stack(
            self, self.stack_name + "-ec2", self.base_module.vpc
        )
        self.ec2_module = CdkAuroraStack(
            self, self.stack_name + "-aurora", self.base_module.vpc
        )


if __name__ == "__main__":
    app = GravitonID()
    app.synth()
