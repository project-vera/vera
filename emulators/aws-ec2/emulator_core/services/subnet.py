from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
import ipaddress
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State
from ..utils import parse_ipv4_cidr, invalid_cidr_error

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class Subnet:
    assign_ipv6_address_on_creation: bool = False
    availability_zone: str = ""
    availability_zone_id: str = ""
    available_ip_address_count: int = 0
    block_public_access_states: Dict[str, Any] = field(default_factory=dict)
    cidr_block: str = ""
    customer_owned_ipv4_pool: str = ""
    default_for_az: bool = False
    enable_dns64: bool = False
    enable_lni_at_device_index: int = 0
    ipv6_cidr_block_association_set: List[Any] = field(default_factory=list)
    ipv6_native: bool = False
    map_customer_owned_ip_on_launch: bool = False
    map_public_ip_on_launch: bool = False
    outpost_arn: str = ""
    owner_id: str = ""
    private_dns_name_options_on_launch: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    subnet_arn: str = ""
    subnet_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    type: str = ""
    vpc_id: str = ""

    # Internal dependency tracking — not in API response
    ec2_instance_connect_endpoint_ids: List[str] = field(default_factory=list)  # tracks Ec2InstanceConnectEndpoint children
    elastic_ip_addresse_ids: List[str] = field(default_factory=list)  # tracks ElasticIpAddresse children
    instance_ids: List[str] = field(default_factory=list)  # tracks Instance children
    nat_gateway_ids: List[str] = field(default_factory=list)  # tracks NatGateway children
    transit_gateway_multicast_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayMulticast children
    network_interface_ids: List[str] = field(default_factory=list)  # tracks ElasticNetworkInterface children

    subnet_cidr_reservations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assignIpv6AddressOnCreation": self.assign_ipv6_address_on_creation,
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "availableIpAddressCount": self.available_ip_address_count,
            "blockPublicAccessStates": self.block_public_access_states,
            "cidrBlock": self.cidr_block,
            "customerOwnedIpv4Pool": self.customer_owned_ipv4_pool,
            "defaultForAz": self.default_for_az,
            "enableDns64": self.enable_dns64,
            "enableLniAtDeviceIndex": self.enable_lni_at_device_index,
            "ipv6CidrBlockAssociationSet": self.ipv6_cidr_block_association_set,
            "ipv6Native": self.ipv6_native,
            "mapCustomerOwnedIpOnLaunch": self.map_customer_owned_ip_on_launch,
            "mapPublicIpOnLaunch": self.map_public_ip_on_launch,
            "outpostArn": self.outpost_arn,
            "ownerId": self.owner_id,
            "privateDnsNameOptionsOnLaunch": self.private_dns_name_options_on_launch,
            "state": self.state,
            "subnetArn": self.subnet_arn,
            "subnetId": self.subnet_id,
            "tagSet": self.tag_set,
            "type": self.type,
            "vpcId": self.vpc_id,
        }

