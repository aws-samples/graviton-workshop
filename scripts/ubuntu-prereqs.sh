sudo systemctl stop apt-daily.timer
sudo apt-get update
sudo apt-get install -y jq gettext bash-completion moreutils postgresql-client-14 postgresql-client-common 
curl -sSL -o /tmp/kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.29.0/2024-01-04/bin/linux/amd64/kubectl
chmod +x /tmp/kubectl
sudo mv /tmp/kubectl /usr/local/bin/kubectl
pip3 install --upgrade awscli 
hash -r
export TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
export AWS_REGION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bash_profile
echo "export AWS_REGION=${AWS_REGION}" | tee -a ~/.bash_profile
aws configure set default.region ${AWS_REGION}
aws configure set default.account ${ACCOUNT_ID}
aws configure get default.region
aws configure get default.account
aws iam get-role --role-name "AWSServiceRoleForElasticLoadBalancing" || aws iam create-service-linked-role --aws-service-name "elasticloadbalancing.amazonaws.com"
aws iam get-role --role-name "AWSServiceRoleForAmazonOpenSearchService" || aws iam create-service-linked-role --aws-service-name "opensearchservice.amazonaws.com"
sudo systemctl start apt-daily.timer
cd ~/environment/graviton-workshop && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
npm -g uninstall cdk &&  npm install -g aws-cdk@2.1029
cdk bootstrap
cdk synth
