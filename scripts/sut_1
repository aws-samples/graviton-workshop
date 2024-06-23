# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash

# Update the system
sudo yum update -y

# Prerequisites
sudo yum install git -y

# Java compiler and runtime version
sudo amazon-linux-extras enable corretto8
sudo yum clean metadata
sudo yum install java-1.8.0-amazon-corretto-devel -y
sudo yum install java-11-amazon-corretto-headless -y

# Switch between Java versions
sudo update-alternatives --set java /usr/lib/jvm/java-1.8.0-amazon-corretto.aarch64/jre/bin/java
# sudo update-alternatives --set java /usr/lib/jvm/java-11-amazon-corretto.aarch64/bin/java

# Build system
sudo yum install maven -y

# Clone repo
# git clone https://github.com/vert-x3/vertx-examples.git

# Install and configure CW agent
sudo yum install amazon-cloudwatch-agent -y
cat <<EOF >/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "metrics": {
    "metrics_collected": {
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval":30
      },
      "swap": {
        "measurement": [
          "swap_used_percent"
        ],
        "metrics_collection_interval":30
      }
    }
  }
}
EOF
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Configure Vertx access logging (optional)
# aws s3 cp s3://graviton-perf-module/SimpleREST.java \
#   vertx-examples/web-examples/src/main/java/io/vertx/example/web/rest/SimpleREST.java

# Maven build
# aws s3 cp s3://graviton-perf-module/pom-java8.xml vertx-examples/web-examples/pom.xml
# mvn package -f vertx-examples/web-examples/pom.xml

# Launch verticle
# nohup java -XX:+PerfDisableSharedMem -XX:+UseG1GC -jar vertx-examples/web-examples/target/web-examples-4.1.2-fat.jar &

# Test verticle
# curl http://localhost:8080/products
