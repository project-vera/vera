from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
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
class RouteTable:
    carrier_gateway_id: str = ""
    core_network_arn: str = ""
    destination_cidr_block: str = ""
    destination_ipv6_cidr_block: str = ""
    destination_prefix_list_id: str = ""
    egress_only_internet_gateway_id: str = ""
    gateway_id: str = ""
    instance_id: str = ""
    instance_owner_id: str = ""
    ip_address: str = ""
    local_gateway_id: str = ""
    nat_gateway_id: str = ""
    network_interface_id: str = ""
    odb_network_arn: str = ""
    origin: str = ""
    state: str = ""
    transit_gateway_id: str = ""
    vpc_peering_connection_id: str = ""

    route_table_id: str = ""
    vpc_id: str = ""
    owner_id: str = ""
    association_set: List[Dict[str, Any]] = field(default_factory=list)
    route_set: List[Dict[str, Any]] = field(default_factory=list)
    propagating_vgw_set: List[Dict[str, Any]] = field(default_factory=list)
    tag_set: List[Dict[str, Any]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    is_main: bool = False
    association_index: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrierGatewayId": self.carrier_gateway_id,
            "coreNetworkArn": self.core_network_arn,
            "destinationCidrBlock": self.destination_cidr_block,
            "destinationIpv6CidrBlock": self.destination_ipv6_cidr_block,
            "destinationPrefixListId": self.destination_prefix_list_id,
            "egressOnlyInternetGatewayId": self.egress_only_internet_gateway_id,
            "gatewayId": self.gateway_id,
            "instanceId": self.instance_id,
            "instanceOwnerId": self.instance_owner_id,
            "ipAddress": self.ip_address,
            "localGatewayId": self.local_gateway_id,
            "natGatewayId": self.nat_gateway_id,
            "networkInterfaceId": self.network_interface_id,
            "odbNetworkArn": self.odb_network_arn,
            "origin": self.origin,
            "state": self.state,
            "transitGatewayId": self.transit_gateway_id,
            "vpcPeeringConnectionId": self.vpc_peering_connection_id,
            "routeTableId": self.route_table_id,
            "vpcId": self.vpc_id,
            "ownerId": self.owner_id,
            "associationSet": self.association_set,
            "routeSet": self.route_set,
            "propagatingVgwSet": self.propagating_vgw_set,
            "tagSet": self.tag_set,
        }

