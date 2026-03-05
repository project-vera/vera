**Example 1: To create a VPC for the endpoint workflow**

The following ``create-vpc`` example creates a VPC with the specified IPv4 CIDR block that will host the VPC endpoint. ::

    aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-endpoint-vpc}]'

Output::

    {
        "Vpc": {
            "CidrBlock": "10.0.0.0/16",
            "DhcpOptionsId": "dopt-5EXAMPLE",
            "State": "pending",
            "VpcId": "vpc-1a2b3c4d",
            "OwnerId": "123456789012",
            "InstanceTenancy": "default",
            "Ipv6CidrBlockAssociationSet": [],
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-07501b79ecEXAMPLE",
                    "CidrBlock": "10.0.0.0/16",
                    "CidrBlockState": {
                        "State": "associated"
                    }
                }
            ],
            "IsDefault": false,
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-endpoint-vpc"
                }
            ]
        }
    }

**Example 2: To wait for the VPC to become available**

The following ``wait vpc-available`` example pauses and resumes running only after it confirms that the specified VPC is available. It produces no output. ::

    aws ec2 wait vpc-available \
        --vpc-ids vpc-1a2b3c4d

**Example 3: To create a gateway VPC endpoint for Amazon S3**

The following ``create-vpc-endpoint`` example creates a gateway VPC endpoint between the VPC created in Example 1 and Amazon S3, associating a route table with the endpoint. ::

    aws ec2 create-vpc-endpoint \
        --vpc-id vpc-1a2b3c4d \
        --service-name com.amazonaws.us-east-1.s3 \
        --route-table-ids rtb-11aa22bb \
        --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=my-s3-gateway-endpoint}]'

Output::

    {
        "VpcEndpoint": {
            "PolicyDocument": "{\"Version\":\"2008-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"*\",\"Resource\":\"*\"}]}",
            "VpcId": "vpc-1a2b3c4d",
            "State": "available",
            "ServiceName": "com.amazonaws.us-east-1.s3",
            "RouteTableIds": [
                "rtb-11aa22bb"
            ],
            "VpcEndpointId": "vpce-032a826a",
            "VpcEndpointType": "Gateway",
            "CreationTimestamp": "2023-09-15T10:30:00Z",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-s3-gateway-endpoint"
                }
            ],
            "OwnerId": "123456789012"
        }
    }

**Example 4: To describe the VPC endpoints**

The following ``describe-vpc-endpoints`` example retrieves details about the VPC endpoint to confirm it is in the ``available`` state. ::

    aws ec2 describe-vpc-endpoints \
        --vpc-endpoint-ids vpce-032a826a

Output::

    {
        "VpcEndpoints": [
            {
                "PolicyDocument": "{\"Version\":\"2008-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"*\",\"Resource\":\"*\"}]}",
                "VpcId": "vpc-1a2b3c4d",
                "NetworkInterfaceIds": [],
                "SubnetIds": [],
                "PrivateDnsEnabled": true,
                "State": "available",
                "ServiceName": "com.amazonaws.us-east-1.s3",
                "RouteTableIds": [
                    "rtb-11aa22bb"
                ],
                "Groups": [],
                "VpcEndpointId": "vpce-032a826a",
                "VpcEndpointType": "Gateway",
                "CreationTimestamp": "2023-09-15T10:30:00Z",
                "DnsEntries": [],
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "my-s3-gateway-endpoint"
                    }
                ],
                "OwnerId": "123456789012"
            }
        ]
    }

**Example 5: To modify the gateway endpoint by adding a route table**

The following ``modify-vpc-endpoint`` example modifies the gateway endpoint by associating an additional route table with it. ::

    aws ec2 modify-vpc-endpoint \
        --vpc-endpoint-id vpce-032a826a \
        --add-route-table-ids rtb-aaa222bb

Output::

    {
        "Return": true
    }

**Example 6: To create an interface endpoint for EC2**

The following ``create-vpc-endpoint`` example creates an interface VPC endpoint for the EC2 service in the same VPC, associating it with a subnet and security group. ::

    aws ec2 create-vpc-endpoint \
        --vpc-id vpc-1a2b3c4d \
        --vpc-endpoint-type Interface \
        --service-name com.amazonaws.us-east-1.ec2 \
        --subnet-ids subnet-7b16de0c \
        --security-group-id sg-54e8bf31 \
        --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=my-ec2-interface-endpoint}]'

Output::

    {
        "VpcEndpoint": {
            "VpcEndpointId": "vpce-0f89a33420c1931d7",
            "VpcEndpointType": "Interface",
            "VpcId": "vpc-1a2b3c4d",
            "ServiceName": "com.amazonaws.us-east-1.ec2",
            "State": "pending",
            "RouteTableIds": [],
            "SubnetIds": [
                "subnet-7b16de0c"
            ],
            "Groups": [
                {
                    "GroupId": "sg-54e8bf31",
                    "GroupName": "default"
                }
            ],
            "PrivateDnsEnabled": false,
            "RequesterManaged": false,
            "NetworkInterfaceIds": [
                "eni-2ec2b084"
            ],
            "DnsEntries": [
                {
                    "DnsName": "vpce-0f89a33420c1931d7-bluzidnv.ec2.us-east-1.vpce.amazonaws.com",
                    "HostedZoneId": "Z7HUB22UULQXV"
                }
            ],
            "CreationTimestamp": "2023-09-15T11:00:00.000Z",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-ec2-interface-endpoint"
                }
            ],
            "OwnerId": "123456789012"
        }
    }

**Example 7: To delete both VPC endpoints**

The following ``delete-vpc-endpoints`` example deletes both the gateway and interface endpoints created in the workflow. If the command succeeds, the ``Unsuccessful`` list is empty. ::

    aws ec2 delete-vpc-endpoints \
        --vpc-endpoint-ids vpce-032a826a vpce-0f89a33420c1931d7

Output::

    {
        "Unsuccessful": []
    }
