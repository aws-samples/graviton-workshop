### Gathering VPC IDs
#export DefaultVpcId=$(aws ec2 describe-vpcs --query "Vpcs[].VpcId" --output json | jq -r '.[0]')
export DefaultVpcId=$(aws ec2 describe-vpcs --filter "Name=isDefault, Values=true" --query "Vpcs[].VpcId" --output json  | jq -r '.[0]')
export GravitonVpcId=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=GravitonID-base/BaseVPC" --query "Vpcs[].VpcId" --output json  | jq -r '.[0]')
echo $DefaultVpcId
echo $GravitonVpcId

### Route Table VPC IDs
export DefaultRouteTableID=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=${DefaultVpcId}" --query 'RouteTables[?Associations[0].Main == `true`]' --output json | jq -r '.[0].RouteTableId')
export GravitonRouteTableID=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=${GravitonVpcId}" --query 'RouteTables[?Associations[0].Main == `true`]'  --output json| jq -r '.[0].RouteTableId')
echo $DefaultRouteTableID
echo $GravitonRouteTableID

### VPC CIDRs
export DefaultRouteCidr=$(aws ec2 describe-vpcs --filters "Name=vpc-id,Values=${DefaultVpcId}" --query "Vpcs[].CidrBlock" --output json | jq -r '.[0]')
echo $DefaultRouteCidr
echo $GravitonRouteCidr

#### Graviton VPC CIDR / Source VPC route table config
aws ec2 delete-route --route-table-id "$DefaultRouteTableID" --destination-cidr-block "$GravitonRouteCidr"
aws ec2 delete-route --route-table-id "$GravitonRouteTableID" --destination-cidr-block "$DefaultRouteCidr"

#### Add  routes to Graviton Private Subnets
export GravitonPrivate1RouteTableID=$(aws ec2 describe-route-tables --filters 'Name=tag:Name,Values=GravitonID-base/BaseVPC/PrivateSubnet1' --query 'RouteTables[].Associations[].RouteTableId' --output json| jq -r '.[0]')
export GravitonPrivate2RouteTableID=$(aws ec2 describe-route-tables --filters 'Name=tag:Name,Values=GravitonID-base/BaseVPC/PrivateSubnet2' --query 'RouteTables[].Associations[].RouteTableId' --output json| jq -r '.[0]')

aws ec2 delete-route --route-table-id "$GravitonPrivate1RouteTableID" --destination-cidr-block "$DefaultRouteCidr" 
aws ec2 delete-route --route-table-id "$GravitonPrivate2RouteTableID" --destination-cidr-block "$DefaultRouteCidr" 

### Create the VPC peering and accept the request
VpcPeeringId=$(aws ec2 describe-vpc-peering-connections --filters 'Name=tag:Name,Values=GravitonID-VPCPeering' --query 'VpcPeeringConnections[*].VpcPeeringConnectionId'  --output json | jq -r '.[0]')

aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $VpcPeeringId
