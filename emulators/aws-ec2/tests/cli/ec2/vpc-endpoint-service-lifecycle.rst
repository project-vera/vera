**Example 1: To create an endpoint service configuration for an interface endpoint**

The following ``create-vpc-endpoint-service-configuration`` example creates a VPC endpoint service configuration using the specified Network Load Balancer. Requests to connect to the service through an interface endpoint must be accepted. ::

    aws ec2 create-vpc-endpoint-service-configuration \
        --network-load-balancer-arns arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/nlb-vpce/e94221227f1ba532 \
        --acceptance-required \
        --tag-specifications 'ResourceType=vpc-endpoint-service,Tags=[{Key=Name,Value=my-endpoint-service}]'

Output::

    {
        "ServiceConfiguration": {
            "ServiceType": [
                {
                    "ServiceType": "Interface"
                }
            ],
            "NetworkLoadBalancerArns": [
                "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/nlb-vpce/e94221227f1ba532"
            ],
            "ServiceName": "com.amazonaws.vpce.us-east-1.vpce-svc-03d5ebb7d9579a2b3",
            "ServiceState": "Available",
            "ServiceId": "vpce-svc-03d5ebb7d9579a2b3",
            "AcceptanceRequired": true,
            "AvailabilityZones": [
                "us-east-1d"
            ],
            "BaseEndpointDnsNames": [
                "vpce-svc-03d5ebb7d9579a2b3.us-east-1.vpce.amazonaws.com"
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-endpoint-service"
                }
            ]
        }
    }

**Example 2: To describe the endpoint service configuration**

The following ``describe-vpc-endpoint-service-configurations`` example retrieves the details of the endpoint service to confirm its availability and settings. ::

    aws ec2 describe-vpc-endpoint-service-configurations \
        --filters Name=service-id,Values=vpce-svc-03d5ebb7d9579a2b3

Output::

    {
        "ServiceConfigurations": [
            {
                "ServiceType": [
                    {
                        "ServiceType": "Interface"
                    }
                ],
                "ServiceId": "vpce-svc-03d5ebb7d9579a2b3",
                "ServiceName": "com.amazonaws.vpce.us-east-1.vpce-svc-03d5ebb7d9579a2b3",
                "ServiceState": "Available",
                "AvailabilityZones": [
                    "us-east-1d"
                ],
                "AcceptanceRequired": true,
                "ManagesVpcEndpoints": false,
                "NetworkLoadBalancerArns": [
                    "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/net/nlb-vpce/e94221227f1ba532"
                ],
                "BaseEndpointDnsNames": [
                    "vpce-svc-03d5ebb7d9579a2b3.us-east-1.vpce.amazonaws.com"
                ],
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "my-endpoint-service"
                    }
                ]
            }
        ]
    }

**Example 3: To check for pending endpoint connection requests**

The following ``describe-vpc-endpoint-connections`` example lists endpoint connections to the service that are in the ``pendingAcceptance`` state. ::

    aws ec2 describe-vpc-endpoint-connections \
        --filters Name=service-id,Values=vpce-svc-03d5ebb7d9579a2b3 Name=vpc-endpoint-state,Values=pendingAcceptance

Output::

    {
        "VpcEndpointConnections": [
            {
                "VpcEndpointId": "vpce-0c1308d7312217abc",
                "ServiceId": "vpce-svc-03d5ebb7d9579a2b3",
                "CreationTimestamp": "2023-09-20T14:00:24.350Z",
                "VpcEndpointState": "pendingAcceptance",
                "VpcEndpointOwner": "123456789012"
            }
        ]
    }

**Example 4: To accept a pending endpoint connection request**

The following ``accept-vpc-endpoint-connections`` example accepts the pending endpoint connection request for the specified service. If the command succeeds, the ``Unsuccessful`` list is empty. ::

    aws ec2 accept-vpc-endpoint-connections \
        --service-id vpce-svc-03d5ebb7d9579a2b3 \
        --vpc-endpoint-ids vpce-0c1308d7312217abc

Output::

    {
        "Unsuccessful": []
    }

**Example 5: To modify the endpoint service to disable acceptance requirement**

The following ``modify-vpc-endpoint-service-configuration`` example updates the service configuration to automatically accept new endpoint connections without manual approval. ::

    aws ec2 modify-vpc-endpoint-service-configuration \
        --service-id vpce-svc-03d5ebb7d9579a2b3 \
        --no-acceptance-required

Output::

    {
        "ReturnValue": true
    }

**Example 6: To delete the endpoint service configuration**

The following ``delete-vpc-endpoint-service-configurations`` example deletes the specified endpoint service configuration. If the command succeeds, the ``Unsuccessful`` list is empty. ::

    aws ec2 delete-vpc-endpoint-service-configurations \
        --service-ids vpce-svc-03d5ebb7d9579a2b3

Output::

    {
        "Unsuccessful": []
    }
