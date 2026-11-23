"""CIDR validation in the VPC, subnet and route handlers.

Run from emulators/aws-ec2:  python -m unittest tests.unit.test_cidr_validation
"""
import unittest

from emulator_core.state import EC2State
from emulator_core.services.vpc import Vpc_Backend
from emulator_core.services.subnet import Subnet_Backend
from emulator_core.services.routetable import RouteTable_Backend
from emulator_core.services.internetgateway import InternetGateway_Backend

BAD_FORM = "InvalidParameterValue"


def code(resp):
    return resp.get("Error", {}).get("Code") if isinstance(resp, dict) else None


class CidrValidationTest(unittest.TestCase):
    def setUp(self):
        EC2State.reset()
        self.vpc = Vpc_Backend()
        self.subnet = Subnet_Backend()
        self.rtb = RouteTable_Backend()

    def make_vpc(self, cidr="10.0.0.0/16"):
        resp = self.vpc.CreateVpc({"CidrBlock": cidr})
        self.assertNotIn("Error", resp)
        return resp["vpc"]["vpcId"]

    def test_create_vpc_malformed(self):
        for bad in ["999.0.0.0/16", "10.0.0.0", "10.0.0.0/", "abc", "10.0.0.0/16/8",
                    "10.0.0.0/255.255.0.0", "2001:db8::/56", "10.0.0/16"]:
            with self.subTest(cidr=bad):
                resp = self.vpc.CreateVpc({"CidrBlock": bad})
                self.assertEqual(code(resp), BAD_FORM)
                self.assertIn(f"Value ({bad}) for parameter cidrBlock is invalid", resp["Error"]["Message"])
        self.assertEqual(len(self.vpc.resources), 0)

    def test_create_vpc_block_size(self):
        for bad in ["10.0.0.0/8", "10.0.0.0/15", "10.0.0.0/29", "10.0.0.0/32"]:
            with self.subTest(cidr=bad):
                resp = self.vpc.CreateVpc({"CidrBlock": bad})
                self.assertEqual(code(resp), "InvalidVpc.Range")
                self.assertEqual(resp["Error"]["Message"], f"The CIDR '{bad}' is invalid.")
        for ok in ["10.0.0.0/16", "10.0.0.0/28", "192.168.0.0/20"]:
            with self.subTest(cidr=ok):
                self.assertNotIn("Error", self.vpc.CreateVpc({"CidrBlock": ok}))

    def test_associate_vpc_cidr_block(self):
        vpc_id = self.make_vpc()
        resp = self.vpc.AssociateVpcCidrBlock({"VpcId": vpc_id, "CidrBlock": "999.0.0.0/16"})
        self.assertEqual(code(resp), BAD_FORM)
        resp = self.vpc.AssociateVpcCidrBlock({"VpcId": vpc_id, "CidrBlock": "10.1.0.0/8"})
        self.assertEqual(code(resp), "InvalidVpc.Range")
        self.assertEqual(len(self.vpc.resources[vpc_id].cidr_block_association_set), 1)
        resp = self.vpc.AssociateVpcCidrBlock({"VpcId": vpc_id, "CidrBlock": "10.1.0.0/16"})
        self.assertNotIn("Error", resp)

    def test_create_subnet_malformed(self):
        vpc_id = self.make_vpc()
        for bad in ["999.0.0.0/24", "10.0.0.0", "nonsense"]:
            with self.subTest(cidr=bad):
                resp = self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": bad})
                self.assertEqual(code(resp), BAD_FORM)
        self.assertEqual(len(self.subnet.resources), 0)

    def test_create_subnet_range(self):
        vpc_id = self.make_vpc()
        for bad in ["10.0.0.0/29", "10.0.0.0/15", "10.1.0.0/24", "192.168.0.0/24"]:
            with self.subTest(cidr=bad):
                resp = self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": bad})
                self.assertEqual(code(resp), "InvalidSubnet.Range")
                self.assertEqual(resp["Error"]["Message"], f"The CIDR '{bad}' is invalid.")

    def test_create_subnet_inside_secondary_block(self):
        vpc_id = self.make_vpc()
        self.vpc.AssociateVpcCidrBlock({"VpcId": vpc_id, "CidrBlock": "10.1.0.0/16"})
        resp = self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": "10.1.0.0/24"})
        self.assertNotIn("Error", resp)
        self.assertEqual(resp["subnet"]["availableIpAddressCount"], 251)

    def test_create_subnet_conflict(self):
        vpc_id = self.make_vpc()
        other_vpc = self.make_vpc()
        self.assertNotIn("Error", self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": "10.0.1.0/24"}))
        for bad in ["10.0.1.0/24", "10.0.0.0/16", "10.0.1.128/25"]:
            with self.subTest(cidr=bad):
                resp = self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": bad})
                self.assertEqual(code(resp), "InvalidSubnet.Conflict")
                self.assertEqual(resp["Error"]["Message"], f"The CIDR '{bad}' conflicts with another subnet")
        self.assertNotIn("Error", self.subnet.CreateSubnet({"VpcId": vpc_id, "CidrBlock": "10.0.2.0/24"}))
        self.assertNotIn("Error", self.subnet.CreateSubnet({"VpcId": other_vpc, "CidrBlock": "10.0.1.0/24"}))

    def test_ipv6_only_subnet_still_allowed(self):
        vpc_id = self.make_vpc()
        resp = self.subnet.CreateSubnet({"VpcId": vpc_id, "Ipv6CidrBlock": "2001:db8:0:1::/64", "Ipv6Native": "true"})
        self.assertNotIn("Error", resp)

    def test_create_route_malformed_destination(self):
        vpc_id = self.make_vpc()
        rtb_id = self.rtb.CreateRouteTable({"VpcId": vpc_id})["routeTable"]["routeTableId"]
        igw = InternetGateway_Backend()
        igw_id = igw.CreateInternetGateway({})["internetGateway"]["internetGatewayId"]
        self.assertNotIn("Error", igw.AttachInternetGateway({"InternetGatewayId": igw_id, "VpcId": vpc_id}))
        for bad in ["999.0.0.0/8", "not-a-cidr"]:
            with self.subTest(cidr=bad):
                resp = self.rtb.CreateRoute({"RouteTableId": rtb_id, "DestinationCidrBlock": bad, "GatewayId": igw_id})
                self.assertEqual(code(resp), BAD_FORM)
                self.assertIn("parameter destinationCidrBlock is invalid", resp["Error"]["Message"])
        resp = self.rtb.CreateRoute({"RouteTableId": rtb_id, "DestinationCidrBlock": "0.0.0.0/0", "GatewayId": igw_id})
        self.assertNotIn("Error", resp)

if __name__ == "__main__":
    unittest.main()
