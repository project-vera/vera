**To modify an endpoint service configuration**

This example changes the acceptance requirement for the specified endpoint service.

Command::

  aws ec2 modify-vpc-endpoint-service-configuration --service-id vpce-svc-09222513e6e77dc86 --no-acceptance-required

Output::

 {
    "ReturnValue": true
 }

**To add supported Regions to an endpoint service**

This example adds two supported Regions to the specified endpoint service so interface endpoints can be created from those Regions.

Command::

  aws ec2 modify-vpc-endpoint-service-configuration --service-id vpce-svc-09222513e6e77dc86 --add-supported-regions us-east-1 us-west-2

Output::

 {
    "ReturnValue": true
 }

**To set a private DNS name for an endpoint service**

This example configures a private DNS name for the specified endpoint service.

Command::

  aws ec2 modify-vpc-endpoint-service-configuration --service-id vpce-svc-09222513e6e77dc86 --private-dns-name api.internal.example.com

Output::

 {
    "ReturnValue": true
 }
