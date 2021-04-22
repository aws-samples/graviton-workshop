This project is designed to help you deploy services such as EKS, ECS, RDS, and EMR on Graviton2 instances.
All the labs use AWS CDK for initial deployment and utilize a dedicated VPC.

Currently covered scenarios include :

* EKS cluster with multi-architecture (x86-64 and arm64) nodegroups
* ECS cluster with sample task and service running on Graviton2 instance type
* CI pipeline for multi-architecture docker container images using CodePipeline, CodeBuild, CodeCommit, and ECR (with docker manifests)
* CI pipeline for running .Net Core 5 on Amazon EKS cluster 
* RDS migration scenario from MySQl 8 on m5 instance type to MySQL on m6g instance type
* RDS migration scenario from MySQl 5 on m5 instance type ->  in-place major version upgrade  MySQL 8 ->  to in-place instance change to m6g instance type
* EMR cluster with sample ETL Spark job running on Graviton2 instance type

