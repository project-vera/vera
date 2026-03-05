**Example 1: To create a VPC with a Name tag**

The following ``create-vpc`` example creates a VPC with the specified IPv4 CIDR block and applies a Name tag. ::

    aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]'

Output::

    {
        "Vpc": {
            "CidrBlock": "10.0.0.0/16",
            "DhcpOptionsId": "dopt-5EXAMPLE",
            "State": "pending",
            "VpcId": "vpc-0a60eb65b4EXAMPLE",
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
                    "Value": "my-vpc"
                }
            ]
        }
    }

**Example 2: To wait for the VPC to become available**

The following ``wait vpc-available`` example pauses and resumes running only after it confirms that the specified VPC is available. ::

    aws ec2 wait vpc-available \
        --vpc-ids vpc-0a60eb65b4EXAMPLE

**Example 3: To describe the VPC and confirm it is available**

The following ``describe-vpcs`` example retrieves details about the newly created VPC to confirm its state is ``available``. ::

    aws ec2 describe-vpcs \
        --vpc-ids vpc-0a60eb65b4EXAMPLE

Output::

    {
        "Vpcs": [
            {
                "CidrBlock": "10.0.0.0/16",
                "DhcpOptionsId": "dopt-5EXAMPLE",
                "State": "available",
                "VpcId": "vpc-0a60eb65b4EXAMPLE",
                "OwnerId": "123456789012",
                "InstanceTenancy": "default",
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
                        "Value": "my-vpc"
                    }
                ]
            }
        ]
    }

**Example 4: To associate an additional IPv4 CIDR block with the VPC**

The following ``associate-vpc-cidr-block`` example associates a secondary IPv4 CIDR block with the VPC to expand its address space. ::

    aws ec2 associate-vpc-cidr-block \
        --vpc-id vpc-0a60eb65b4EXAMPLE \
        --cidr-block 10.1.0.0/16

Output::

    {
        "CidrBlockAssociation": {
            "AssociationId": "vpc-cidr-assoc-00b24cc1c2EXAMPLE",
            "CidrBlock": "10.1.0.0/16",
            "CidrBlockState": {
                "State": "associating"
            }
        },
        "VpcId": "vpc-0a60eb65b4EXAMPLE"
    }

**Example 5: To enable DNS hostnames for instances launched in the VPC**

The following ``modify-vpc-attribute`` example enables DNS hostname assignment for instances launched in the specified VPC. If the command succeeds, no output is returned. ::

    aws ec2 modify-vpc-attribute \
        --vpc-id vpc-0a60eb65b4EXAMPLE \
        --enable-dns-hostnames "{\"Value\":true}"

**Example 6: To verify the DNS hostname attribute on the VPC**

The following ``describe-vpc-attribute`` example retrieves the ``enableDnsHostnames`` attribute to confirm DNS hostname support is enabled. ::

    aws ec2 describe-vpc-attribute \
        --vpc-id vpc-0a60eb65b4EXAMPLE \
        --attribute enableDnsHostnames

Output::

    {
        "VpcId": "vpc-0a60eb65b4EXAMPLE",
        "EnableDnsHostnames": {
            "Value": true
        }
    }

**Example 7: To disassociate the secondary CIDR block from the VPC**

The following ``disassociate-vpc-cidr-block`` example removes the secondary CIDR block association from the VPC. If the command succeeds, no output is returned. ::

    aws ec2 disassociate-vpc-cidr-block \
        --association-id vpc-cidr-assoc-00b24cc1c2EXAMPLE

Output::

  {
    "CidrBlockAssociation": {
        "AssociationId": "vpc-cidr-assoc-00b24cc1c2EXAMPLE", 
        "CidrBlock": "10.1.0.0/16", 
        "CidrBlockState": {
            "State": "disassociating"
        }
    }, 
    "VpcId": "vpc-0a60eb65b4EXAMPLE"
  }

**Example 8: To delete the VPC**

The following ``delete-vpc`` example deletes the specified VPC after all resources have been removed. If the command succeeds, no output is returned. ::

    aws ec2 delete-vpc \
        --vpc-id vpc-0a60eb65b4EXAMPLE
