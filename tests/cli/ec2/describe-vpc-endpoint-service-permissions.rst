**To describe endpoint service permissions**

This example describes the permissions for the specified endpoint service.

Command::

  aws ec2 describe-vpc-endpoint-service-permissions --service-id vpce-svc-03d5ebb7d9579a2b3

Output::

 {
    "AllowedPrincipals": [
        {
            "PrincipalType": "Account", 
            "Principal": "arn:aws:iam::123456789012:root"
        }
    ]
 }

**To describe endpoint service permissions with a query**

This example lists only the principals that are allowed to connect to the specified endpoint service.

Command::

  aws ec2 describe-vpc-endpoint-service-permissions --service-id vpce-svc-03d5ebb7d9579a2b3 --query "AllowedPrincipals[*].Principal"

Output::

  [
    "arn:aws:iam::123456789012:root"
  ]