class Subnet_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.subnets  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.fast_snapshot_restores.get(params['availability_zone_id']).subnet_ids.append(new_id)
    #   Delete: self.state.fast_snapshot_restores.get(resource.availability_zone_id).subnet_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).subnet_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).subnet_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources: List[Any] = []
        for resource_id in resource_ids:
            resource, error = self._get_resource_or_error(store, resource_id, error_code)
            if error:
                return None, error
            resources.append(resource)
        return resources, None

    def _get_subnet_or_error(self, subnet_id: str, error_code: str = "InvalidSubnetID.NotFound"):
        return self._get_resource_or_error(self.resources, subnet_id, error_code, f"The ID '{subnet_id}' does not exist")

    def _validate_subnet_cidr(self, vpc, cidr_block: str):
        net = parse_ipv4_cidr(cidr_block)
        if net is None:
            return invalid_cidr_error(cidr_block)
        if not 16 <= net.prefixlen <= 28:
            return create_error_response("InvalidSubnet.Range", f"The CIDR '{cidr_block}' is invalid.")
        vpc_nets = [
            parse_ipv4_cidr(assoc.get("cidrBlock"))
            for assoc in vpc.cidr_block_association_set
            if (assoc.get("cidrBlockState") or {}).get("state") != "disassociated"
        ]
        if not any(v is not None and net.subnet_of(v) for v in vpc_nets):
            return create_error_response("InvalidSubnet.Range", f"The CIDR '{cidr_block}' is invalid.")
        for other in self.resources.values():
            other_net = parse_ipv4_cidr(other.cidr_block) if other.vpc_id == vpc.vpc_id else None
            if other_net is not None and net.overlaps(other_net):
                return create_error_response(
                    "InvalidSubnet.Conflict", f"The CIDR '{cidr_block}' conflicts with another subnet"
                )
        return None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: str) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def AssociateSubnetCidrBlock(self, params: Dict[str, Any]):
        """Associates a CIDR block with your subnet. You can only associate a single IPv6 CIDR
            block with your subnet."""

        error = self._require_params(params, ["SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet, error = self._get_subnet_or_error(subnet_id)
        if error:
            return error

        if subnet.ipv6_cidr_block_association_set:
            return create_error_response(
                "InvalidSubnet.Conflict",
                "IPv6 CIDR block already associated with subnet.",
            )

        ipv6_cidr_block = params.get("Ipv6CidrBlock") or ""
        ipam_pool_id = params.get("Ipv6IpamPoolId") or ""
        if not ipv6_cidr_block and not ipam_pool_id and params.get("Ipv6NetmaskLength") is None:
            return create_error_response("InvalidParameterValue", "Missing IPv6 CIDR block parameters.")

        association = {
            "associationId": self._generate_id("subnet-cidr-assoc"),
            "ipSource": "amazon",
            "ipv6AddressAttribute": "",
            "ipv6CidrBlock": ipv6_cidr_block,
            "ipv6CidrBlockState": {
                "state": "associated",
                "statusMessage": "",
            },
        }
        subnet.ipv6_cidr_block_association_set.append(association)

        return {
            'ipv6CidrBlockAssociation': association,
            'subnetId': subnet_id,
            }

    def CreateDefaultSubnet(self, params: Dict[str, Any]):
        """Creates a default subnet with a size/20IPv4 CIDR block in the
            specified Availability Zone in your default VPC. You can have only one default subnet
            per Availability Zone. For more information, seeCreate a default
                subnetin theAmazon VPC User Guide."""

        availability_zone = params.get("AvailabilityZone") or ""
        availability_zone_id = params.get("AvailabilityZoneId") or ""

        default_vpc = None
        default_attr = None
        if "default-vpc" in self.state.account_attributes:
            default_attr = self.state.account_attributes.get("default-vpc")
        else:
            for candidate in self.state.account_attributes.values():
                if getattr(candidate, "attribute_name", "") == "default-vpc":
                    default_attr = candidate
                    break
        if default_attr:
            for item in default_attr.attribute_value_set or []:
                if isinstance(item, dict):
                    vpc_id = item.get("attributeValue") or item.get("AttributeValue") or item.get("value")
                else:
                    vpc_id = item
                if vpc_id and vpc_id in self.state.vpcs:
                    default_vpc = self.state.vpcs.get(vpc_id)
                    break

        if not default_vpc:
            for candidate in self.state.vpcs.values():
                if getattr(candidate, "is_default", False) or getattr(candidate, "default", False) or getattr(candidate, "default_vpc", False):
                    default_vpc = candidate
                    break

        if not default_vpc and self.state.vpcs:
            default_vpc = next(iter(self.state.vpcs.values()))

        if not default_vpc:
            return create_error_response("InvalidVpcID.NotFound", "Default VPC does not exist.")

        vpc_id = getattr(default_vpc, "vpc_id", "") or getattr(default_vpc, "vpcId", "")
        for subnet in self.resources.values():
            if subnet.vpc_id != vpc_id or not subnet.default_for_az:
                continue
            if availability_zone and subnet.availability_zone == availability_zone:
                return create_error_response("InvalidSubnet.Conflict", "Default subnet already exists in the Availability Zone.")
            if availability_zone_id and subnet.availability_zone_id == availability_zone_id:
                return create_error_response("InvalidSubnet.Conflict", "Default subnet already exists in the Availability Zone.")
            if not availability_zone and not availability_zone_id:
                return create_error_response("InvalidSubnet.Conflict", "Default subnet already exists in the Availability Zone.")

        vpc_cidr = getattr(default_vpc, "cidr_block", "") or getattr(default_vpc, "cidrBlock", "")
        cidr_block = ""
        if vpc_cidr:
            try:
                vpc_net = ipaddress.ip_network(vpc_cidr, strict=False)
                desired_prefix = 20 if vpc_net.prefixlen < 20 else vpc_net.prefixlen
                candidates = [vpc_net] if vpc_net.prefixlen >= desired_prefix else list(vpc_net.subnets(new_prefix=desired_prefix))
                used_cidrs = {s.cidr_block for s in self.resources.values() if s.vpc_id == vpc_id and s.cidr_block}
                for candidate in candidates:
                    if str(candidate) not in used_cidrs:
                        cidr_block = str(candidate)
                        break
            except ValueError:
                cidr_block = vpc_cidr
        if not cidr_block:
            cidr_block = "10.0.0.0/20"

        available_ip_address_count = 0
        try:
            net = ipaddress.ip_network(cidr_block, strict=False)
            if net.version == 4:
                available_ip_address_count = max(net.num_addresses - 5, 0)
        except ValueError:
            available_ip_address_count = 0

        ipv6_native = str2bool(params.get("Ipv6Native"))
        ipv6_cidr_block_association_set: List[Dict[str, Any]] = []
        if ipv6_native:
            ipv6_cidr = getattr(default_vpc, "ipv6_cidr_block", "") or getattr(default_vpc, "ipv6CidrBlock", "")
            if ipv6_cidr:
                ipv6_cidr_block_association_set = [{
                    "associationId": self._generate_id("subnet-cidr-assoc"),
                    "ipSource": "amazon",
                    "ipv6AddressAttribute": "",
                    "ipv6CidrBlock": ipv6_cidr,
                    "ipv6CidrBlockState": {
                        "state": "associated",
                        "statusMessage": "",
                    },
                }]

        subnet_id = self._generate_id("subnet")
        resource = Subnet(
            assign_ipv6_address_on_creation=ipv6_native,
            availability_zone=availability_zone,
            availability_zone_id=availability_zone_id,
            available_ip_address_count=available_ip_address_count,
            block_public_access_states={"internetGatewayBlockMode": "off"},
            cidr_block=cidr_block,
            default_for_az=True,
            enable_dns64=False,
            enable_lni_at_device_index=0,
            ipv6_cidr_block_association_set=ipv6_cidr_block_association_set,
            ipv6_native=ipv6_native,
            map_customer_owned_ip_on_launch=False,
            map_public_ip_on_launch=True,
            outpost_arn="",
            owner_id=getattr(default_vpc, "owner_id", ""),
            private_dns_name_options_on_launch={
                "enableResourceNameDnsAAAARecord": False,
                "enableResourceNameDnsARecord": False,
                "hostnameType": "ip-name",
            },
            state="available",
            subnet_arn="",
            subnet_id=subnet_id,
            tag_set=[],
            type="",
            vpc_id=vpc_id,
        )

        self.resources[subnet_id] = resource
        parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
        if parent and hasattr(parent, "subnet_ids"):
            parent.subnet_ids.append(subnet_id)
        if default_vpc and hasattr(default_vpc, "subnet_ids"):
            default_vpc.subnet_ids.append(subnet_id)

        return {
            'subnet': resource.to_dict(),
            }

    def CreateSubnet(self, params: Dict[str, Any]):
        """Creates a subnet in the specified VPC. For an IPv4 only subnet, specify an IPv4 CIDR block.
            If the VPC has an IPv6 CIDR block, you can create an IPv6 only subnet or a dual stack subnet instead.
            For an IPv6 only subnet, specify an IPv6 CIDR block. For a dual stack subnet, spec"""

        error = self._require_params(params, ["VpcId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        availability_zone = params.get("AvailabilityZone") or ""
        availability_zone_id = params.get("AvailabilityZoneId") or ""
        cidr_block = params.get("CidrBlock") or ""
        ipv6_cidr_block = params.get("Ipv6CidrBlock") or ""
        ipv6_native = str2bool(params.get("Ipv6Native"))
        outpost_arn = params.get("OutpostArn") or ""

        if cidr_block:
            error = self._validate_subnet_cidr(vpc, cidr_block)
            if error:
                return error

        tag_set = self._extract_tags(params.get("TagSpecification.N", []) or [], "subnet")

        ipv6_cidr_block_association_set: List[Dict[str, Any]] = []
        if ipv6_cidr_block:
            ipv6_cidr_block_association_set = [{
                "associationId": self._generate_id("subnet-cidr-assoc"),
                "ipSource": "amazon",
                "ipv6AddressAttribute": "",
                "ipv6CidrBlock": ipv6_cidr_block,
                "ipv6CidrBlockState": {
                    "state": "associated",
                    "statusMessage": "",
                },
            }]

        available_ip_address_count = 0
        if cidr_block:
            net = parse_ipv4_cidr(cidr_block)
            available_ip_address_count = max(net.num_addresses - 5, 0)

        subnet_id = self._generate_id("subnet")
        resource = Subnet(
            assign_ipv6_address_on_creation=ipv6_native,
            availability_zone=availability_zone,
            availability_zone_id=availability_zone_id,
            available_ip_address_count=available_ip_address_count,
            block_public_access_states={"internetGatewayBlockMode": "off"},
            cidr_block=cidr_block,
            customer_owned_ipv4_pool="",
            default_for_az=False,
            enable_dns64=False,
            enable_lni_at_device_index=0,
            ipv6_cidr_block_association_set=ipv6_cidr_block_association_set,
            ipv6_native=ipv6_native,
            map_customer_owned_ip_on_launch=False,
            map_public_ip_on_launch=False,
            outpost_arn=outpost_arn,
            owner_id=getattr(vpc, "owner_id", ""),
            private_dns_name_options_on_launch={
                "enableResourceNameDnsAAAARecord": False,
                "enableResourceNameDnsARecord": False,
                "hostnameType": "ip-name",
            },
            state="available",
            subnet_arn="",
            subnet_id=subnet_id,
            tag_set=tag_set,
            type="",
            vpc_id=vpc_id,
        )

        self.resources[subnet_id] = resource
        parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
        if parent and hasattr(parent, "subnet_ids"):
            parent.subnet_ids.append(subnet_id)
        if vpc and hasattr(vpc, "subnet_ids"):
            vpc.subnet_ids.append(subnet_id)

        return {
            'subnet': resource.to_dict(),
            }

    def CreateSubnetCidrReservation(self, params: Dict[str, Any]):
        """Creates a subnet CIDR reservation. For more information, seeSubnet CIDR reservationsin theAmazon VPC User GuideandManage prefixes 
                for your network interfacesin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["Cidr", "ReservationType", "SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet, error = self._get_subnet_or_error(subnet_id)
        if error:
            return error

        tag_set = self._extract_tags(params.get("TagSpecification.N", []) or [], "subnet-cidr-reservation")
        reservation_id = self._generate_id("subnet-cidr-resv")
        owner_id = subnet.owner_id
        if not owner_id:
            vpc = self.state.vpcs.get(subnet.vpc_id)
            if vpc:
                owner_id = getattr(vpc, "owner_id", "")

        reservation = {
            "cidr": params.get("Cidr") or "",
            "description": params.get("Description") or "",
            "ownerId": owner_id,
            "reservationType": params.get("ReservationType") or "",
            "subnetCidrReservationId": reservation_id,
            "subnetId": subnet_id,
            "tagSet": tag_set,
        }
        subnet.subnet_cidr_reservations.append(reservation)

        return {
            'subnetCidrReservation': reservation,
            }

    def DeleteSubnet(self, params: Dict[str, Any]):
        """Deletes the specified subnet. You must terminate all running instances in the subnet before you can delete the subnet."""

        error = self._require_params(params, ["SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet, error = self._get_subnet_or_error(subnet_id)
        if error:
            return error

        if getattr(subnet, "ec2_instance_connect_endpoint_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent Ec2InstanceConnectEndpoint(s) and cannot be deleted.')
        if getattr(subnet, "elastic_ip_addresse_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent ElasticIpAddresse(s) and cannot be deleted.')
        if getattr(subnet, "instance_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent Instance(s) and cannot be deleted.')
        if getattr(subnet, "nat_gateway_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent NatGateway(s) and cannot be deleted.')
        if getattr(subnet, "transit_gateway_multicast_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent TransitGatewayMulticast(s) and cannot be deleted.')
        if getattr(subnet, "network_interface_ids", []):
            return create_error_response('DependencyViolation', 'Subnet has dependent ElasticNetworkInterface(s) and cannot be deleted.')

        self.resources.pop(subnet_id, None)

        parent = self.state.fast_snapshot_restores.get(subnet.availability_zone_id)
        if parent and hasattr(parent, "subnet_ids") and subnet_id in parent.subnet_ids:
            parent.subnet_ids.remove(subnet_id)
        vpc = self.state.vpcs.get(subnet.vpc_id)
        if vpc and hasattr(vpc, "subnet_ids") and subnet_id in vpc.subnet_ids:
            vpc.subnet_ids.remove(subnet_id)

        return {
            'return': True,
            }

    def DeleteSubnetCidrReservation(self, params: Dict[str, Any]):
        """Deletes a subnet CIDR reservation."""

        error = self._require_params(params, ["SubnetCidrReservationId"])
        if error:
            return error

        reservation_id = params.get("SubnetCidrReservationId")
        target_subnet = None
        reservation = None
        for subnet in self.resources.values():
            for item in getattr(subnet, "subnet_cidr_reservations", []):
                if item.get("subnetCidrReservationId") == reservation_id:
                    target_subnet = subnet
                    reservation = item
                    break
            if reservation:
                break

        if not reservation or not target_subnet:
            return create_error_response("InvalidSubnetCidrReservationId.NotFound", f"The ID '{reservation_id}' does not exist")

        if reservation in target_subnet.subnet_cidr_reservations:
            target_subnet.subnet_cidr_reservations.remove(reservation)

        return {
            'deletedSubnetCidrReservation': reservation,
            }

    def DescribeSubnets(self, params: Dict[str, Any]):
        """Describes your subnets. The default is to describe all your subnets. 
          Alternatively, you can specify specific subnet IDs or filter the results to
          include only the subnets that match specific criteria. For more information, seeSubnetsin theAmazon VPC User Guide."""

        subnet_ids = params.get("SubnetId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if subnet_ids:
            resources, error = self._get_resources_by_ids(self.resources, subnet_ids, "InvalidSubnetID.NotFound")
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        subnet_set = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'nextToken': None,
            'subnetSet': subnet_set,
            }

    def DisassociateSubnetCidrBlock(self, params: Dict[str, Any]):
        """Disassociates a CIDR block from a subnet. Currently, you can disassociate an IPv6 CIDR block only. You must detach or delete all gateways and resources that are associated with the CIDR block before you can disassociate it."""

        error = self._require_params(params, ["AssociationId"])
        if error:
            return error

        association_id = params.get("AssociationId")
        target_subnet = None
        association = None
        for subnet in self.resources.values():
            for item in subnet.ipv6_cidr_block_association_set:
                if item.get("associationId") == association_id:
                    target_subnet = subnet
                    association = item
                    break
            if association:
                break

        if not association or not target_subnet:
            return create_error_response("InvalidAssociationID.NotFound", f"The ID '{association_id}' does not exist")

        association_state = association.get("ipv6CidrBlockState") or {}
        association_state["state"] = "disassociated"
        association_state.setdefault("statusMessage", "")
        association["ipv6CidrBlockState"] = association_state

        if association in target_subnet.ipv6_cidr_block_association_set:
            target_subnet.ipv6_cidr_block_association_set.remove(association)

        return {
            'ipv6CidrBlockAssociation': association,
            'subnetId': target_subnet.subnet_id,
            }

    def GetSubnetCidrReservations(self, params: Dict[str, Any]):
        """Gets information about the subnet CIDR reservations."""

        error = self._require_params(params, ["SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet, error = self._get_subnet_or_error(subnet_id)
        if error:
            return error

        reservations = list(getattr(subnet, "subnet_cidr_reservations", []))
        filters = params.get("Filter.N", []) or []
        if filters:
            filtered: List[Dict[str, Any]] = []
            filter_map = {
                "cidr": "cidr",
                "description": "description",
                "owner-id": "ownerId",
                "reservation-type": "reservationType",
                "subnet-cidr-reservation-id": "subnetCidrReservationId",
                "subnet-id": "subnetId",
            }
            for reservation in reservations:
                include = True
                for filter_item in filters:
                    name = (filter_item.get("Name") or "").lower()
                    key = filter_map.get(name)
                    if not key:
                        continue
                    values = filter_item.get("Value") or []
                    if values and reservation.get(key) not in values:
                        include = False
                        break
                if include:
                    filtered.append(reservation)
            reservations = filtered

        max_results = int(params.get("MaxResults") or 100)
        reservations = reservations[:max_results]

        ipv4_reservations: List[Dict[str, Any]] = []
        ipv6_reservations: List[Dict[str, Any]] = []
        for reservation in reservations:
            cidr = reservation.get("cidr") or ""
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                if net.version == 6:
                    ipv6_reservations.append(reservation)
                else:
                    ipv4_reservations.append(reservation)
            except ValueError:
                ipv4_reservations.append(reservation)

        return {
            'nextToken': None,
            'subnetIpv4CidrReservationSet': ipv4_reservations,
            'subnetIpv6CidrReservationSet': ipv6_reservations,
            }

    def ModifySubnetAttribute(self, params: Dict[str, Any]):
        """Modifies a subnet attribute. You can only modify one attribute at a time. Use this action to modify subnets on AWS Outposts. To modify a subnet on an Outpost rack, set bothMapCustomerOwnedIpOnLaunchandCustomerOwnedIpv4Pool. These two parameters act as a single
                    attribute."""

        error = self._require_params(params, ["SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet, error = self._get_subnet_or_error(subnet_id)
        if error:
            return error

        if params.get("AssignIpv6AddressOnCreation") is not None:
            subnet.assign_ipv6_address_on_creation = str2bool(params.get("AssignIpv6AddressOnCreation"))

        if params.get("EnableDns64") is not None:
            subnet.enable_dns64 = str2bool(params.get("EnableDns64"))

        if params.get("EnableLniAtDeviceIndex") is not None:
            subnet.enable_lni_at_device_index = int(params.get("EnableLniAtDeviceIndex") or 0)

        if params.get("DisableLniAtDeviceIndex") is not None:
            if str2bool(params.get("DisableLniAtDeviceIndex")):
                subnet.enable_lni_at_device_index = 0

        if params.get("MapPublicIpOnLaunch") is not None:
            subnet.map_public_ip_on_launch = str2bool(params.get("MapPublicIpOnLaunch"))

        if params.get("MapCustomerOwnedIpOnLaunch") is not None:
            subnet.map_customer_owned_ip_on_launch = str2bool(params.get("MapCustomerOwnedIpOnLaunch"))

        if params.get("CustomerOwnedIpv4Pool") is not None:
            subnet.customer_owned_ipv4_pool = params.get("CustomerOwnedIpv4Pool") or ""

        if params.get("EnableResourceNameDnsAAAARecordOnLaunch") is not None:
            subnet.private_dns_name_options_on_launch.setdefault("enableResourceNameDnsAAAARecord", False)
            subnet.private_dns_name_options_on_launch["enableResourceNameDnsAAAARecord"] = str2bool(
                params.get("EnableResourceNameDnsAAAARecordOnLaunch")
            )

        if params.get("EnableResourceNameDnsARecordOnLaunch") is not None:
            subnet.private_dns_name_options_on_launch.setdefault("enableResourceNameDnsARecord", False)
            subnet.private_dns_name_options_on_launch["enableResourceNameDnsARecord"] = str2bool(
                params.get("EnableResourceNameDnsARecordOnLaunch")
            )

        if params.get("PrivateDnsHostnameTypeOnLaunch") is not None:
            subnet.private_dns_name_options_on_launch.setdefault("hostnameType", "")
            subnet.private_dns_name_options_on_launch["hostnameType"] = params.get("PrivateDnsHostnameTypeOnLaunch") or ""

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'subnet') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class subnet_RequestParser:
    @staticmethod
    def parse_associate_subnet_cidr_block_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Ipv6CidrBlock": get_scalar(md, "Ipv6CidrBlock"),
            "Ipv6IpamPoolId": get_scalar(md, "Ipv6IpamPoolId"),
            "Ipv6NetmaskLength": get_int(md, "Ipv6NetmaskLength"),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_create_default_subnet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Ipv6Native": get_scalar(md, "Ipv6Native"),
        }

    @staticmethod
    def parse_create_subnet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "CidrBlock": get_scalar(md, "CidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Ipv4IpamPoolId": get_scalar(md, "Ipv4IpamPoolId"),
            "Ipv4NetmaskLength": get_int(md, "Ipv4NetmaskLength"),
            "Ipv6CidrBlock": get_scalar(md, "Ipv6CidrBlock"),
            "Ipv6IpamPoolId": get_scalar(md, "Ipv6IpamPoolId"),
            "Ipv6Native": get_scalar(md, "Ipv6Native"),
            "Ipv6NetmaskLength": get_int(md, "Ipv6NetmaskLength"),
            "OutpostArn": get_scalar(md, "OutpostArn"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_create_subnet_cidr_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReservationType": get_scalar(md, "ReservationType"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_subnet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_delete_subnet_cidr_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetCidrReservationId": get_scalar(md, "SubnetCidrReservationId"),
        }

    @staticmethod
    def parse_describe_subnets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SubnetId.N": get_indexed_list(md, "SubnetId"),
        }

    @staticmethod
    def parse_disassociate_subnet_cidr_block_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
        }

    @staticmethod
    def parse_get_subnet_cidr_reservations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_modify_subnet_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssignIpv6AddressOnCreation": get_scalar(md, "AssignIpv6AddressOnCreation"),
            "CustomerOwnedIpv4Pool": get_scalar(md, "CustomerOwnedIpv4Pool"),
            "DisableLniAtDeviceIndex": get_scalar(md, "DisableLniAtDeviceIndex"),
            "EnableDns64": get_scalar(md, "EnableDns64"),
            "EnableLniAtDeviceIndex": get_int(md, "EnableLniAtDeviceIndex"),
            "EnableResourceNameDnsAAAARecordOnLaunch": get_scalar(md, "EnableResourceNameDnsAAAARecordOnLaunch"),
            "EnableResourceNameDnsARecordOnLaunch": get_scalar(md, "EnableResourceNameDnsARecordOnLaunch"),
            "MapCustomerOwnedIpOnLaunch": get_scalar(md, "MapCustomerOwnedIpOnLaunch"),
            "MapPublicIpOnLaunch": get_scalar(md, "MapPublicIpOnLaunch"),
            "PrivateDnsHostnameTypeOnLaunch": get_scalar(md, "PrivateDnsHostnameTypeOnLaunch"),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateSubnetCidrBlock": subnet_RequestParser.parse_associate_subnet_cidr_block_request,
            "CreateDefaultSubnet": subnet_RequestParser.parse_create_default_subnet_request,
            "CreateSubnet": subnet_RequestParser.parse_create_subnet_request,
            "CreateSubnetCidrReservation": subnet_RequestParser.parse_create_subnet_cidr_reservation_request,
            "DeleteSubnet": subnet_RequestParser.parse_delete_subnet_request,
            "DeleteSubnetCidrReservation": subnet_RequestParser.parse_delete_subnet_cidr_reservation_request,
            "DescribeSubnets": subnet_RequestParser.parse_describe_subnets_request,
            "DisassociateSubnetCidrBlock": subnet_RequestParser.parse_disassociate_subnet_cidr_block_request,
            "GetSubnetCidrReservations": subnet_RequestParser.parse_get_subnet_cidr_reservations_request,
            "ModifySubnetAttribute": subnet_RequestParser.parse_modify_subnet_attribute_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class subnet_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(subnet_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(subnet_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(subnet_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(subnet_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_associate_subnet_cidr_block_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateSubnetCidrBlockResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipv6CidrBlockAssociation
        _ipv6CidrBlockAssociation_key = None
        if "ipv6CidrBlockAssociation" in data:
            _ipv6CidrBlockAssociation_key = "ipv6CidrBlockAssociation"
        elif "Ipv6CidrBlockAssociation" in data:
            _ipv6CidrBlockAssociation_key = "Ipv6CidrBlockAssociation"
        if _ipv6CidrBlockAssociation_key:
            param_data = data[_ipv6CidrBlockAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipv6CidrBlockAssociation>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipv6CidrBlockAssociation>')
        # Serialize subnetId
        _subnetId_key = None
        if "subnetId" in data:
            _subnetId_key = "subnetId"
        elif "SubnetId" in data:
            _subnetId_key = "SubnetId"
        if _subnetId_key:
            param_data = data[_subnetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<subnetId>{esc(str(param_data))}</subnetId>')
        xml_parts.append(f'</AssociateSubnetCidrBlockResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_default_subnet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateDefaultSubnetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize subnet
        _subnet_key = None
        if "subnet" in data:
            _subnet_key = "subnet"
        elif "Subnet" in data:
            _subnet_key = "Subnet"
        if _subnet_key:
            param_data = data[_subnet_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<subnet>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</subnet>')
        xml_parts.append(f'</CreateDefaultSubnetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_subnet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateSubnetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize subnet
        _subnet_key = None
        if "subnet" in data:
            _subnet_key = "subnet"
        elif "Subnet" in data:
            _subnet_key = "Subnet"
        if _subnet_key:
            param_data = data[_subnet_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<subnet>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</subnet>')
        xml_parts.append(f'</CreateSubnetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_subnet_cidr_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateSubnetCidrReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize subnetCidrReservation
        _subnetCidrReservation_key = None
        if "subnetCidrReservation" in data:
            _subnetCidrReservation_key = "subnetCidrReservation"
        elif "SubnetCidrReservation" in data:
            _subnetCidrReservation_key = "SubnetCidrReservation"
        if _subnetCidrReservation_key:
            param_data = data[_subnetCidrReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<subnetCidrReservation>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</subnetCidrReservation>')
        xml_parts.append(f'</CreateSubnetCidrReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_subnet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteSubnetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DeleteSubnetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_subnet_cidr_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteSubnetCidrReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize deletedSubnetCidrReservation
        _deletedSubnetCidrReservation_key = None
        if "deletedSubnetCidrReservation" in data:
            _deletedSubnetCidrReservation_key = "deletedSubnetCidrReservation"
        elif "DeletedSubnetCidrReservation" in data:
            _deletedSubnetCidrReservation_key = "DeletedSubnetCidrReservation"
        if _deletedSubnetCidrReservation_key:
            param_data = data[_deletedSubnetCidrReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<deletedSubnetCidrReservation>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</deletedSubnetCidrReservation>')
        xml_parts.append(f'</DeleteSubnetCidrReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_subnets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSubnetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize subnetSet
        _subnetSet_key = None
        if "subnetSet" in data:
            _subnetSet_key = "subnetSet"
        elif "SubnetSet" in data:
            _subnetSet_key = "SubnetSet"
        elif "Subnets" in data:
            _subnetSet_key = "Subnets"
        if _subnetSet_key:
            param_data = data[_subnetSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<subnetSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</subnetSet>')
            else:
                xml_parts.append(f'{indent_str}<subnetSet/>')
        xml_parts.append(f'</DescribeSubnetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_subnet_cidr_block_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateSubnetCidrBlockResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipv6CidrBlockAssociation
        _ipv6CidrBlockAssociation_key = None
        if "ipv6CidrBlockAssociation" in data:
            _ipv6CidrBlockAssociation_key = "ipv6CidrBlockAssociation"
        elif "Ipv6CidrBlockAssociation" in data:
            _ipv6CidrBlockAssociation_key = "Ipv6CidrBlockAssociation"
        if _ipv6CidrBlockAssociation_key:
            param_data = data[_ipv6CidrBlockAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipv6CidrBlockAssociation>')
            xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipv6CidrBlockAssociation>')
        # Serialize subnetId
        _subnetId_key = None
        if "subnetId" in data:
            _subnetId_key = "subnetId"
        elif "SubnetId" in data:
            _subnetId_key = "SubnetId"
        if _subnetId_key:
            param_data = data[_subnetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<subnetId>{esc(str(param_data))}</subnetId>')
        xml_parts.append(f'</DisassociateSubnetCidrBlockResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_subnet_cidr_reservations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetSubnetCidrReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize subnetIpv4CidrReservationSet
        _subnetIpv4CidrReservationSet_key = None
        if "subnetIpv4CidrReservationSet" in data:
            _subnetIpv4CidrReservationSet_key = "subnetIpv4CidrReservationSet"
        elif "SubnetIpv4CidrReservationSet" in data:
            _subnetIpv4CidrReservationSet_key = "SubnetIpv4CidrReservationSet"
        elif "SubnetIpv4CidrReservations" in data:
            _subnetIpv4CidrReservationSet_key = "SubnetIpv4CidrReservations"
        if _subnetIpv4CidrReservationSet_key:
            param_data = data[_subnetIpv4CidrReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<subnetIpv4CidrReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</subnetIpv4CidrReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<subnetIpv4CidrReservationSet/>')
        # Serialize subnetIpv6CidrReservationSet
        _subnetIpv6CidrReservationSet_key = None
        if "subnetIpv6CidrReservationSet" in data:
            _subnetIpv6CidrReservationSet_key = "subnetIpv6CidrReservationSet"
        elif "SubnetIpv6CidrReservationSet" in data:
            _subnetIpv6CidrReservationSet_key = "SubnetIpv6CidrReservationSet"
        elif "SubnetIpv6CidrReservations" in data:
            _subnetIpv6CidrReservationSet_key = "SubnetIpv6CidrReservations"
        if _subnetIpv6CidrReservationSet_key:
            param_data = data[_subnetIpv6CidrReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<subnetIpv6CidrReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(subnet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</subnetIpv6CidrReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<subnetIpv6CidrReservationSet/>')
        xml_parts.append(f'</GetSubnetCidrReservationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_subnet_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifySubnetAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</ModifySubnetAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateSubnetCidrBlock": subnet_ResponseSerializer.serialize_associate_subnet_cidr_block_response,
            "CreateDefaultSubnet": subnet_ResponseSerializer.serialize_create_default_subnet_response,
            "CreateSubnet": subnet_ResponseSerializer.serialize_create_subnet_response,
            "CreateSubnetCidrReservation": subnet_ResponseSerializer.serialize_create_subnet_cidr_reservation_response,
            "DeleteSubnet": subnet_ResponseSerializer.serialize_delete_subnet_response,
            "DeleteSubnetCidrReservation": subnet_ResponseSerializer.serialize_delete_subnet_cidr_reservation_response,
            "DescribeSubnets": subnet_ResponseSerializer.serialize_describe_subnets_response,
            "DisassociateSubnetCidrBlock": subnet_ResponseSerializer.serialize_disassociate_subnet_cidr_block_response,
            "GetSubnetCidrReservations": subnet_ResponseSerializer.serialize_get_subnet_cidr_reservations_response,
            "ModifySubnetAttribute": subnet_ResponseSerializer.serialize_modify_subnet_attribute_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

