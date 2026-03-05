**Example 1: To create a virtual private gateway**

The following ``create-vpn-gateway`` example creates a virtual private gateway using the ``ipsec.1`` VPN type and a custom Amazon-side ASN for BGP sessions. ::

    aws ec2 create-vpn-gateway \
        --type ipsec.1 \
        --amazon-side-asn 65001 \
        --tag-specifications 'ResourceType=vpn-gateway,Tags=[{Key=Name,Value=my-vgw}]'

Output::

    {
        "VpnGateway": {
            "AmazonSideAsn": 65001,
            "State": "available",
            "Type": "ipsec.1",
            "VpnGatewayId": "vgw-9a4cacf3",
            "VpcAttachments": [],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-vgw"
                }
            ]
        }
    }

**Example 2: To create a VPC to attach to the virtual private gateway**

The following ``create-vpc`` example creates a VPC with the specified IPv4 CIDR block that will be attached to the virtual private gateway. ::

    aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vgw-vpc}]'

Output::

    {
        "Vpc": {
            "CidrBlock": "10.0.0.0/16",
            "DhcpOptionsId": "dopt-5EXAMPLE",
            "State": "pending",
            "VpcId": "vpc-a01106c2",
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
                    "Value": "my-vgw-vpc"
                }
            ]
        }
    }

**Example 3: To attach the virtual private gateway to the VPC**

The following ``attach-vpn-gateway`` example attaches the virtual private gateway created in Example 1 to the VPC created in Example 2. ::

    aws ec2 attach-vpn-gateway \
        --vpn-gateway-id vgw-9a4cacf3 \
        --vpc-id vpc-a01106c2

Output::

    {
        "VpcAttachment": {
            "State": "attaching",
            "VpcId": "vpc-a01106c2"
        }
    }

**Example 4: To describe the virtual private gateway and confirm attachment**

The following ``describe-vpn-gateways`` example retrieves details about the specified virtual private gateway to confirm the attachment state. ::

    aws ec2 describe-vpn-gateways \
        --vpn-gateway-ids vgw-9a4cacf3

Output::

    {
        "VpnGateways": [
            {
                "AmazonSideAsn": 65001,
                "State": "available",
                "Type": "ipsec.1",
                "VpnGatewayId": "vgw-9a4cacf3",
                "VpcAttachments": [
                    {
                        "State": "attaching",
                        "VpcId": "vpc-a01106c2"
                    }
                ],
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "my-vgw"
                    }
                ]
            }
        ]
    }

**Example 5: To detach the virtual private gateway from the VPC**

The following ``detach-vpn-gateway`` example detaches the virtual private gateway from the VPC prior to deletion. If the command succeeds, no output is returned. ::

    aws ec2 detach-vpn-gateway \
        --vpn-gateway-id vgw-9a4cacf3 \
        --vpc-id vpc-a01106c2

**Example 6: To delete the virtual private gateway**

The following ``delete-vpn-gateway`` example deletes the specified virtual private gateway after it has been detached from the VPC. If the command succeeds, no output is returned. ::

    aws ec2 delete-vpn-gateway \
        --vpn-gateway-id vgw-9a4cacf3

**Example 7: To delete the VPC**

The following ``delete-vpc`` example deletes the VPC that was created for the virtual private gateway workflow. If the command succeeds, no output is returned. ::

    aws ec2 delete-vpc \
        --vpc-id vpc-a01106c2
