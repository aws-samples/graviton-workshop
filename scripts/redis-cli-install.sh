#!/bin/bash

cd /home/ec2-user/
amazon-linux-extras install epel -y
yum install gcc jemalloc-devel openssl-devel tcl tcl-devel -y
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make BUILD_TLS=yes
