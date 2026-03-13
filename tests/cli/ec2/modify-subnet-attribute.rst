**To change a subnet's public IPv4 addressing behavior**

This example modifies subnet-1a2b3c4d to specify that all instances launched into this subnet are assigned a public IPv4 address. If the command succeeds, no output is returned.

Command::

  aws ec2 modify-subnet-attribute --subnet-id subnet-1a2b3c4d --map-public-ip-on-launch

**To change a subnet's IPv6 addressing behavior**

This example modifies subnet-1a2b3c4d to specify that all instances launched into this subnet are assigned an IPv6 address from the range of the subnet.

Command::

  aws ec2 modify-subnet-attribute --subnet-id subnet-1a2b3c4d --assign-ipv6-address-on-creation

**To enable DNS64 for a subnet**

This example modifies ``subnet-1a2b3c4d`` so IPv6-only workloads in the subnet can reach IPv4 destinations through a NAT64 gateway. If the command succeeds, no output is returned.

Command::

  aws ec2 modify-subnet-attribute --subnet-id subnet-1a2b3c4d --enable-dns64

**To change the private DNS hostname type for a subnet**

This example modifies ``subnet-1a2b3c4d`` so that instances launched into the subnet use resource-name based private DNS hostnames. If the command succeeds, no output is returned.

Command::

  aws ec2 modify-subnet-attribute --subnet-id subnet-1a2b3c4d --private-dns-hostname-type-on-launch resource-name

**To enable resource-name AAAA records for a subnet**

This example modifies ``subnet-1a2b3c4d`` so that instances launched into the subnet receive IPv6 AAAA records that are derived from the resource name. If the command succeeds, no output is returned.

Command::

  aws ec2 modify-subnet-attribute --subnet-id subnet-1a2b3c4d --enable-resource-name-dns-aaaa-record-on-launch

For more information, see `IP Addressing in Your VPC`_ in the *AWS Virtual Private Cloud User Guide*.

.. _`IP Addressing in Your VPC`: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-ip-addressing.html