class RouteTable_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.route_tables  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.instances.get(params['instance_id']).route_table_ids.append(new_id)
    #   Delete: self.state.instances.get(resource.instance_id).route_table_ids.remove(resource_id)
    #   Create: self.state.local_gateways.get(params['local_gateway_id']).route_table_ids.append(new_id)
    #   Delete: self.state.local_gateways.get(resource.local_gateway_id).route_table_ids.remove(resource_id)
    #   Create: self.state.nat_gateways.get(params['nat_gateway_id']).route_table_ids.append(new_id)
    #   Delete: self.state.nat_gateways.get(resource.nat_gateway_id).route_table_ids.remove(resource_id)
    #   Create: self.state.transit_gateway_multicast.get(params['network_interface_id']).route_table_ids.append(new_id)
    #   Delete: self.state.transit_gateway_multicast.get(resource.network_interface_id).route_table_ids.remove(resource_id)
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).route_table_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).route_table_ids.remove(resource_id)
    #   Create: self.state.vpc_peering.get(params['vpc_peering_connection_id']).route_table_ids.append(new_id)
    #   Delete: self.state.vpc_peering.get(resource.vpc_peering_connection_id).route_table_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).route_table_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).route_table_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_route_table(self, route_table_id: str) -> (Optional[RouteTable], Optional[Dict[str, Any]]):
        route_table = self.resources.get(route_table_id)
        if not route_table:
            return None, create_error_response(
                "InvalidRouteTableID.NotFound",
                f"The ID '{route_table_id}' does not exist",
            )
        return route_table, None

    def _get_or_error(self, store: Dict[str, Any], resource_id: str, code: str, message: str):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(code, message)
        return resource, None

    def _extract_tag_set(self, tag_specs: List[Dict[str, Any]], resource_type: str):
        for spec in tag_specs or []:
            if spec.get("ResourceType") == resource_type:
                tags = spec.get("Tags", []) or []
                tag_map = {tag.get("Key"): tag.get("Value", "") for tag in tags if tag.get("Key")}
                return tags, tag_map
        return [], {}

    def _find_association(self, association_id: str):
        for route_table in self.resources.values():
            association = route_table.association_index.get(association_id)
            if association:
                return route_table, association, None
            for item in route_table.association_set:
                if item.get("routeTableAssociationId") == association_id:
                    return route_table, item, None
        return None, None, create_error_response(
            "InvalidAssociationID.NotFound",
            f"The association ID '{association_id}' does not exist",
        )

    def _find_route(self, route_table: RouteTable, destination_cidr: str, destination_ipv6: str, destination_prefix_list: str):
        for route in route_table.route_set:
            if destination_cidr and route.get("destinationCidrBlock") == destination_cidr:
                return route
            if destination_ipv6 and route.get("destinationIpv6CidrBlock") == destination_ipv6:
                return route
            if destination_prefix_list and route.get("destinationPrefixListId") == destination_prefix_list:
                return route
        return None

    def AssociateRouteTable(self, params: Dict[str, Any]):
        """Associates a subnet in your VPC or an internet gateway or virtual private gateway
            attached to your VPC with a route table in your VPC. This association causes traffic
            from the subnet or gateway to be routed according to the routes in the route table. The
            action re"""

        error = self._require_params(params, ["RouteTableId"])
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        route_table, error = self._get_route_table(route_table_id)
        if error:
            return error

        subnet_id = params.get("SubnetId")
        gateway_id = params.get("GatewayId")
        if not subnet_id and not gateway_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SubnetId or GatewayId",
            )

        subnet = None
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                return create_error_response(
                    "InvalidSubnetID.NotFound",
                    f"The ID '{subnet_id}' does not exist",
                )

        if gateway_id:
            igw = self.state.internet_gateways.get(gateway_id)
            vgw = self.state.virtual_private_gateways.get(gateway_id)
            if not igw and not vgw:
                return create_error_response(
                    "InvalidGatewayID.NotFound",
                    f"The ID '{gateway_id}' does not exist",
                )

        association_id = self._generate_id("rtbassoc")
        association = {
            "associationState": {"state": "associated", "statusMessage": ""},
            "gatewayId": gateway_id,
            "main": False,
            "publicIpv4Pool": params.get("PublicIpv4Pool"),
            "routeTableAssociationId": association_id,
            "routeTableId": route_table_id,
            "subnetId": subnet_id,
        }

        route_table.association_set.append(association)
        route_table.association_index[association_id] = association

        if subnet and hasattr(subnet, "route_table_id"):
            subnet.route_table_id = route_table_id

        return {
            'associationId': association_id,
            'associationState': {
                'state': "associated",
                'statusMessage': "",
                },
            }

    def CreateRoute(self, params: Dict[str, Any]):
        """Creates a route in a route table within a VPC. You must specify either a destination CIDR block or a prefix list ID. You must also specify  
         exactly one of the resources from the parameter list. When determining how to route traffic, we use the route with the most specific match.
          """

        error = self._require_params(params, ["RouteTableId"])
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        route_table, error = self._get_route_table(route_table_id)
        if error:
            return error

        destination_cidr = params.get("DestinationCidrBlock")
        destination_ipv6 = params.get("DestinationIpv6CidrBlock")
        destination_prefix_list = params.get("DestinationPrefixListId")
        if not destination_cidr and not destination_ipv6 and not destination_prefix_list:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationIpv6CidrBlock or DestinationPrefixListId",
            )

        if destination_cidr and parse_ipv4_cidr(destination_cidr) is None:
            return invalid_cidr_error(destination_cidr, "destinationCidrBlock")

        target_values = {
            "CarrierGatewayId": params.get("CarrierGatewayId"),
            "CoreNetworkArn": params.get("CoreNetworkArn"),
            "EgressOnlyInternetGatewayId": params.get("EgressOnlyInternetGatewayId"),
            "GatewayId": params.get("GatewayId"),
            "InstanceId": params.get("InstanceId"),
            "LocalGatewayId": params.get("LocalGatewayId"),
            "NatGatewayId": params.get("NatGatewayId"),
            "NetworkInterfaceId": params.get("NetworkInterfaceId"),
            "OdbNetworkArn": params.get("OdbNetworkArn"),
            "TransitGatewayId": params.get("TransitGatewayId"),
            "VpcEndpointId": params.get("VpcEndpointId"),
            "VpcPeeringConnectionId": params.get("VpcPeeringConnectionId"),
        }
        specified_targets = {key: value for key, value in target_values.items() if value}
        if not specified_targets:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: target for the route",
            )
        if len(specified_targets) > 1:
            return create_error_response(
                "InvalidParameterValue",
                "Exactly one target must be specified for the route",
            )

        carrier_gateway_id = params.get("CarrierGatewayId")
        if carrier_gateway_id and not self.state.carrier_gateways.get(carrier_gateway_id):
            return create_error_response(
                "InvalidCarrierGatewayID.NotFound",
                f"The ID '{carrier_gateway_id}' does not exist",
            )

        egress_only_id = params.get("EgressOnlyInternetGatewayId")
        if egress_only_id:
            egress_gateway = self.state.internet_gateways.get(egress_only_id)
            if not egress_gateway or not getattr(egress_gateway, "is_egress_only", False):
                return create_error_response(
                    "InvalidEgressOnlyInternetGatewayId.NotFound",
                    f"The ID '{egress_only_id}' does not exist",
                )

        gateway_id = params.get("GatewayId")
        if gateway_id:
            igw = self.state.internet_gateways.get(gateway_id)
            vgw = self.state.virtual_private_gateways.get(gateway_id)
            if not igw and not vgw:
                return create_error_response(
                    "InvalidGatewayID.NotFound",
                    f"The ID '{gateway_id}' does not exist",
                )

        instance_id = params.get("InstanceId")
        instance = None
        if instance_id:
            instance = self.state.instances.get(instance_id)
            if not instance:
                return create_error_response(
                    "InvalidInstanceID.NotFound",
                    f"The ID '{instance_id}' does not exist",
                )

        local_gateway_id = params.get("LocalGatewayId")
        if local_gateway_id and not self.state.local_gateways.get(local_gateway_id):
            return create_error_response(
                "InvalidLocalGatewayId.NotFound",
                f"The ID '{local_gateway_id}' does not exist",
            )

        nat_gateway_id = params.get("NatGatewayId")
        if nat_gateway_id and not self.state.nat_gateways.get(nat_gateway_id):
            return create_error_response(
                "InvalidNatGatewayID.NotFound",
                f"The ID '{nat_gateway_id}' does not exist",
            )

        network_interface_id = params.get("NetworkInterfaceId")
        network_interface = None
        if network_interface_id:
            network_interface = self.state.elastic_network_interfaces.get(network_interface_id)
            if not network_interface:
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        transit_gateway_id = params.get("TransitGatewayId")
        if transit_gateway_id and not self.state.transit_gateways.get(transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{transit_gateway_id}' does not exist",
            )

        vpc_endpoint_id = params.get("VpcEndpointId")
        if vpc_endpoint_id and not self.state.vpc_endpoints.get(vpc_endpoint_id):
            return create_error_response(
                "InvalidVpcEndpointID.NotFound",
                f"The ID '{vpc_endpoint_id}' does not exist",
            )

        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        if vpc_peering_connection_id and not self.state.vpc_peering.get(vpc_peering_connection_id):
            return create_error_response(
                "InvalidVpcPeeringConnectionID.NotFound",
                f"The ID '{vpc_peering_connection_id}' does not exist",
            )

        instance_owner_id = getattr(instance, "owner_id", "") if instance else ""
        ip_address = ""
        if instance and getattr(instance, "private_ip_address", ""):
            ip_address = instance.private_ip_address
        if network_interface and getattr(network_interface, "private_ip_address", ""):
            ip_address = network_interface.private_ip_address

        route = {
            "carrierGatewayId": carrier_gateway_id,
            "coreNetworkArn": params.get("CoreNetworkArn"),
            "destinationCidrBlock": destination_cidr,
            "destinationIpv6CidrBlock": destination_ipv6,
            "destinationPrefixListId": destination_prefix_list,
            "egressOnlyInternetGatewayId": egress_only_id,
            "gatewayId": gateway_id,
            "instanceId": instance_id,
            "instanceOwnerId": instance_owner_id,
            "ipAddress": ip_address,
            "localGatewayId": local_gateway_id,
            "natGatewayId": nat_gateway_id,
            "networkInterfaceId": network_interface_id,
            "odbNetworkArn": params.get("OdbNetworkArn"),
            "origin": "CreateRoute",
            "state": "active",
            "transitGatewayId": transit_gateway_id,
            "vpcPeeringConnectionId": vpc_peering_connection_id,
            "vpcEndpointId": vpc_endpoint_id,
        }

        if route_table.route_set is None:
            route_table.route_set = []
        existing_route = self._find_route(route_table, destination_cidr, destination_ipv6, destination_prefix_list)
        if existing_route and existing_route in route_table.route_set:
            route_table.route_set.remove(existing_route)
        route_table.route_set.append(route)

        return {
            'return': True,
            }

    def CreateRouteTable(self, params: Dict[str, Any]):
        """Creates a route table for the specified VPC. After you create a route table, you can add routes and associate the table with a subnet. For more information, seeRoute tablesin theAmazon VPC User Guide."""

        error = self._require_params(params, ["VpcId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(tag_specs, "route-table")

        route_table_id = self._generate_id("rtb")
        owner_id = getattr(vpc, "owner_id", "")
        association_set: List[Dict[str, Any]] = []
        propagating_vgw_set: List[Dict[str, Any]] = []
        route_set: List[Dict[str, Any]] = []

        vpc_cidr = getattr(vpc, "cidr_block", "") or getattr(vpc, "cidrBlock", "")
        if vpc_cidr:
            route_set.append({
                "destinationCidrBlock": vpc_cidr,
                "gatewayId": "local",
                "origin": "CreateRouteTable",
                "state": "active",
            })

        vpc_ipv6 = getattr(vpc, "ipv6_cidr_block", "") or getattr(vpc, "ipv6CidrBlock", "")
        if vpc_ipv6:
            route_set.append({
                "destinationIpv6CidrBlock": vpc_ipv6,
                "gatewayId": "local",
                "origin": "CreateRouteTable",
                "state": "active",
            })

        resource = RouteTable(
            association_set=association_set,
            is_main=False,
            owner_id=owner_id,
            propagating_vgw_set=propagating_vgw_set,
            route_set=route_set,
            route_table_id=route_table_id,
            tag_set=tag_set,
            tags=tag_map,
            vpc_id=vpc_id,
        )
        self.resources[route_table_id] = resource

        if hasattr(vpc, "route_table_ids"):
            vpc.route_table_ids.append(route_table_id)

        return {
            'clientToken': params.get("ClientToken"),
            'routeTable': {
                'associationSet': resource.association_set,
                'ownerId': resource.owner_id,
                'propagatingVgwSet': resource.propagating_vgw_set,
                'routeSet': resource.route_set,
                'routeTableId': resource.route_table_id,
                'tagSet': resource.tag_set,
                'vpcId': resource.vpc_id,
                },
            }

    def DeleteRoute(self, params: Dict[str, Any]):
        """Deletes the specified route from the specified route table."""

        error = self._require_params(params, ["RouteTableId"])
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        route_table, error = self._get_route_table(route_table_id)
        if error:
            return error

        destination_cidr = params.get("DestinationCidrBlock")
        destination_ipv6 = params.get("DestinationIpv6CidrBlock")
        destination_prefix_list = params.get("DestinationPrefixListId")
        if not destination_cidr and not destination_ipv6 and not destination_prefix_list:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationIpv6CidrBlock or DestinationPrefixListId",
            )

        route = self._find_route(route_table, destination_cidr, destination_ipv6, destination_prefix_list)
        if not route:
            return create_error_response(
                "InvalidRoute.NotFound",
                "The specified route does not exist.",
            )

        route_table.route_set.remove(route)

        return {
            'return': True,
            }

    def DeleteRouteTable(self, params: Dict[str, Any]):
        """Deletes the specified route table. You must disassociate the route table from any subnets before you can delete it. You can't delete the main route table."""

        error = self._require_params(params, ["RouteTableId"])
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        route_table, error = self._get_route_table(route_table_id)
        if error:
            return error

        if route_table.is_main:
            return create_error_response(
                "DependencyViolation",
                "Cannot delete the main route table.",
            )

        if route_table.association_set:
            return create_error_response(
                "DependencyViolation",
                "Route table has existing associations.",
            )

        vpc = self.state.vpcs.get(route_table.vpc_id)
        if vpc and hasattr(vpc, "route_table_ids") and route_table_id in vpc.route_table_ids:
            vpc.route_table_ids.remove(route_table_id)

        instance = self.state.instances.get(route_table.instance_id)
        if instance and hasattr(instance, "route_table_ids") and route_table_id in instance.route_table_ids:
            instance.route_table_ids.remove(route_table_id)

        local_gateway = self.state.local_gateways.get(route_table.local_gateway_id)
        if local_gateway and hasattr(local_gateway, "route_table_ids") and route_table_id in local_gateway.route_table_ids:
            local_gateway.route_table_ids.remove(route_table_id)

        nat_gateway = self.state.nat_gateways.get(route_table.nat_gateway_id)
        if nat_gateway and hasattr(nat_gateway, "route_table_ids") and route_table_id in nat_gateway.route_table_ids:
            nat_gateway.route_table_ids.remove(route_table_id)

        tgw_multicast = self.state.transit_gateway_multicast.get(route_table.network_interface_id)
        if tgw_multicast and hasattr(tgw_multicast, "route_table_ids") and route_table_id in tgw_multicast.route_table_ids:
            tgw_multicast.route_table_ids.remove(route_table_id)

        transit_gateway = self.state.transit_gateways.get(route_table.transit_gateway_id)
        if transit_gateway and hasattr(transit_gateway, "route_table_ids") and route_table_id in transit_gateway.route_table_ids:
            transit_gateway.route_table_ids.remove(route_table_id)

        vpc_peering = self.state.vpc_peering.get(route_table.vpc_peering_connection_id)
        if vpc_peering and hasattr(vpc_peering, "route_table_ids") and route_table_id in vpc_peering.route_table_ids:
            vpc_peering.route_table_ids.remove(route_table_id)

        self.resources.pop(route_table_id, None)

        return {
            'return': True,
            }

    def DescribeRouteTables(self, params: Dict[str, Any]):
        """Describes your route tables. The default is to describe all your route tables. 
           Alternatively, you can specify specific route table IDs or filter the results to
           include only the route tables that match specific criteria. Each subnet in your VPC must be associated with a route t"""

        route_table_ids = params.get("RouteTableId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if route_table_ids:
            resources: List[RouteTable] = []
            for route_table_id in route_table_ids:
                resource = self.resources.get(route_table_id)
                if not resource:
                    return create_error_response(
                        "InvalidRouteTableID.NotFound",
                        f"The ID '{route_table_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        route_tables = []
        for resource in resources[:max_results]:
            route_tables.append({
                "associationSet": resource.association_set,
                "ownerId": resource.owner_id,
                "propagatingVgwSet": resource.propagating_vgw_set,
                "routeSet": resource.route_set,
                "routeTableId": resource.route_table_id,
                "tagSet": resource.tag_set,
                "vpcId": resource.vpc_id,
            })

        return {
            'nextToken': None,
            'routeTableSet': route_tables,
            }

    def DisassociateRouteTable(self, params: Dict[str, Any]):
        """Disassociates a subnet or gateway from a route table. After you perform this action, the subnet no longer uses the routes in the route table.
				Instead, it uses the routes in the VPC's main route table. For more information
				about route tables, seeRoute
				tablesin theAmazon VPC User Guide."""

        error = self._require_params(params, ["AssociationId"])
        if error:
            return error

        association_id = params.get("AssociationId")
        route_table, association, error = self._find_association(association_id)
        if error:
            return error

        if association.get("main"):
            return create_error_response(
                "DependencyViolation",
                "Cannot disassociate the main route table.",
            )

        route_table.association_index.pop(association_id, None)
        if association in route_table.association_set:
            route_table.association_set.remove(association)

        subnet_id = association.get("subnetId")
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if subnet and hasattr(subnet, "route_table_id"):
                subnet.route_table_id = ""

        return {
            'return': True,
            }

    def ReplaceRoute(self, params: Dict[str, Any]):
        """Replaces an existing route within a route table in a VPC. You must specify either a destination CIDR block or a prefix list ID. You must also specify  
           exactly one of the resources from the parameter list, or reset the local route to its default 
           target. For more information, s"""

        error = self._require_params(params, ["RouteTableId"])
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        route_table, error = self._get_route_table(route_table_id)
        if error:
            return error

        destination_cidr = params.get("DestinationCidrBlock")
        destination_ipv6 = params.get("DestinationIpv6CidrBlock")
        destination_prefix_list = params.get("DestinationPrefixListId")
        if not destination_cidr and not destination_ipv6 and not destination_prefix_list:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationIpv6CidrBlock or DestinationPrefixListId",
            )

        local_target = str2bool(params.get("LocalTarget"))
        target_values = {
            "CarrierGatewayId": params.get("CarrierGatewayId"),
            "CoreNetworkArn": params.get("CoreNetworkArn"),
            "EgressOnlyInternetGatewayId": params.get("EgressOnlyInternetGatewayId"),
            "GatewayId": params.get("GatewayId"),
            "InstanceId": params.get("InstanceId"),
            "LocalGatewayId": params.get("LocalGatewayId"),
            "NatGatewayId": params.get("NatGatewayId"),
            "NetworkInterfaceId": params.get("NetworkInterfaceId"),
            "OdbNetworkArn": params.get("OdbNetworkArn"),
            "TransitGatewayId": params.get("TransitGatewayId"),
            "VpcEndpointId": params.get("VpcEndpointId"),
            "VpcPeeringConnectionId": params.get("VpcPeeringConnectionId"),
        }
        specified_targets = {key: value for key, value in target_values.items() if value}
        if local_target and specified_targets:
            return create_error_response(
                "InvalidParameterValue",
                "LocalTarget cannot be combined with other targets",
            )
        if not local_target:
            if not specified_targets:
                return create_error_response(
                    "MissingParameter",
                    "Missing required parameter: target for the route",
                )
            if len(specified_targets) > 1:
                return create_error_response(
                    "InvalidParameterValue",
                    "Exactly one target must be specified for the route",
                )

        existing_route = self._find_route(route_table, destination_cidr, destination_ipv6, destination_prefix_list)
        if not existing_route:
            return create_error_response(
                "InvalidRoute.NotFound",
                "The specified route does not exist.",
            )

        carrier_gateway_id = params.get("CarrierGatewayId")
        if carrier_gateway_id and not self.state.carrier_gateways.get(carrier_gateway_id):
            return create_error_response(
                "InvalidCarrierGatewayID.NotFound",
                f"The ID '{carrier_gateway_id}' does not exist",
            )

        egress_only_id = params.get("EgressOnlyInternetGatewayId")
        if egress_only_id:
            egress_gateway = self.state.internet_gateways.get(egress_only_id)
            if not egress_gateway or not getattr(egress_gateway, "is_egress_only", False):
                return create_error_response(
                    "InvalidEgressOnlyInternetGatewayId.NotFound",
                    f"The ID '{egress_only_id}' does not exist",
                )

        gateway_id = params.get("GatewayId")
        if gateway_id:
            igw = self.state.internet_gateways.get(gateway_id)
            vgw = self.state.virtual_private_gateways.get(gateway_id)
            if not igw and not vgw:
                return create_error_response(
                    "InvalidGatewayID.NotFound",
                    f"The ID '{gateway_id}' does not exist",
                )

        instance_id = params.get("InstanceId")
        instance = None
        if instance_id:
            instance = self.state.instances.get(instance_id)
            if not instance:
                return create_error_response(
                    "InvalidInstanceID.NotFound",
                    f"The ID '{instance_id}' does not exist",
                )

        local_gateway_id = params.get("LocalGatewayId")
        if local_gateway_id and not self.state.local_gateways.get(local_gateway_id):
            return create_error_response(
                "InvalidLocalGatewayId.NotFound",
                f"The ID '{local_gateway_id}' does not exist",
            )

        nat_gateway_id = params.get("NatGatewayId")
        if nat_gateway_id and not self.state.nat_gateways.get(nat_gateway_id):
            return create_error_response(
                "InvalidNatGatewayID.NotFound",
                f"The ID '{nat_gateway_id}' does not exist",
            )

        network_interface_id = params.get("NetworkInterfaceId")
        network_interface = None
        if network_interface_id:
            network_interface = self.state.elastic_network_interfaces.get(network_interface_id)
            if not network_interface:
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        transit_gateway_id = params.get("TransitGatewayId")
        if transit_gateway_id and not self.state.transit_gateways.get(transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{transit_gateway_id}' does not exist",
            )

        vpc_endpoint_id = params.get("VpcEndpointId")
        if vpc_endpoint_id and not self.state.vpc_endpoints.get(vpc_endpoint_id):
            return create_error_response(
                "InvalidVpcEndpointID.NotFound",
                f"The ID '{vpc_endpoint_id}' does not exist",
            )

        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        if vpc_peering_connection_id and not self.state.vpc_peering.get(vpc_peering_connection_id):
            return create_error_response(
                "InvalidVpcPeeringConnectionID.NotFound",
                f"The ID '{vpc_peering_connection_id}' does not exist",
            )

        instance_owner_id = getattr(instance, "owner_id", "") if instance else ""
        ip_address = ""
        if instance and getattr(instance, "private_ip_address", ""):
            ip_address = instance.private_ip_address
        if network_interface and getattr(network_interface, "private_ip_address", ""):
            ip_address = network_interface.private_ip_address

        gateway_id_value = "local" if local_target else gateway_id
        route = {
            "carrierGatewayId": carrier_gateway_id,
            "coreNetworkArn": params.get("CoreNetworkArn"),
            "destinationCidrBlock": destination_cidr,
            "destinationIpv6CidrBlock": destination_ipv6,
            "destinationPrefixListId": destination_prefix_list,
            "egressOnlyInternetGatewayId": egress_only_id,
            "gatewayId": gateway_id_value,
            "instanceId": instance_id,
            "instanceOwnerId": instance_owner_id,
            "ipAddress": ip_address,
            "localGatewayId": local_gateway_id,
            "natGatewayId": nat_gateway_id,
            "networkInterfaceId": network_interface_id,
            "odbNetworkArn": params.get("OdbNetworkArn"),
            "origin": "ReplaceRoute",
            "state": "active",
            "transitGatewayId": transit_gateway_id,
            "vpcPeeringConnectionId": vpc_peering_connection_id,
            "vpcEndpointId": vpc_endpoint_id,
        }

        if existing_route in route_table.route_set:
            index = route_table.route_set.index(existing_route)
            route_table.route_set[index] = route
        else:
            route_table.route_set.append(route)

        return {
            'return': True,
            }

    def ReplaceRouteTableAssociation(self, params: Dict[str, Any]):
        """Changes the route table associated with a given subnet, internet gateway, or virtual private gateway in a VPC. After the operation
        completes, the subnet or gateway uses the routes in the new route table. For more
        information about route tables, seeRoute
        tablesin theAmazon VPC"""

        error = self._require_params(params, ["AssociationId", "RouteTableId"])
        if error:
            return error

        association_id = params.get("AssociationId")
        route_table, association, error = self._find_association(association_id)
        if error:
            return error

        if association.get("main"):
            return create_error_response(
                "DependencyViolation",
                "Cannot replace association for the main route table.",
            )

        new_route_table_id = params.get("RouteTableId")
        new_route_table, error = self._get_route_table(new_route_table_id)
        if error:
            return error

        new_association_id = self._generate_id("rtbassoc")
        new_association = dict(association)
        new_association["routeTableAssociationId"] = new_association_id
        new_association["routeTableId"] = new_route_table_id
        new_association["associationState"] = {"state": "associated", "statusMessage": ""}

        route_table.association_index.pop(association_id, None)
        if association in route_table.association_set:
            route_table.association_set.remove(association)

        new_route_table.association_set.append(new_association)
        new_route_table.association_index[new_association_id] = new_association

        subnet_id = new_association.get("subnetId")
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if subnet and hasattr(subnet, "route_table_id"):
                subnet.route_table_id = new_route_table_id

        return {
            'associationState': {
                'state': "associated",
                'statusMessage': "",
                },
            'newAssociationId': new_association_id,
            }

    def _generate_id(self, prefix: str = 'cagw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class routetable_RequestParser:
    @staticmethod
    def parse_associate_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GatewayId": get_scalar(md, "GatewayId"),
            "PublicIpv4Pool": get_scalar(md, "PublicIpv4Pool"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_create_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CarrierGatewayId": get_scalar(md, "CarrierGatewayId"),
            "CoreNetworkArn": get_scalar(md, "CoreNetworkArn"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationIpv6CidrBlock": get_scalar(md, "DestinationIpv6CidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EgressOnlyInternetGatewayId": get_scalar(md, "EgressOnlyInternetGatewayId"),
            "GatewayId": get_scalar(md, "GatewayId"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "LocalGatewayId": get_scalar(md, "LocalGatewayId"),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
            "OdbNetworkArn": get_scalar(md, "OdbNetworkArn"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "VpcEndpointId": get_scalar(md, "VpcEndpointId"),
            "VpcPeeringConnectionId": get_scalar(md, "VpcPeeringConnectionId"),
        }

    @staticmethod
    def parse_create_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_delete_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationIpv6CidrBlock": get_scalar(md, "DestinationIpv6CidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_delete_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_describe_route_tables_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RouteTableId.N": get_indexed_list(md, "RouteTableId"),
        }

    @staticmethod
    def parse_disassociate_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_replace_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CarrierGatewayId": get_scalar(md, "CarrierGatewayId"),
            "CoreNetworkArn": get_scalar(md, "CoreNetworkArn"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationIpv6CidrBlock": get_scalar(md, "DestinationIpv6CidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EgressOnlyInternetGatewayId": get_scalar(md, "EgressOnlyInternetGatewayId"),
            "GatewayId": get_scalar(md, "GatewayId"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "LocalGatewayId": get_scalar(md, "LocalGatewayId"),
            "LocalTarget": get_scalar(md, "LocalTarget"),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
            "OdbNetworkArn": get_scalar(md, "OdbNetworkArn"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "VpcEndpointId": get_scalar(md, "VpcEndpointId"),
            "VpcPeeringConnectionId": get_scalar(md, "VpcPeeringConnectionId"),
        }

    @staticmethod
    def parse_replace_route_table_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateRouteTable": routetable_RequestParser.parse_associate_route_table_request,
            "CreateRoute": routetable_RequestParser.parse_create_route_request,
            "CreateRouteTable": routetable_RequestParser.parse_create_route_table_request,
            "DeleteRoute": routetable_RequestParser.parse_delete_route_request,
            "DeleteRouteTable": routetable_RequestParser.parse_delete_route_table_request,
            "DescribeRouteTables": routetable_RequestParser.parse_describe_route_tables_request,
            "DisassociateRouteTable": routetable_RequestParser.parse_disassociate_route_table_request,
            "ReplaceRoute": routetable_RequestParser.parse_replace_route_request,
            "ReplaceRouteTableAssociation": routetable_RequestParser.parse_replace_route_table_association_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class routetable_ResponseSerializer:
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
                xml_parts.extend(routetable_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(routetable_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(routetable_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(routetable_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associationId
        _associationId_key = None
        if "associationId" in data:
            _associationId_key = "associationId"
        elif "AssociationId" in data:
            _associationId_key = "AssociationId"
        if _associationId_key:
            param_data = data[_associationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationId>{esc(str(param_data))}</associationId>')
        # Serialize associationState
        _associationState_key = None
        if "associationState" in data:
            _associationState_key = "associationState"
        elif "AssociationState" in data:
            _associationState_key = "AssociationState"
        if _associationState_key:
            param_data = data[_associationState_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationState>')
            xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</associationState>')
        xml_parts.append(f'</AssociateRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CreateRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize routeTable
        _routeTable_key = None
        if "routeTable" in data:
            _routeTable_key = "routeTable"
        elif "RouteTable" in data:
            _routeTable_key = "RouteTable"
        if _routeTable_key:
            param_data = data[_routeTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeTable>')
            xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeTable>')
        xml_parts.append(f'</CreateRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_route_tables_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeRouteTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize routeTableSet
        _routeTableSet_key = None
        if "routeTableSet" in data:
            _routeTableSet_key = "routeTableSet"
        elif "RouteTableSet" in data:
            _routeTableSet_key = "RouteTableSet"
        elif "RouteTables" in data:
            _routeTableSet_key = "RouteTables"
        if _routeTableSet_key:
            param_data = data[_routeTableSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeTableSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeTableSet>')
            else:
                xml_parts.append(f'{indent_str}<routeTableSet/>')
        xml_parts.append(f'</DescribeRouteTablesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DisassociateRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ReplaceRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_route_table_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceRouteTableAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associationState
        _associationState_key = None
        if "associationState" in data:
            _associationState_key = "associationState"
        elif "AssociationState" in data:
            _associationState_key = "AssociationState"
        if _associationState_key:
            param_data = data[_associationState_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationState>')
            xml_parts.extend(routetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</associationState>')
        # Serialize newAssociationId
        _newAssociationId_key = None
        if "newAssociationId" in data:
            _newAssociationId_key = "newAssociationId"
        elif "NewAssociationId" in data:
            _newAssociationId_key = "NewAssociationId"
        if _newAssociationId_key:
            param_data = data[_newAssociationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<newAssociationId>{esc(str(param_data))}</newAssociationId>')
        xml_parts.append(f'</ReplaceRouteTableAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateRouteTable": routetable_ResponseSerializer.serialize_associate_route_table_response,
            "CreateRoute": routetable_ResponseSerializer.serialize_create_route_response,
            "CreateRouteTable": routetable_ResponseSerializer.serialize_create_route_table_response,
            "DeleteRoute": routetable_ResponseSerializer.serialize_delete_route_response,
            "DeleteRouteTable": routetable_ResponseSerializer.serialize_delete_route_table_response,
            "DescribeRouteTables": routetable_ResponseSerializer.serialize_describe_route_tables_response,
            "DisassociateRouteTable": routetable_ResponseSerializer.serialize_disassociate_route_table_response,
            "ReplaceRoute": routetable_ResponseSerializer.serialize_replace_route_response,
            "ReplaceRouteTableAssociation": routetable_ResponseSerializer.serialize_replace_route_table_association_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

