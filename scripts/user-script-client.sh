# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0
#!/bin/bash


# Update the system
sudo yum update -y

sudo yum install git -y
sudo yum groupinstall "Development Tools" -y
sudo yum install openssl-devel -y
git clone https://github.com/giltene/wrk2.git
make -C wrk2/
sudo cp wrk2/wrk /usr/local/bin/wrk

# Get latest python 3.8.x and make it the default for python3 (AL2 comes with python 3.7.x)
sudo amazon-linux-extras install -y python3.8
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# Install pip
python3 -m ensurepip --upgrade

# Install dependencies for plotting results
python3 -m pip install matplotlib
