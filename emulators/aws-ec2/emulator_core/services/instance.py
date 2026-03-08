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
class Instance:
    ami_launch_index: int = 0
    architecture: str = ""
    block_device_mapping: List[Any] = field(default_factory=list)
    boot_mode: str = ""
    capacity_block_id: str = ""
    capacity_reservation_id: str = ""
    capacity_reservation_specification: Dict[str, Any] = field(default_factory=dict)
    client_token: str = ""
    cpu_options: Dict[str, Any] = field(default_factory=dict)
    current_instance_boot_mode: str = ""
    dns_name: str = ""
    ebs_optimized: bool = False
    elastic_gpu_association_set: List[Any] = field(default_factory=list)
    elastic_inference_accelerator_association_set: List[Any] = field(default_factory=list)
    ena_support: bool = False
    enclave_options: Dict[str, Any] = field(default_factory=dict)
    group_set: List[Any] = field(default_factory=list)
    hibernation_options: Dict[str, Any] = field(default_factory=dict)
    hypervisor: str = ""
    iam_instance_profile: Dict[str, Any] = field(default_factory=dict)
    image_id: str = ""
    instance_id: str = ""
    instance_lifecycle: str = ""
    instance_state: Dict[str, Any] = field(default_factory=dict)
    instance_type: str = ""
    ip_address: str = ""
    ipv6_address: str = ""
    kernel_id: str = ""
    key_name: str = ""
    launch_time: str = ""
    license_set: List[Any] = field(default_factory=list)
    maintenance_options: Dict[str, Any] = field(default_factory=dict)
    metadata_options: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    network_interface_set: List[Any] = field(default_factory=list)
    network_performance_options: Dict[str, Any] = field(default_factory=dict)
    operator: Dict[str, Any] = field(default_factory=dict)
    outpost_arn: str = ""
    placement: Dict[str, Any] = field(default_factory=dict)
    platform: str = ""
    platform_details: str = ""
    private_dns_name: str = ""
    private_dns_name_options: Dict[str, Any] = field(default_factory=dict)
    private_ip_address: str = ""
    product_codes: List[Any] = field(default_factory=list)
    ramdisk_id: str = ""
    reason: str = ""
    root_device_name: str = ""
    root_device_type: str = ""
    source_dest_check: bool = False
    spot_instance_request_id: str = ""
    sriov_net_support: str = ""
    state_reason: Dict[str, Any] = field(default_factory=dict)
    subnet_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    tpm_support: str = ""
    usage_operation: str = ""
    # Has to assign a time string here to avoid invalid timestamp errors from AWS CLI
    usage_operation_update_time: str = datetime.now(timezone.utc).isoformat()
    virtualization_type: str = ""
    vpc_id: str = ""

    # Internal dependency tracking — not in API response
    bundle_task_ids: List[str] = field(default_factory=list)  # tracks BundleTask children
    elastic_graphic_ids: List[str] = field(default_factory=list)  # tracks ElasticGraphic children
    elastic_ip_addresse_ids: List[str] = field(default_factory=list)  # tracks ElasticIpAddresse children
    route_table_ids: List[str] = field(default_factory=list)  # tracks RouteTable children
    spot_instance_ids: List[str] = field(default_factory=list)  # tracks SpotInstance children

    disable_api_termination: bool = False
    disable_api_stop: bool = False
    instance_initiated_shutdown_behavior: str = ""
    user_data: str = ""
    iam_instance_profile_association: Dict[str, Any] = field(default_factory=dict)
    credit_specification: Dict[str, Any] = field(default_factory=dict)
    instance_event_schedule: Dict[str, Any] = field(default_factory=dict)
    console_output: str = ""
    console_output_timestamp: str = ""
    console_screenshot: str = ""
    uefi_data: str = ""
    password_data: str = ""
    password_data_timestamp: str = ""
    reported_status: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amiLaunchIndex": self.ami_launch_index,
            "architecture": self.architecture,
            "blockDeviceMapping": self.block_device_mapping,
            "bootMode": self.boot_mode,
            "capacityBlockId": self.capacity_block_id,
            "capacityReservationId": self.capacity_reservation_id,
            "capacityReservationSpecification": self.capacity_reservation_specification,
            "clientToken": self.client_token,
            "cpuOptions": self.cpu_options,
            "currentInstanceBootMode": self.current_instance_boot_mode,
            "dnsName": self.dns_name,
            "ebsOptimized": self.ebs_optimized,
            "elasticGpuAssociationSet": self.elastic_gpu_association_set,
            "elasticInferenceAcceleratorAssociationSet": self.elastic_inference_accelerator_association_set,
            "enaSupport": self.ena_support,
            "enclaveOptions": self.enclave_options,
            "groupSet": self.group_set,
            "hibernationOptions": self.hibernation_options,
            "hypervisor": self.hypervisor,
            "iamInstanceProfile": self.iam_instance_profile,
            "imageId": self.image_id,
            "instanceId": self.instance_id,
            "instanceLifecycle": self.instance_lifecycle,
            "instanceState": self.instance_state,
            "instanceType": self.instance_type,
            "ipAddress": self.ip_address,
            "ipv6Address": self.ipv6_address,
            "kernelId": self.kernel_id,
            "keyName": self.key_name,
            "launchTime": self.launch_time,
            "licenseSet": self.license_set,
            "maintenanceOptions": self.maintenance_options,
            "metadataOptions": self.metadata_options,
            "monitoring": self.monitoring,
            "networkInterfaceSet": self.network_interface_set,
            "networkPerformanceOptions": self.network_performance_options,
            "operator": self.operator,
            "outpostArn": self.outpost_arn,
            "placement": self.placement,
            "platform": self.platform,
            "platformDetails": self.platform_details,
            "privateDnsName": self.private_dns_name,
            "privateDnsNameOptions": self.private_dns_name_options,
            "privateIpAddress": self.private_ip_address,
            "productCodes": self.product_codes,
            "ramdiskId": self.ramdisk_id,
            "reason": self.reason,
            "rootDeviceName": self.root_device_name,
            "rootDeviceType": self.root_device_type,
            "sourceDestCheck": self.source_dest_check,
            "spotInstanceRequestId": self.spot_instance_request_id,
            "sriovNetSupport": self.sriov_net_support,
            "stateReason": self.state_reason,
            "subnetId": self.subnet_id,
            "tagSet": self.tag_set,
            "tpmSupport": self.tpm_support,
            "usageOperation": self.usage_operation,
            "usageOperationUpdateTime": self.usage_operation_update_time,
            "virtualizationType": self.virtualization_type,
            "vpcId": self.vpc_id,
        }

class Instance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.instances  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.capacity_reservations.get(params['capacity_reservation_id']).instance_ids.append(new_id)
    #   Delete: self.state.capacity_reservations.get(resource.capacity_reservation_id).instance_ids.remove(resource_id)
    #   Create: self.state.amis.get(params['image_id']).instance_ids.append(new_id)
    #   Delete: self.state.amis.get(resource.image_id).instance_ids.remove(resource_id)
    #   Create: self.state.spot_instances.get(params['spot_instance_request_id']).instance_ids.append(new_id)
    #   Delete: self.state.spot_instances.get(resource.spot_instance_request_id).instance_ids.remove(resource_id)
    #   Create: self.state.subnets.get(params['subnet_id']).instance_ids.append(new_id)
    #   Delete: self.state.subnets.get(resource.subnet_id).instance_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).instance_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).instance_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_or_error(self, store: Dict[str, Any], resource_id: str, code: str, message: Optional[str] = None):
        resource = store.get(resource_id) if resource_id else None
        if not resource:
            if message is None:
                message = f"The ID '{resource_id}' does not exist"
            return None, create_error_response(code, message)
        return resource, None

    def _now_isoformat(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _set_instance_state(self, instance: Instance, name: str, code: int) -> None:
        instance.instance_state = {"code": code, "name": name}

    def _ensure_store(self, attr: str) -> Dict[str, Any]:
        if not hasattr(self.state, attr):
            setattr(self.state, attr, {})
        return getattr(self.state, attr)

    def _build_sip_config(self, status: Optional[str], config: Any) -> Dict[str, Any]:
        config_values = config if isinstance(config, dict) else {}
        return {
            "appleInternal": config_values.get("appleInternal") or config_values.get("AppleInternal"),
            "baseSystem": config_values.get("baseSystem") or config_values.get("BaseSystem"),
            "debuggingRestrictions": config_values.get("debuggingRestrictions") or config_values.get("DebuggingRestrictions"),
            "dTraceRestrictions": config_values.get("dTraceRestrictions") or config_values.get("DTraceRestrictions"),
            "filesystemProtections": config_values.get("filesystemProtections") or config_values.get("FilesystemProtections"),
            "kextSigning": config_values.get("kextSigning") or config_values.get("KextSigning"),
            "nvramProtections": config_values.get("nvramProtections") or config_values.get("NvramProtections"),
            "status": status,
        }


    def AssociateIamInstanceProfile(self, params: Dict[str, Any]):
        """Associates an IAM instance profile with a running or stopped instance. You cannot
            associate more than one IAM instance profile with an instance."""

        error = self._require_params(params, ["IamInstanceProfile", "InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        if instance.iam_instance_profile_association:
            return create_error_response("IncorrectState", "Instance already has an associated IAM instance profile.")

        profile = params.get("IamInstanceProfile") or {}
        association = {
            "associationId": self._generate_id("iip-assoc"),
            "iamInstanceProfile": profile,
            "instanceId": instance.instance_id or instance_id,
            "state": "associated",
            "timestamp": self._now_isoformat(),
        }
        instance.iam_instance_profile = profile if isinstance(profile, dict) else {}
        instance.iam_instance_profile_association = association

        return {
            'iamInstanceProfileAssociation': association,
            }

    def CreateDelegateMacVolumeOwnershipTask(self, params: Dict[str, Any]):
        """Delegates ownership of the Amazon EBS root volume for an Apple silicon 
         Mac instance to an administrative user."""

        error = self._require_params(params, ["InstanceId", "MacCredentials"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set: List[Dict[str, Any]] = []
        for spec in tag_specs:
            tag_set.extend(spec.get("Tags", []) or [])

        task_id = self._generate_id("mmt")
        start_time = self._now_isoformat()
        task = {
            "instanceId": instance.instance_id or instance_id,
            "macModificationTaskId": task_id,
            "macSystemIntegrityProtectionConfig": self._build_sip_config(None, None),
            "startTime": start_time,
            "tagSet": tag_set,
            "taskState": "pending",
            "taskType": "volume-ownership-delegation",
        }
        store = self._ensure_store("mac_modification_tasks")
        store[task_id] = task

        return {
            'macModificationTask': task,
            }

    def CreateMacSystemIntegrityProtectionModificationTask(self, params: Dict[str, Any]):
        """Creates a System Integrity Protection (SIP) modification task to configure the SIP settings 
         for an x86 Mac instance or Apple silicon Mac instance. For more information, seeConfigure SIP for Amazon EC2 instancesin theAmazon EC2 User Guide. When you configure the SIP settings for your instan"""

        error = self._require_params(params, ["InstanceId", "MacSystemIntegrityProtectionStatus"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set: List[Dict[str, Any]] = []
        for spec in tag_specs:
            tag_set.extend(spec.get("Tags", []) or [])

        task_id = self._generate_id("mmt")
        start_time = self._now_isoformat()
        status = params.get("MacSystemIntegrityProtectionStatus") or ""
        config = params.get("MacSystemIntegrityProtectionConfiguration")
        task = {
            "instanceId": instance.instance_id or instance_id,
            "macModificationTaskId": task_id,
            "macSystemIntegrityProtectionConfig": self._build_sip_config(status, config),
            "startTime": start_time,
            "tagSet": tag_set,
            "taskState": "pending",
            "taskType": "sip-modification",
        }
        store = self._ensure_store("mac_modification_tasks")
        store[task_id] = task

        return {
            'macModificationTask': task,
            }

    def DescribeIamInstanceProfileAssociations(self, params: Dict[str, Any]):
        """Describes your IAM instance profile associations."""

        association_ids = params.get("AssociationId.N", []) or []
        associations: List[Dict[str, Any]] = []
        for instance in self.resources.values():
            association = getattr(instance, "iam_instance_profile_association", None) or {}
            if association.get("associationId"):
                associations.append(association)

        if association_ids:
            existing_ids = {assoc.get("associationId") for assoc in associations}
            for association_id in association_ids:
                if association_id not in existing_ids:
                    return create_error_response("InvalidIamInstanceProfileAssociationId.NotFound", f"The ID '{association_id}' does not exist")
            associations = [assoc for assoc in associations if assoc.get("associationId") in association_ids]

        associations = apply_filters(associations, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        start = int(params.get("NextToken") or 0)
        end = start + max_results
        page = associations[start:end]
        next_token = str(end) if end < len(associations) else None

        return {
            'iamInstanceProfileAssociationSet': page,
            'nextToken': next_token,
            }

    def DescribeInstanceAttribute(self, params: Dict[str, Any]):
        """Describes the specified attribute of the specified instance. You can specify only one
            attribute at a time. Available attributes include SQL license exemption configuration
            for instances registered with the SQL LE service."""

        error = self._require_params(params, ["Attribute", "InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        attribute = params.get("Attribute") or ""
        response = {
            'blockDeviceMapping': instance.block_device_mapping,
            'disableApiStop': {
                'Value': instance.disable_api_stop,
                },
            'disableApiTermination': {
                'Value': instance.disable_api_termination,
                },
            'ebsOptimized': {
                'Value': instance.ebs_optimized,
                },
            'enaSupport': {
                'Value': instance.ena_support,
                },
            'enclaveOptions': {
                'enabled': (instance.enclave_options or {}).get("enabled"),
                },
            'groupSet': instance.group_set,
            'instanceId': instance.instance_id or instance_id,
            'instanceInitiatedShutdownBehavior': {
                'Value': instance.instance_initiated_shutdown_behavior,
                },
            'instanceType': {
                'Value': instance.instance_type,
                },
            'kernel': {
                'Value': instance.kernel_id,
                },
            'productCodes': instance.product_codes,
            'ramdisk': {
                'Value': instance.ramdisk_id,
                },
            'rootDeviceName': {
                'Value': instance.root_device_name,
                },
            'sourceDestCheck': {
                'Value': instance.source_dest_check,
                },
            'sriovNetSupport': {
                'Value': instance.sriov_net_support,
                },
            'userData': {
                'Value': instance.user_data,
                },
            }

        attribute_map = {
            "blockdevicemapping": "blockDeviceMapping",
            "disableapistop": "disableApiStop",
            "disableaptermination": "disableApiTermination",
            "ebsoptimized": "ebsOptimized",
            "enasupport": "enaSupport",
            "enclaveoptions": "enclaveOptions",
            "groupset": "groupSet",
            "groupSet": "groupSet",
            "instanceinitiatedshutdownbehavior": "instanceInitiatedShutdownBehavior",
            "instancetype": "instanceType",
            "kernel": "kernel",
            "productcodes": "productCodes",
            "ramdisk": "ramdisk",
            "rootdevicename": "rootDeviceName",
            "sourcedestcheck": "sourceDestCheck",
            "sriovnetsupport": "sriovNetSupport",
            "userdata": "userData",
        }
        attribute_key = attribute_map.get(attribute.replace("-", "").lower())
        if attribute_key:
            value = response.get(attribute_key)
            return {
                'blockDeviceMapping': None,
                'disableApiStop': None,
                'disableApiTermination': None,
                'ebsOptimized': None,
                'enaSupport': None,
                'enclaveOptions': None,
                'groupSet': None,
                'instanceId': instance.instance_id or instance_id,
                'instanceInitiatedShutdownBehavior': None,
                'instanceType': None,
                'kernel': None,
                'productCodes': None,
                'ramdisk': None,
                'rootDeviceName': None,
                'sourceDestCheck': None,
                'sriovNetSupport': None,
                'userData': None,
                **{attribute_key: value},
            }

        return response

    def DescribeInstanceCreditSpecifications(self, params: Dict[str, Any]):
        """Describes the credit option for CPU usage of the specified burstable performance
            instances. The credit options arestandardandunlimited. If you do not specify an instance ID, Amazon EC2 returns burstable performance
            instances with theunlimitedcredit option, as well as instance"""

        instance_ids = params.get("InstanceId.N", []) or []
        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances = list(self.resources.values())
        if instance_ids:
            instances = [inst for inst in instances if inst.instance_id in instance_ids]

        specs = []
        for inst in instances:
            spec = inst.credit_specification or {}
            cpu_credits = spec.get("CpuCredits") or spec.get("cpuCredits") or "standard"
            specs.append({"cpuCredits": cpu_credits, "instanceId": inst.instance_id})

        specs = apply_filters(specs, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        start = int(params.get("NextToken") or 0)
        end = start + max_results
        page = specs[start:end]
        next_token = str(end) if end < len(specs) else None

        return {
            'instanceCreditSpecificationSet': page,
            'nextToken': next_token,
            }

    def DescribeInstances(self, params: Dict[str, Any]):
        """Describes the specified instances or all instances. If you specify instance IDs, the output includes information for only the specified
            instances. If you specify filters, the output includes information for only those
            instances that meet the filter criteria. If you do not spe"""

        instance_ids = params.get("InstanceId.N", []) or []
        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances = list(self.resources.values())
        if instance_ids:
            instances = [inst for inst in instances if inst.instance_id in instance_ids]

        instances = apply_filters(instances, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        start = int(params.get("NextToken") or 0)
        end = start + max_results
        page_instances = instances[start:end]
        next_token = str(end) if end < len(instances) else None

        reservation = {
            "groupSet": [],
            "instancesSet": [inst.to_dict() for inst in page_instances],
            "ownerId": "",
            "requesterId": "",
            "reservationId": "",
        }

        return {
            'nextToken': next_token,
            'reservationSet': [reservation],
            }

    def DescribeInstanceStatus(self, params: Dict[str, Any]):
        """Describes the status of the specified instances or all of your instances. By default,
            only running instances are described, unless you specifically indicate to return the
            status of all instances. Instance status includes the following components: Status checks- Amazon EC2 per"""

        instance_ids = params.get("InstanceId.N", []) or []
        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances = list(self.resources.values())
        if instance_ids:
            instances = [inst for inst in instances if inst.instance_id in instance_ids]

        include_all = str2bool(params.get("IncludeAllInstances"))
        if not include_all:
            instances = [inst for inst in instances if (inst.instance_state or {}).get("name") == "running"]

        status_items = []
        for inst in instances:
            status_items.append({
                "attachedEbsStatus": "attached",
                "availabilityZone": (inst.placement or {}).get("availabilityZone", ""),
                "availabilityZoneId": (inst.placement or {}).get("availabilityZoneId", ""),
                "eventsSet": [],
                "instanceId": inst.instance_id,
                "instanceState": inst.instance_state,
                "instanceStatus": {"details": [], "status": "ok"},
                "operator": inst.operator,
                "outpostArn": inst.outpost_arn,
                "systemStatus": {"details": [], "status": "ok"},
            })

        status_items = apply_filters(status_items, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        start = int(params.get("NextToken") or 0)
        end = start + max_results
        page = status_items[start:end]
        next_token = str(end) if end < len(status_items) else None

        return {
            'instanceStatusSet': page,
            'nextToken': next_token,
            }

    def DisassociateIamInstanceProfile(self, params: Dict[str, Any]):
        """Disassociates an IAM instance profile from a running or stopped instance. UseDescribeIamInstanceProfileAssociationsto get the association
            ID."""

        error = self._require_params(params, ["AssociationId"])
        if error:
            return error

        association_id = params.get("AssociationId") or ""
        target_instance = None
        target_association = None
        for instance in self.resources.values():
            association = instance.iam_instance_profile_association
            if association and association.get("associationId") == association_id:
                target_instance = instance
                target_association = association
                break

        if not target_association:
            return create_error_response("InvalidIamInstanceProfileAssociationId.NotFound", f"The ID '{association_id}' does not exist")

        target_instance.iam_instance_profile = {}
        target_instance.iam_instance_profile_association = {}
        disassociated = {
            "associationId": association_id,
            "iamInstanceProfile": target_association.get("iamInstanceProfile", {}),
            "instanceId": target_instance.instance_id,
            "state": "disassociated",
            "timestamp": self._now_isoformat(),
        }

        return {
            'iamInstanceProfileAssociation': disassociated,
            }

    def GetConsoleOutput(self, params: Dict[str, Any]):
        """Gets the console output for the specified instance. For Linux instances, the instance
            console output displays the exact console output that would normally be displayed on a
            physical monitor attached to a computer. For Windows instances, the instance console
            output"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        output = instance.console_output
        timestamp = instance.console_output_timestamp
        if not output:
            output = ""
            timestamp = self._now_isoformat()
            instance.console_output = output
            instance.console_output_timestamp = timestamp

        return {
            'instanceId': instance.instance_id or instance_id,
            'output': output,
            'timestamp': timestamp,
            }

    def GetConsoleScreenshot(self, params: Dict[str, Any]):
        """Retrieve a JPG-format screenshot of a running instance to help with
            troubleshooting. The returned content is Base64-encoded. For more information, seeInstance console outputin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        image_data = instance.console_screenshot
        if not image_data:
            image_data = ""
            instance.console_screenshot = image_data

        return {
            'imageData': image_data,
            'instanceId': instance.instance_id or instance_id,
            }

    def GetDefaultCreditSpecification(self, params: Dict[str, Any]):
        """Describes the default credit option for CPU usage of a burstable performance instance
            family. For more information, seeBurstable
                performance instancesin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["InstanceFamily"])
        if error:
            return error

        instance_family = params.get("InstanceFamily") or ""
        defaults = self._ensure_store("default_credit_specifications")
        cpu_credits = defaults.get(instance_family, "standard")

        return {
            'instanceFamilyCreditSpecification': {
                'cpuCredits': cpu_credits,
                'instanceFamily': instance_family,
                },
            }

    def GetInstanceMetadataDefaults(self, params: Dict[str, Any]):
        """Gets the default instance metadata service (IMDS) settings that are set at the account
            level in the specified AWS  Region. For more information, seeOrder of precedence for instance metadata optionsin theAmazon EC2 User Guide."""

        defaults = self._ensure_store("instance_metadata_defaults")

        return {
            'accountLevel': {
                'httpEndpoint': defaults.get("httpEndpoint"),
                'httpPutResponseHopLimit': defaults.get("httpPutResponseHopLimit"),
                'httpTokens': defaults.get("httpTokens"),
                'instanceMetadataTags': defaults.get("instanceMetadataTags"),
                'managedBy': defaults.get("managedBy"),
                'managedExceptionMessage': defaults.get("managedExceptionMessage"),
                },
            }

    def GetInstanceUefiData(self, params: Dict[str, Any]):
        """A binary representation of the UEFI variable store. Only non-volatile variables are
            stored. This is a base64 encoded and zlib compressed binary value that must be properly
            encoded. When you useregister-imageto create
            an AMI, you can create an exact copy of your va"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        uefi_data = instance.uefi_data
        if not uefi_data:
            uefi_data = ""
            instance.uefi_data = uefi_data

        return {
            'instanceId': instance.instance_id or instance_id,
            'uefiData': uefi_data,
            }

    def GetPasswordData(self, params: Dict[str, Any]):
        """Retrieves the encrypted administrator password for a running Windows instance. The Windows password is generated at boot by theEC2Configservice orEC2Launchscripts (Windows Server 2016 and later). This usually only
            happens the first time an instance is launched. For more information, seeE"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        password_data = instance.password_data
        timestamp = instance.password_data_timestamp
        if password_data is None:
            password_data = ""
            timestamp = self._now_isoformat()
            instance.password_data = password_data
            instance.password_data_timestamp = timestamp

        return {
            'instanceId': instance.instance_id or instance_id,
            'passwordData': password_data,
            'timestamp': timestamp,
            }

    def ModifyDefaultCreditSpecification(self, params: Dict[str, Any]):
        """Modifies the default credit option for CPU usage of burstable performance instances.
            The default credit option is set at the account level per AWS Region, and
            is specified per instance family. All new burstable performance instances in the account
            launch using the"""

        error = self._require_params(params, ["CpuCredits", "InstanceFamily"])
        if error:
            return error

        cpu_credits = params.get("CpuCredits") or ""
        instance_family = params.get("InstanceFamily") or ""
        defaults = self._ensure_store("default_credit_specifications")
        defaults[instance_family] = cpu_credits

        return {
            'instanceFamilyCreditSpecification': {
                'cpuCredits': cpu_credits,
                'instanceFamily': instance_family,
                },
            }

    def ModifyInstanceAttribute(self, params: Dict[str, Any]):
        """Modifies the specified attribute of the specified instance. You can specify only one
            attribute at a time. Note:Using this action to change the security groups
            associated with an elastic network interface (ENI) attached to an instance can
            result in an error if the """

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        group_ids = params.get("GroupId.N", []) or []
        if group_ids:
            group_set = []
            for group_id in group_ids:
                group = self.state.security_groups.get(group_id)
                if not group:
                    return create_error_response("InvalidSecurityGroupID.NotFound", f"Security group '{group_id}' does not exist.")
                group_set.append({"GroupId": group_id, "GroupName": getattr(group, "group_name", "")})
            instance.group_set = group_set

        block_device_mapping = params.get("BlockDeviceMapping.N", [])
        if block_device_mapping:
            instance.block_device_mapping = block_device_mapping

        if params.get("DisableApiStop") is not None:
            instance.disable_api_stop = str2bool(params.get("DisableApiStop"))
        if params.get("DisableApiTermination") is not None:
            instance.disable_api_termination = str2bool(params.get("DisableApiTermination"))
        if params.get("EbsOptimized") is not None:
            instance.ebs_optimized = str2bool(params.get("EbsOptimized"))
        if params.get("EnaSupport") is not None:
            instance.ena_support = str2bool(params.get("EnaSupport"))
        if params.get("InstanceInitiatedShutdownBehavior"):
            instance.instance_initiated_shutdown_behavior = params.get("InstanceInitiatedShutdownBehavior") or ""
        if params.get("InstanceType"):
            instance.instance_type = params.get("InstanceType") or ""
        if params.get("Kernel"):
            instance.kernel_id = params.get("Kernel") or ""
        if params.get("Ramdisk"):
            instance.ramdisk_id = params.get("Ramdisk") or ""
        if params.get("SourceDestCheck") is not None:
            instance.source_dest_check = str2bool(params.get("SourceDestCheck"))
        if params.get("SriovNetSupport"):
            instance.sriov_net_support = params.get("SriovNetSupport") or ""
        if params.get("UserData"):
            instance.user_data = params.get("UserData") or ""

        attribute = params.get("Attribute") or ""
        value = params.get("Value")
        attribute_map = {
            "instanceinitiatedshutdownbehavior": "instance_initiated_shutdown_behavior",
            "instancetype": "instance_type",
            "kernel": "kernel_id",
            "ramdisk": "ramdisk_id",
            "sriovnetsupport": "sriov_net_support",
            "userdata": "user_data",
        }
        normalized = attribute.replace("-", "").lower()
        if normalized in ("disableapitermination", "disableapistop", "ebsoptimized", "enasupport", "sourcedestcheck") and value is not None:
            bool_value = str2bool(value)
            if normalized == "disableapitermination":
                instance.disable_api_termination = bool_value
            elif normalized == "disableapistop":
                instance.disable_api_stop = bool_value
            elif normalized == "ebsoptimized":
                instance.ebs_optimized = bool_value
            elif normalized == "enasupport":
                instance.ena_support = bool_value
            elif normalized == "sourcedestcheck":
                instance.source_dest_check = bool_value
        elif normalized in attribute_map and value is not None:
            setattr(instance, attribute_map[normalized], value)

        return {
            'return': True,
            }

    def ModifyInstanceCpuOptions(self, params: Dict[str, Any]):
        """By default, all vCPUs for the instance type are active when you launch an instance. When you 
			configure the number of active vCPUs for the instance, it can help you save on licensing costs and 
			optimize performance. The base cost of the instance remains unchanged. The number of active vCPUs eq"""

        error = self._require_params(params, ["CoreCount", "InstanceId", "ThreadsPerCore"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        core_count = int(params.get("CoreCount") or 0)
        threads_per_core = int(params.get("ThreadsPerCore") or 0)
        instance.cpu_options = {
            "coreCount": core_count,
            "threadsPerCore": threads_per_core,
        }

        return {
            'coreCount': core_count,
            'instanceId': instance.instance_id or instance_id,
            'threadsPerCore': threads_per_core,
            }

    def ModifyInstanceCreditSpecification(self, params: Dict[str, Any]):
        """Modifies the credit option for CPU usage on a running or stopped burstable performance
            instance. The credit options arestandardandunlimited. For more information, seeBurstable
                performance instancesin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["InstanceCreditSpecification.N"])
        if error:
            return error

        specifications = params.get("InstanceCreditSpecification.N", []) or []
        successful = []
        unsuccessful = []

        for spec in specifications:
            instance_id = spec.get("InstanceId") or spec.get("instanceId") or ""
            cpu_credits = spec.get("CpuCredits") or spec.get("cpuCredits") or ""
            if not instance_id:
                unsuccessful.append({
                    "instanceId": instance_id,
                    "error": {
                        "code": "MissingParameter",
                        "message": "Missing required parameter: InstanceId",
                    },
                })
                continue

            instance = self.resources.get(instance_id)
            if not instance:
                unsuccessful.append({
                    "instanceId": instance_id,
                    "error": {
                        "code": "InvalidInstanceID.NotFound",
                        "message": f"The ID '{instance_id}' does not exist",
                    },
                })
                continue

            if cpu_credits:
                instance.credit_specification = {"cpuCredits": cpu_credits}
            successful.append({"instanceId": instance_id})

        return {
            'successfulInstanceCreditSpecificationSet': successful,
            'unsuccessfulInstanceCreditSpecificationSet': unsuccessful,
            }

    def ModifyInstanceEventStartTime(self, params: Dict[str, Any]):
        """Modifies the start time for a scheduled Amazon EC2 instance event."""

        error = self._require_params(params, ["InstanceEventId", "InstanceId", "NotBefore"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        instance_event_id = params.get("InstanceEventId") or ""
        not_before = params.get("NotBefore") or ""

        event = {
            "code": "instance-reboot",
            "description": "Instance event scheduled",
            "instanceEventId": instance_event_id,
            "notAfter": "",
            "notBefore": not_before,
            "notBeforeDeadline": "",
        }
        instance.instance_event_schedule = event

        return {
            'event': event,
            }

    def ModifyInstanceMaintenanceOptions(self, params: Dict[str, Any]):
        """Modifies the recovery behavior of your instance to disable simplified automatic
            recovery or set the recovery behavior to default. The default configuration will not
            enable simplified automatic recovery for an unsupported instance type. For more
            information, seeSim"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        auto_recovery = params.get("AutoRecovery")
        reboot_migration = params.get("RebootMigration")
        if auto_recovery is not None:
            instance.maintenance_options["autoRecovery"] = auto_recovery
        if reboot_migration is not None:
            instance.maintenance_options["rebootMigration"] = reboot_migration

        return {
            'autoRecovery': instance.maintenance_options.get("autoRecovery"),
            'instanceId': instance.instance_id or instance_id,
            'rebootMigration': instance.maintenance_options.get("rebootMigration"),
            }

    def ModifyInstanceMetadataDefaults(self, params: Dict[str, Any]):
        """Modifies the default instance metadata service (IMDS) settings at the account level in
            the specified AWS  Region. To remove a parameter's account-level default setting, specifyno-preference. If an account-level setting is cleared withno-preference, then the instance launch considers the """

        defaults = self._ensure_store("instance_metadata_defaults")

        if params.get("HttpEndpoint") is not None:
            defaults["httpEndpoint"] = params.get("HttpEndpoint")
        if params.get("HttpPutResponseHopLimit") is not None:
            defaults["httpPutResponseHopLimit"] = params.get("HttpPutResponseHopLimit")
        if params.get("HttpTokens") is not None:
            defaults["httpTokens"] = params.get("HttpTokens")
        if params.get("InstanceMetadataTags") is not None:
            defaults["instanceMetadataTags"] = params.get("InstanceMetadataTags")

        return {
            'return': True,
            }

    def ModifyInstanceMetadataOptions(self, params: Dict[str, Any]):
        """Modify the instance metadata parameters on a running or stopped instance. When you
            modify the parameters on a stopped instance, they are applied when the instance is
            started. When you modify the parameters on a running instance, the API responds with a
            state of â"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        if params.get("HttpEndpoint") is not None:
            instance.metadata_options["httpEndpoint"] = params.get("HttpEndpoint")
        if params.get("HttpProtocolIpv6") is not None:
            instance.metadata_options["httpProtocolIpv6"] = params.get("HttpProtocolIpv6")
        if params.get("HttpPutResponseHopLimit") is not None:
            instance.metadata_options["httpPutResponseHopLimit"] = params.get("HttpPutResponseHopLimit")
        if params.get("HttpTokens") is not None:
            instance.metadata_options["httpTokens"] = params.get("HttpTokens")
        if params.get("InstanceMetadataTags") is not None:
            instance.metadata_options["instanceMetadataTags"] = params.get("InstanceMetadataTags")

        metadata = instance.metadata_options
        return {
            'instanceId': instance.instance_id or instance_id,
            'instanceMetadataOptions': {
                'httpEndpoint': metadata.get("httpEndpoint"),
                'httpProtocolIpv6': metadata.get("httpProtocolIpv6"),
                'httpPutResponseHopLimit': metadata.get("httpPutResponseHopLimit"),
                'httpTokens': metadata.get("httpTokens"),
                'instanceMetadataTags': metadata.get("instanceMetadataTags"),
                'state': "applied",
                },
            }

    def ModifyInstanceNetworkPerformanceOptions(self, params: Dict[str, Any]):
        """Change the configuration of the network performance options for an existing 
            instance."""

        error = self._require_params(params, ["BandwidthWeighting", "InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        bandwidth_weighting = params.get("BandwidthWeighting") or ""
        instance.network_performance_options["bandwidthWeighting"] = bandwidth_weighting

        return {
            'bandwidthWeighting': bandwidth_weighting,
            'instanceId': instance.instance_id or instance_id,
            }

    def ModifyPrivateDnsNameOptions(self, params: Dict[str, Any]):
        """Modifies the options for instance hostnames for the specified instance."""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        if params.get("EnableResourceNameDnsAAAARecord") is not None:
            instance.private_dns_name_options["enableResourceNameDnsAAAARecord"] = str2bool(
                params.get("EnableResourceNameDnsAAAARecord")
            )
        if params.get("EnableResourceNameDnsARecord") is not None:
            instance.private_dns_name_options["enableResourceNameDnsARecord"] = str2bool(
                params.get("EnableResourceNameDnsARecord")
            )
        if params.get("PrivateDnsHostnameType") is not None:
            instance.private_dns_name_options["privateDnsHostnameType"] = params.get("PrivateDnsHostnameType")

        return {
            'return': True,
            }

    def ModifyPublicIpDnsNameOptions(self, params: Dict[str, Any]):
        """Modify public hostname options for a network interface. For more information, seeEC2 instance hostnames, DNS names, and domainsin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["HostnameType", "NetworkInterfaceId"])
        if error:
            return error

        network_interface_id = params.get("NetworkInterfaceId") or ""
        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            return create_error_response("InvalidNetworkInterfaceID.NotFound", f"Network interface '{network_interface_id}' does not exist.")

        hostname_type = params.get("HostnameType") or ""
        if isinstance(eni, dict):
            eni["publicHostnameType"] = hostname_type
        else:
            setattr(eni, "public_hostname_type", hostname_type)

        return {
            'successful': True,
            }

    def MonitorInstances(self, params: Dict[str, Any]):
        """Enables detailed monitoring for a running instance. Otherwise, basic monitoring is
            enabled. For more information, seeMonitor your instances using
                CloudWatchin theAmazon EC2 User Guide. To disable detailed monitoring, seeUnmonitorInstances."""

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            instance.monitoring = {"state": "enabled"}
            instances_set.append({"instanceId": instance_id, "monitoring": instance.monitoring})

        return {
            'instancesSet': instances_set,
            }

    def RebootInstances(self, params: Dict[str, Any]):
        """Requests a reboot of the specified instances. This operation is asynchronous; it only
            queues a request to reboot the specified instances. The operation succeeds if the
            instances are valid and belong to you. Requests to reboot terminated instances are
            ignored. If a"""

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            if (instance.instance_state or {}).get("name") == "terminated":
                continue
            instance.state_reason = {"message": "reboot-initiated"}

        return {
            'return': True,
            }

    def ReplaceIamInstanceProfileAssociation(self, params: Dict[str, Any]):
        """Replaces an IAM instance profile for the specified running instance. You can use
            this action to change the IAM instance profile that's associated with an instance
            without having to disassociate the existing IAM instance profile first. UseDescribeIamInstanceProfileAssociations"""

        error = self._require_params(params, ["AssociationId", "IamInstanceProfile"])
        if error:
            return error

        association_id = params.get("AssociationId") or ""
        profile = params.get("IamInstanceProfile") or {}

        target_instance = None
        for instance in self.resources.values():
            association = instance.iam_instance_profile_association
            if association and association.get("associationId") == association_id:
                target_instance = instance
                break

        if not target_instance:
            return create_error_response("InvalidIamInstanceProfileAssociationId.NotFound", f"The ID '{association_id}' does not exist")

        association = {
            "associationId": association_id,
            "iamInstanceProfile": profile,
            "instanceId": target_instance.instance_id,
            "state": "associated",
            "timestamp": self._now_isoformat(),
        }
        target_instance.iam_instance_profile = profile if isinstance(profile, dict) else {}
        target_instance.iam_instance_profile_association = association

        return {
            'iamInstanceProfileAssociation': association,
            }

    def ReportInstanceStatus(self, params: Dict[str, Any]):
        """Submits feedback about the status of an instance. The instance must be in therunningstate. If your experience with the instance differs from the
            instance status returned byDescribeInstanceStatus, use ReportInstanceStatus to report your experience with the instance. Amazon
            EC2"""

        error = self._require_params(params, ["InstanceId.N", "ReasonCode.N", "Status"])
        if error:
            return error

        instance_ids = params.get("InstanceId.N", []) or []
        reason_codes = params.get("ReasonCode.N", []) or []
        status = params.get("Status") or ""

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            if (instance.instance_state or {}).get("name") != "running":
                return create_error_response("IncorrectInstanceState", "Instance must be running to report status.")
            instance.reported_status = {
                "description": params.get("Description") or "",
                "endTime": params.get("EndTime") or "",
                "startTime": params.get("StartTime") or "",
                "reasonCodes": reason_codes,
                "status": status,
            }

        return {
            'return': True,
            }

    def ResetInstanceAttribute(self, params: Dict[str, Any]):
        """Resets an attribute of an instance to its default value. To reset thekernelorramdisk, the instance must be in a stopped
            state. To reset thesourceDestCheck, the instance can be either running or
            stopped. ThesourceDestCheckattribute controls whether source/destination
         """

        error = self._require_params(params, ["Attribute", "InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        attribute = params.get("Attribute") or ""
        normalized = attribute.replace("-", "").lower()
        if normalized in ("kernel", "ramdisk"):
            if (instance.instance_state or {}).get("name") != "stopped":
                return create_error_response("IncorrectInstanceState", "Instance must be stopped to reset kernel or ramdisk.")

        if normalized == "kernel":
            instance.kernel_id = ""
        elif normalized == "ramdisk":
            instance.ramdisk_id = ""
        elif normalized == "sourcedestcheck":
            instance.source_dest_check = False
        elif normalized == "disableapitermination":
            instance.disable_api_termination = False
        elif normalized == "disableapistop":
            instance.disable_api_stop = False
        elif normalized == "instanceinitiatedshutdownbehavior":
            instance.instance_initiated_shutdown_behavior = ""
        elif normalized == "instancetype":
            instance.instance_type = ""
        elif normalized == "userdata":
            instance.user_data = ""

        return {
            'return': True,
            }

    def RunInstances(self, params: Dict[str, Any]):
        """Launches the specified number of instances using an AMI for which you have
            permissions. You can specify a number of options, or leave the default options. The following rules
            apply: If you don't specify a subnet ID, we choose a default subnet from
                    your def"""

        error = self._require_params(params, ["MaxCount", "MinCount"])
        if error:
            return error

        max_count = int(params.get("MaxCount") or 0)
        min_count = int(params.get("MinCount") or 0)
        if max_count < min_count:
            return create_error_response("InvalidParameterValue", "MaxCount must be greater than or equal to MinCount")

        image_id = params.get("ImageId") or ""
        if image_id and image_id not in self.state.amis:
            return create_error_response("InvalidAMIID.NotFound", f"AMI '{image_id}' does not exist.")

        subnet_id = params.get("SubnetId") or ""

        capacity_spec = params.get("CapacityReservationSpecification") or {}
        capacity_reservation_id = ""
        if isinstance(capacity_spec, dict):
            capacity_reservation_id = capacity_spec.get("CapacityReservationId") or ""
        elif isinstance(capacity_spec, str):
            capacity_reservation_id = capacity_spec
        if capacity_reservation_id and capacity_reservation_id not in self.state.capacity_reservations:
            return create_error_response("InvalidCapacityReservationId.NotFound", f"Capacity Reservation '{capacity_reservation_id}' does not exist.")

        subnet = None
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        vpc_id = subnet.vpc_id if subnet else ""
        if vpc_id and vpc_id not in self.state.vpcs:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        key_name = params.get("KeyName") or ""
        if key_name:
            kp_match = next(
                (kp for kp in self.state.key_pairs.values() if getattr(kp, "key_name", "") == key_name),
                None,
            )
            if not kp_match:
                return create_error_response("InvalidKeyPair.NotFound", f"Key pair '{key_name}' does not exist.")

        instance_type = params.get("InstanceType") or ""
        if instance_type and self.state.instance_types:
            it_match = self.state.instance_types.get(instance_type) or next(
                (t for t in self.state.instance_types.values() if getattr(t, "instance_type", "") == instance_type),
                None,
            )
            if not it_match:
                return create_error_response(
                    "InvalidInstanceType.NotFound",
                    f"The instance type '{instance_type}' does not exist",
                )

        group_set: List[Dict[str, Any]] = []
        security_group_ids = params.get("SecurityGroupId.N", []) or []
        for group_id in security_group_ids:
            group = self.state.security_groups.get(group_id)
            if not group:
                return create_error_response("InvalidSecurityGroupID.NotFound", f"Security group '{group_id}' does not exist.")
            group_set.append({"GroupId": group_id, "GroupName": getattr(group, "group_name", "")})

        security_group_names = params.get("SecurityGroup.N", []) or []
        if security_group_names:
            all_groups = list(self.state.security_groups.values())
            for name in security_group_names:
                match = next((g for g in all_groups if getattr(g, "group_name", "") == name), None)
                if not match:
                    return create_error_response("InvalidGroup.NotFound", f"Security group '{name}' does not exist.")
                group_set.append({"GroupId": getattr(match, "group_id", ""), "GroupName": name})

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set: List[Dict[str, Any]] = []
        for spec in tag_specs:
            resource_type = spec.get("ResourceType")
            if resource_type and resource_type != "instance":
                continue
            tag_set.extend(spec.get("Tags", []) or [])

        monitoring_value = params.get("Monitoring") or ""
        monitoring_state = ""
        if monitoring_value:
            monitoring_state = "enabled" if str(monitoring_value).lower() in ("true", "1", "enabled") else "disabled"
        monitoring = {"state": monitoring_state} if monitoring_state else {}

        credit_spec = params.get("CreditSpecification") or {}
        cpu_options = params.get("CpuOptions") or {}
        metadata_options = params.get("MetadataOptions") or {}
        network_perf_options = params.get("NetworkPerformanceOptions") or {}
        private_dns_options = params.get("PrivateDnsNameOptions") or {}
        maintenance_options = params.get("MaintenanceOptions") or {}
        hibernation_options = params.get("HibernationOptions") or {}
        enclave_options = params.get("EnclaveOptions") or {}
        placement = params.get("Placement") or {}
        iam_instance_profile = params.get("IamInstanceProfile") or {}
        block_device_mapping = params.get("BlockDeviceMapping.N", []) or []
        elastic_gpu_association_set = params.get("ElasticGpuSpecification.N", []) or []
        elastic_inference_association_set = params.get("ElasticInferenceAccelerator.N", []) or []
        network_interface_set = params.get("NetworkInterface.N", []) or []
        license_set = params.get("LicenseSpecification.N", []) or []
        ipv6_addresses = params.get("Ipv6Address.N", []) or []

        launch_time = self._now_isoformat()
        instances = []
        reservation_id = self._generate_id("r")
        for _ in range(max_count):
            instance_id = self._generate_id("i")
            instance = Instance(
                ami_launch_index=0,
                block_device_mapping=block_device_mapping,
                capacity_reservation_id=capacity_reservation_id,
                capacity_reservation_specification=capacity_spec if isinstance(capacity_spec, dict) else {},
                client_token=params.get("ClientToken") or "",
                cpu_options=cpu_options,
                ebs_optimized=str2bool(params.get("EbsOptimized")),
                elastic_gpu_association_set=elastic_gpu_association_set,
                elastic_inference_accelerator_association_set=elastic_inference_association_set,
                ena_support=str2bool(params.get("EnablePrimaryIpv6")),
                enclave_options=enclave_options,
                group_set=group_set,
                hibernation_options=hibernation_options,
                iam_instance_profile=iam_instance_profile,
                image_id=image_id,
                instance_id=instance_id,
                instance_state={"code": 16, "name": "running"},
                instance_type=params.get("InstanceType") or "",
                ipv6_address=ipv6_addresses[0] if ipv6_addresses else "",
                kernel_id=params.get("KernelId") or "",
                key_name=key_name,
                launch_time=launch_time,
                license_set=license_set,
                maintenance_options=maintenance_options if isinstance(maintenance_options, dict) else {},
                metadata_options=metadata_options if isinstance(metadata_options, dict) else {},
                monitoring=monitoring,
                network_interface_set=network_interface_set,
                network_performance_options=network_perf_options if isinstance(network_perf_options, dict) else {},
                operator=params.get("Operator") or {},
                placement=placement if isinstance(placement, dict) else {},
                private_dns_name_options=private_dns_options if isinstance(private_dns_options, dict) else {},
                private_ip_address=params.get("PrivateIpAddress") or "",
                ramdisk_id=params.get("RamdiskId") or "",
                subnet_id=subnet_id,
                tag_set=tag_set,
                vpc_id=vpc_id,
            )
            instance.instance_initiated_shutdown_behavior = params.get("InstanceInitiatedShutdownBehavior") or ""
            instance.disable_api_stop = str2bool(params.get("DisableApiStop"))
            instance.disable_api_termination = str2bool(params.get("DisableApiTermination"))
            instance.user_data = params.get("UserData") or ""
            instance.credit_specification = credit_spec if isinstance(credit_spec, dict) else {}

            if iam_instance_profile:
                assoc_id = self._generate_id("iip-assoc")
                association = {
                    "associationId": assoc_id,
                    "iamInstanceProfile": iam_instance_profile,
                    "instanceId": instance_id,
                    "state": "associated",
                    "timestamp": launch_time,
                }
                instance.iam_instance_profile_association = association

            if capacity_reservation_id:
                parent = self.state.capacity_reservations.get(capacity_reservation_id)
                if parent and hasattr(parent, "instance_ids"):
                    parent.instance_ids.append(instance_id)

            self.resources[instance_id] = instance

            if image_id:
                parent = self.state.amis.get(image_id)
                if parent and hasattr(parent, "instance_ids"):
                    parent.instance_ids.append(instance_id)
            if subnet_id:
                parent = self.state.subnets.get(subnet_id)
                if parent and hasattr(parent, "instance_ids"):
                    parent.instance_ids.append(instance_id)
            if vpc_id:
                parent = self.state.vpcs.get(vpc_id)
                if parent and hasattr(parent, "instance_ids"):
                    parent.instance_ids.append(instance_id)

            instances.append(instance.to_dict())

        return {
            'groupSet': group_set,
            'instancesSet': instances,
            'ownerId': "",
            'requesterId': "",
            'reservationId': reservation_id,
            }

    def SendDiagnosticInterrupt(self, params: Dict[str, Any]):
        """Sends a diagnostic interrupt to the specified Amazon EC2 instance to trigger akernel panic(on Linux instances), or ablue
                screen/stop error(on Windows instances). For
            instances based on Intel and AMD processors, the interrupt is received as anon-maskable interrupt(NMI). In"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance, error = self._get_or_error(self.resources, instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        instance.state_reason = {"message": "diagnostic-interrupt"}

        return {
            'return': True,
            }

    def StartInstances(self, params: Dict[str, Any]):
        """Starts an Amazon EBS-backed instance that you've previously stopped. Instances that use Amazon EBS volumes as their root devices can be quickly stopped and
            started. When an instance is stopped, the compute resources are released and you are not
            billed for instance usage. Howe"""

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            previous_state = instance.instance_state or {"code": 0, "name": "pending"}
            if previous_state.get("name") == "stopped":
                self._set_instance_state(instance, "running", 16)
            instances_set.append({
                "currentState": instance.instance_state,
                "instanceId": instance.instance_id,
                "previousState": previous_state,
            })

        return {
            'instancesSet': instances_set,
            }

    def StopInstances(self, params: Dict[str, Any]):
        """Stops an Amazon EBS-backed instance. You can restart your instance at any time using
            theStartInstancesAPI. For more information, seeStop and start Amazon EC2
                instancesin theAmazon EC2 User Guide. When you stop or hibernate an instance, we shut it down. By default, this in"""

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            previous_state = instance.instance_state or {"code": 0, "name": "pending"}
            if previous_state.get("name") == "running":
                self._set_instance_state(instance, "stopped", 80)
            instances_set.append({
                "currentState": instance.instance_state,
                "instanceId": instance.instance_id,
                "previousState": previous_state,
            })

        return {
            'instancesSet': instances_set,
            }

    def TerminateInstances(self, params: Dict[str, Any]):
        """Terminates (deletes) the specified instances. This operation isidempotent; if you
            terminate an instance more than once, each call succeeds. Terminating an instance is permanent and irreversible. After you terminate an instance, you can no longer connect to it, and it can't be recovered. """

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue

            if getattr(instance, 'bundle_task_ids', []):
                return create_error_response('DependencyViolation', 'Instance has dependent BundleTask(s) and cannot be deleted.')
            if getattr(instance, 'elastic_graphic_ids', []):
                return create_error_response('DependencyViolation', 'Instance has dependent ElasticGraphic(s) and cannot be deleted.')
            if getattr(instance, 'elastic_ip_addresse_ids', []):
                return create_error_response('DependencyViolation', 'Instance has dependent ElasticIpAddresse(s) and cannot be deleted.')
            if getattr(instance, 'route_table_ids', []):
                return create_error_response('DependencyViolation', 'Instance has dependent RouteTable(s) and cannot be deleted.')
            if getattr(instance, 'spot_instance_ids', []):
                return create_error_response('DependencyViolation', 'Instance has dependent SpotInstance(s) and cannot be deleted.')

            previous_state = instance.instance_state or {"code": 0, "name": "pending"}
            self._set_instance_state(instance, "terminated", 48)
            instances_set.append({
                "currentState": instance.instance_state,
                "instanceId": instance.instance_id,
                "previousState": previous_state,
            })

            parent = self.state.capacity_reservations.get(instance.capacity_reservation_id)
            if parent and hasattr(parent, 'instance_ids') and instance_id in parent.instance_ids:
                parent.instance_ids.remove(instance_id)
            parent = self.state.amis.get(instance.image_id)
            if parent and hasattr(parent, 'instance_ids') and instance_id in parent.instance_ids:
                parent.instance_ids.remove(instance_id)
            parent = self.state.spot_instances.get(instance.spot_instance_request_id)
            if parent and hasattr(parent, 'instance_ids') and instance_id in parent.instance_ids:
                parent.instance_ids.remove(instance_id)
            parent = self.state.subnets.get(instance.subnet_id)
            if parent and hasattr(parent, 'instance_ids') and instance_id in parent.instance_ids:
                parent.instance_ids.remove(instance_id)
            parent = self.state.vpcs.get(instance.vpc_id)
            if parent and hasattr(parent, 'instance_ids') and instance_id in parent.instance_ids:
                parent.instance_ids.remove(instance_id)

            del self.resources[instance_id]

        return {
            'instancesSet': instances_set,
            }

    def UnmonitorInstances(self, params: Dict[str, Any]):
        """Disables detailed monitoring for a running instance. For more information, seeMonitoring
                your instances and volumesin theAmazon EC2 User Guide."""

        instance_ids = params.get("InstanceId.N", []) or []
        if not instance_ids:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId.N")

        for instance_id in instance_ids:
            if instance_id and instance_id not in self.resources:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.resources.get(instance_id)
            if not instance:
                continue
            instance.monitoring = {"state": "disabled"}
            instances_set.append({"instanceId": instance_id, "monitoring": instance.monitoring})

        return {
            'instancesSet': instances_set,
            }

    def _generate_id(self, prefix: str = 'i') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class instance_RequestParser:
    @staticmethod
    def parse_associate_iam_instance_profile_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "IamInstanceProfile": get_scalar(md, "IamInstanceProfile"),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_create_delegate_mac_volume_ownership_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "MacCredentials": get_scalar(md, "MacCredentials"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_mac_system_integrity_protection_modification_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "MacCredentials": get_scalar(md, "MacCredentials"),
            "MacSystemIntegrityProtectionConfiguration": get_int(md, "MacSystemIntegrityProtectionConfiguration"),
            "MacSystemIntegrityProtectionStatus": get_scalar(md, "MacSystemIntegrityProtectionStatus"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_describe_iam_instance_profile_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId.N": get_indexed_list(md, "AssociationId"),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_instance_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_describe_instance_credit_specifications_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_instance_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IncludeAllInstances": get_scalar(md, "IncludeAllInstances"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_iam_instance_profile_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
        }

    @staticmethod
    def parse_get_console_output_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "Latest": get_scalar(md, "Latest"),
        }

    @staticmethod
    def parse_get_console_screenshot_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "WakeUp": get_scalar(md, "WakeUp"),
        }

    @staticmethod
    def parse_get_default_credit_specification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceFamily": get_scalar(md, "InstanceFamily"),
        }

    @staticmethod
    def parse_get_instance_metadata_defaults_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_get_instance_uefi_data_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_get_password_data_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_modify_default_credit_specification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CpuCredits": get_scalar(md, "CpuCredits"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceFamily": get_scalar(md, "InstanceFamily"),
        }

    @staticmethod
    def parse_modify_instance_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "BlockDeviceMapping.N": get_indexed_list(md, "BlockDeviceMapping"),
            "DisableApiStop": get_scalar(md, "DisableApiStop"),
            "DisableApiTermination": get_scalar(md, "DisableApiTermination"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EbsOptimized": get_scalar(md, "EbsOptimized"),
            "EnaSupport": get_scalar(md, "EnaSupport"),
            "GroupId.N": get_indexed_list(md, "GroupId"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "InstanceInitiatedShutdownBehavior": get_scalar(md, "InstanceInitiatedShutdownBehavior"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "Kernel": get_scalar(md, "Kernel"),
            "Ramdisk": get_scalar(md, "Ramdisk"),
            "SourceDestCheck": get_scalar(md, "SourceDestCheck"),
            "SriovNetSupport": get_scalar(md, "SriovNetSupport"),
            "UserData": get_scalar(md, "UserData"),
            "Value": get_scalar(md, "Value"),
        }

    @staticmethod
    def parse_modify_instance_cpu_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CoreCount": get_int(md, "CoreCount"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "ThreadsPerCore": get_int(md, "ThreadsPerCore"),
        }

    @staticmethod
    def parse_modify_instance_credit_specification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCreditSpecification.N": get_indexed_list(md, "InstanceCreditSpecification"),
        }

    @staticmethod
    def parse_modify_instance_event_start_time_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceEventId": get_scalar(md, "InstanceEventId"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "NotBefore": get_scalar(md, "NotBefore"),
        }

    @staticmethod
    def parse_modify_instance_maintenance_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AutoRecovery": get_scalar(md, "AutoRecovery"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "RebootMigration": get_scalar(md, "RebootMigration"),
        }

    @staticmethod
    def parse_modify_instance_metadata_defaults_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "HttpEndpoint": get_scalar(md, "HttpEndpoint"),
            "HttpPutResponseHopLimit": get_int(md, "HttpPutResponseHopLimit"),
            "HttpTokens": get_scalar(md, "HttpTokens"),
            "InstanceMetadataTags": get_scalar(md, "InstanceMetadataTags"),
        }

    @staticmethod
    def parse_modify_instance_metadata_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "HttpEndpoint": get_scalar(md, "HttpEndpoint"),
            "HttpProtocolIpv6": get_scalar(md, "HttpProtocolIpv6"),
            "HttpPutResponseHopLimit": get_int(md, "HttpPutResponseHopLimit"),
            "HttpTokens": get_scalar(md, "HttpTokens"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "InstanceMetadataTags": get_scalar(md, "InstanceMetadataTags"),
        }

    @staticmethod
    def parse_modify_instance_network_performance_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BandwidthWeighting": get_scalar(md, "BandwidthWeighting"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_modify_private_dns_name_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EnableResourceNameDnsAAAARecord": get_scalar(md, "EnableResourceNameDnsAAAARecord"),
            "EnableResourceNameDnsARecord": get_scalar(md, "EnableResourceNameDnsARecord"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "PrivateDnsHostnameType": get_scalar(md, "PrivateDnsHostnameType"),
        }

    @staticmethod
    def parse_modify_public_ip_dns_name_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "HostnameType": get_scalar(md, "HostnameType"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
        }

    @staticmethod
    def parse_monitor_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
        }

    @staticmethod
    def parse_reboot_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
        }

    @staticmethod
    def parse_replace_iam_instance_profile_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "IamInstanceProfile": get_scalar(md, "IamInstanceProfile"),
        }

    @staticmethod
    def parse_report_instance_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndTime": get_scalar(md, "EndTime"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "ReasonCode.N": get_indexed_list(md, "ReasonCode"),
            "StartTime": get_scalar(md, "StartTime"),
            "Status": get_scalar(md, "Status"),
        }

    @staticmethod
    def parse_reset_instance_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_run_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AdditionalInfo": get_scalar(md, "AdditionalInfo"),
            "BlockDeviceMapping.N": get_indexed_list(md, "BlockDeviceMapping"),
            "CapacityReservationSpecification": get_scalar(md, "CapacityReservationSpecification"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "CpuOptions": get_scalar(md, "CpuOptions"),
            "CreditSpecification": get_scalar(md, "CreditSpecification"),
            "DisableApiStop": get_scalar(md, "DisableApiStop"),
            "DisableApiTermination": get_scalar(md, "DisableApiTermination"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EbsOptimized": get_scalar(md, "EbsOptimized"),
            "ElasticGpuSpecification.N": get_indexed_list(md, "ElasticGpuSpecification"),
            "ElasticInferenceAccelerator.N": get_indexed_list(md, "ElasticInferenceAccelerator"),
            "EnablePrimaryIpv6": get_scalar(md, "EnablePrimaryIpv6"),
            "EnclaveOptions": get_scalar(md, "EnclaveOptions"),
            "HibernationOptions": get_scalar(md, "HibernationOptions"),
            "IamInstanceProfile": get_scalar(md, "IamInstanceProfile"),
            "ImageId": get_scalar(md, "ImageId"),
            "InstanceInitiatedShutdownBehavior": get_scalar(md, "InstanceInitiatedShutdownBehavior"),
            "InstanceMarketOptions": get_scalar(md, "InstanceMarketOptions"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "Ipv6Address.N": get_indexed_list(md, "Ipv6Address"),
            "Ipv6AddressCount": get_int(md, "Ipv6AddressCount"),
            "KernelId": get_scalar(md, "KernelId"),
            "KeyName": get_scalar(md, "KeyName"),
            "LaunchTemplate": get_scalar(md, "LaunchTemplate"),
            "LicenseSpecification.N": get_indexed_list(md, "LicenseSpecification"),
            "MaintenanceOptions": get_int(md, "MaintenanceOptions"),
            "MaxCount": get_int(md, "MaxCount"),
            "MetadataOptions": get_scalar(md, "MetadataOptions"),
            "MinCount": get_int(md, "MinCount"),
            "Monitoring": get_scalar(md, "Monitoring"),
            "NetworkInterface.N": get_indexed_list(md, "NetworkInterface"),
            "NetworkPerformanceOptions": get_scalar(md, "NetworkPerformanceOptions"),
            "Operator": get_scalar(md, "Operator"),
            "Placement": get_scalar(md, "Placement"),
            "PrivateDnsNameOptions": get_scalar(md, "PrivateDnsNameOptions"),
            "PrivateIpAddress": get_scalar(md, "PrivateIpAddress"),
            "RamdiskId": get_scalar(md, "RamdiskId"),
            "SecurityGroup.N": get_indexed_list(md, "SecurityGroup"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "UserData": get_scalar(md, "UserData"),
        }

    @staticmethod
    def parse_send_diagnostic_interrupt_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_start_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AdditionalInfo": get_scalar(md, "AdditionalInfo"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
        }

    @staticmethod
    def parse_stop_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Force": get_scalar(md, "Force"),
            "Hibernate": get_scalar(md, "Hibernate"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "SkipOsShutdown": get_scalar(md, "SkipOsShutdown"),
        }

    @staticmethod
    def parse_terminate_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Force": get_scalar(md, "Force"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "SkipOsShutdown": get_scalar(md, "SkipOsShutdown"),
        }

    @staticmethod
    def parse_unmonitor_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateIamInstanceProfile": instance_RequestParser.parse_associate_iam_instance_profile_request,
            "CreateDelegateMacVolumeOwnershipTask": instance_RequestParser.parse_create_delegate_mac_volume_ownership_task_request,
            "CreateMacSystemIntegrityProtectionModificationTask": instance_RequestParser.parse_create_mac_system_integrity_protection_modification_task_request,
            "DescribeIamInstanceProfileAssociations": instance_RequestParser.parse_describe_iam_instance_profile_associations_request,
            "DescribeInstanceAttribute": instance_RequestParser.parse_describe_instance_attribute_request,
            "DescribeInstanceCreditSpecifications": instance_RequestParser.parse_describe_instance_credit_specifications_request,
            "DescribeInstances": instance_RequestParser.parse_describe_instances_request,
            "DescribeInstanceStatus": instance_RequestParser.parse_describe_instance_status_request,
            "DisassociateIamInstanceProfile": instance_RequestParser.parse_disassociate_iam_instance_profile_request,
            "GetConsoleOutput": instance_RequestParser.parse_get_console_output_request,
            "GetConsoleScreenshot": instance_RequestParser.parse_get_console_screenshot_request,
            "GetDefaultCreditSpecification": instance_RequestParser.parse_get_default_credit_specification_request,
            "GetInstanceMetadataDefaults": instance_RequestParser.parse_get_instance_metadata_defaults_request,
            "GetInstanceUefiData": instance_RequestParser.parse_get_instance_uefi_data_request,
            "GetPasswordData": instance_RequestParser.parse_get_password_data_request,
            "ModifyDefaultCreditSpecification": instance_RequestParser.parse_modify_default_credit_specification_request,
            "ModifyInstanceAttribute": instance_RequestParser.parse_modify_instance_attribute_request,
            "ModifyInstanceCpuOptions": instance_RequestParser.parse_modify_instance_cpu_options_request,
            "ModifyInstanceCreditSpecification": instance_RequestParser.parse_modify_instance_credit_specification_request,
            "ModifyInstanceEventStartTime": instance_RequestParser.parse_modify_instance_event_start_time_request,
            "ModifyInstanceMaintenanceOptions": instance_RequestParser.parse_modify_instance_maintenance_options_request,
            "ModifyInstanceMetadataDefaults": instance_RequestParser.parse_modify_instance_metadata_defaults_request,
            "ModifyInstanceMetadataOptions": instance_RequestParser.parse_modify_instance_metadata_options_request,
            "ModifyInstanceNetworkPerformanceOptions": instance_RequestParser.parse_modify_instance_network_performance_options_request,
            "ModifyPrivateDnsNameOptions": instance_RequestParser.parse_modify_private_dns_name_options_request,
            "ModifyPublicIpDnsNameOptions": instance_RequestParser.parse_modify_public_ip_dns_name_options_request,
            "MonitorInstances": instance_RequestParser.parse_monitor_instances_request,
            "RebootInstances": instance_RequestParser.parse_reboot_instances_request,
            "ReplaceIamInstanceProfileAssociation": instance_RequestParser.parse_replace_iam_instance_profile_association_request,
            "ReportInstanceStatus": instance_RequestParser.parse_report_instance_status_request,
            "ResetInstanceAttribute": instance_RequestParser.parse_reset_instance_attribute_request,
            "RunInstances": instance_RequestParser.parse_run_instances_request,
            "SendDiagnosticInterrupt": instance_RequestParser.parse_send_diagnostic_interrupt_request,
            "StartInstances": instance_RequestParser.parse_start_instances_request,
            "StopInstances": instance_RequestParser.parse_stop_instances_request,
            "TerminateInstances": instance_RequestParser.parse_terminate_instances_request,
            "UnmonitorInstances": instance_RequestParser.parse_unmonitor_instances_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class instance_ResponseSerializer:
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
                xml_parts.extend(instance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(instance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(instance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(instance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_iam_instance_profile_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateIamInstanceProfileResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize iamInstanceProfileAssociation
        _iamInstanceProfileAssociation_key = None
        if "iamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "iamInstanceProfileAssociation"
        elif "IamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "IamInstanceProfileAssociation"
        if _iamInstanceProfileAssociation_key:
            param_data = data[_iamInstanceProfileAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<iamInstanceProfileAssociation>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</iamInstanceProfileAssociation>')
        xml_parts.append(f'</AssociateIamInstanceProfileResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_delegate_mac_volume_ownership_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateDelegateMacVolumeOwnershipTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize macModificationTask
        _macModificationTask_key = None
        if "macModificationTask" in data:
            _macModificationTask_key = "macModificationTask"
        elif "MacModificationTask" in data:
            _macModificationTask_key = "MacModificationTask"
        if _macModificationTask_key:
            param_data = data[_macModificationTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<macModificationTask>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</macModificationTask>')
        xml_parts.append(f'</CreateDelegateMacVolumeOwnershipTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_mac_system_integrity_protection_modification_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateMacSystemIntegrityProtectionModificationTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize macModificationTask
        _macModificationTask_key = None
        if "macModificationTask" in data:
            _macModificationTask_key = "macModificationTask"
        elif "MacModificationTask" in data:
            _macModificationTask_key = "MacModificationTask"
        if _macModificationTask_key:
            param_data = data[_macModificationTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<macModificationTask>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</macModificationTask>')
        xml_parts.append(f'</CreateMacSystemIntegrityProtectionModificationTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_iam_instance_profile_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIamInstanceProfileAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize iamInstanceProfileAssociationSet
        _iamInstanceProfileAssociationSet_key = None
        if "iamInstanceProfileAssociationSet" in data:
            _iamInstanceProfileAssociationSet_key = "iamInstanceProfileAssociationSet"
        elif "IamInstanceProfileAssociationSet" in data:
            _iamInstanceProfileAssociationSet_key = "IamInstanceProfileAssociationSet"
        elif "IamInstanceProfileAssociations" in data:
            _iamInstanceProfileAssociationSet_key = "IamInstanceProfileAssociations"
        if _iamInstanceProfileAssociationSet_key:
            param_data = data[_iamInstanceProfileAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<iamInstanceProfileAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</iamInstanceProfileAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<iamInstanceProfileAssociationSet/>')
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
        xml_parts.append(f'</DescribeIamInstanceProfileAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize blockDeviceMapping
        _blockDeviceMapping_key = None
        if "blockDeviceMapping" in data:
            _blockDeviceMapping_key = "blockDeviceMapping"
        elif "BlockDeviceMapping" in data:
            _blockDeviceMapping_key = "BlockDeviceMapping"
        if _blockDeviceMapping_key:
            param_data = data[_blockDeviceMapping_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<blockDeviceMappingSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</blockDeviceMappingSet>')
            else:
                xml_parts.append(f'{indent_str}<blockDeviceMappingSet/>')
        # Serialize disableApiStop
        _disableApiStop_key = None
        if "disableApiStop" in data:
            _disableApiStop_key = "disableApiStop"
        elif "DisableApiStop" in data:
            _disableApiStop_key = "DisableApiStop"
        if _disableApiStop_key:
            param_data = data[_disableApiStop_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<disableApiStop>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</disableApiStop>')
        # Serialize disableApiTermination
        _disableApiTermination_key = None
        if "disableApiTermination" in data:
            _disableApiTermination_key = "disableApiTermination"
        elif "DisableApiTermination" in data:
            _disableApiTermination_key = "DisableApiTermination"
        if _disableApiTermination_key:
            param_data = data[_disableApiTermination_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<disableApiTermination>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</disableApiTermination>')
        # Serialize ebsOptimized
        _ebsOptimized_key = None
        if "ebsOptimized" in data:
            _ebsOptimized_key = "ebsOptimized"
        elif "EbsOptimized" in data:
            _ebsOptimized_key = "EbsOptimized"
        if _ebsOptimized_key:
            param_data = data[_ebsOptimized_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ebsOptimized>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ebsOptimized>')
        # Serialize enaSupport
        _enaSupport_key = None
        if "enaSupport" in data:
            _enaSupport_key = "enaSupport"
        elif "EnaSupport" in data:
            _enaSupport_key = "EnaSupport"
        if _enaSupport_key:
            param_data = data[_enaSupport_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<enaSupport>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</enaSupport>')
        # Serialize enclaveOptions
        _enclaveOptions_key = None
        if "enclaveOptions" in data:
            _enclaveOptions_key = "enclaveOptions"
        elif "EnclaveOptions" in data:
            _enclaveOptions_key = "EnclaveOptions"
        if _enclaveOptions_key:
            param_data = data[_enclaveOptions_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<enclaveOptionsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</enclaveOptionsSet>')
            else:
                xml_parts.append(f'{indent_str}<enclaveOptionsSet/>')
        # Serialize groupSet
        _groupSet_key = None
        if "groupSet" in data:
            _groupSet_key = "groupSet"
        elif "GroupSet" in data:
            _groupSet_key = "GroupSet"
        elif "Groups" in data:
            _groupSet_key = "Groups"
        if _groupSet_key:
            param_data = data[_groupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<groupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</groupSet>')
            else:
                xml_parts.append(f'{indent_str}<groupSet/>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize instanceInitiatedShutdownBehavior
        _instanceInitiatedShutdownBehavior_key = None
        if "instanceInitiatedShutdownBehavior" in data:
            _instanceInitiatedShutdownBehavior_key = "instanceInitiatedShutdownBehavior"
        elif "InstanceInitiatedShutdownBehavior" in data:
            _instanceInitiatedShutdownBehavior_key = "InstanceInitiatedShutdownBehavior"
        if _instanceInitiatedShutdownBehavior_key:
            param_data = data[_instanceInitiatedShutdownBehavior_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceInitiatedShutdownBehavior>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceInitiatedShutdownBehavior>')
        # Serialize instanceType
        _instanceType_key = None
        if "instanceType" in data:
            _instanceType_key = "instanceType"
        elif "InstanceType" in data:
            _instanceType_key = "InstanceType"
        if _instanceType_key:
            param_data = data[_instanceType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceType>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceType>')
        # Serialize kernel
        _kernel_key = None
        if "kernel" in data:
            _kernel_key = "kernel"
        elif "Kernel" in data:
            _kernel_key = "Kernel"
        if _kernel_key:
            param_data = data[_kernel_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<kernel>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</kernel>')
        # Serialize productCodes
        _productCodes_key = None
        if "productCodes" in data:
            _productCodes_key = "productCodes"
        elif "ProductCodes" in data:
            _productCodes_key = "ProductCodes"
        if _productCodes_key:
            param_data = data[_productCodes_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<productCodesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</productCodesSet>')
            else:
                xml_parts.append(f'{indent_str}<productCodesSet/>')
        # Serialize ramdisk
        _ramdisk_key = None
        if "ramdisk" in data:
            _ramdisk_key = "ramdisk"
        elif "Ramdisk" in data:
            _ramdisk_key = "Ramdisk"
        if _ramdisk_key:
            param_data = data[_ramdisk_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ramdisk>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ramdisk>')
        # Serialize rootDeviceName
        _rootDeviceName_key = None
        if "rootDeviceName" in data:
            _rootDeviceName_key = "rootDeviceName"
        elif "RootDeviceName" in data:
            _rootDeviceName_key = "RootDeviceName"
        if _rootDeviceName_key:
            param_data = data[_rootDeviceName_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<rootDeviceName>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</rootDeviceName>')
        # Serialize sourceDestCheck
        _sourceDestCheck_key = None
        if "sourceDestCheck" in data:
            _sourceDestCheck_key = "sourceDestCheck"
        elif "SourceDestCheck" in data:
            _sourceDestCheck_key = "SourceDestCheck"
        if _sourceDestCheck_key:
            param_data = data[_sourceDestCheck_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sourceDestCheck>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sourceDestCheck>')
        # Serialize sriovNetSupport
        _sriovNetSupport_key = None
        if "sriovNetSupport" in data:
            _sriovNetSupport_key = "sriovNetSupport"
        elif "SriovNetSupport" in data:
            _sriovNetSupport_key = "SriovNetSupport"
        if _sriovNetSupport_key:
            param_data = data[_sriovNetSupport_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sriovNetSupport>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sriovNetSupport>')
        # Serialize userData
        _userData_key = None
        if "userData" in data:
            _userData_key = "userData"
        elif "UserData" in data:
            _userData_key = "UserData"
        if _userData_key:
            param_data = data[_userData_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<userData>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</userData>')
        xml_parts.append(f'</DescribeInstanceAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_credit_specifications_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceCreditSpecificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceCreditSpecificationSet
        _instanceCreditSpecificationSet_key = None
        if "instanceCreditSpecificationSet" in data:
            _instanceCreditSpecificationSet_key = "instanceCreditSpecificationSet"
        elif "InstanceCreditSpecificationSet" in data:
            _instanceCreditSpecificationSet_key = "InstanceCreditSpecificationSet"
        elif "InstanceCreditSpecifications" in data:
            _instanceCreditSpecificationSet_key = "InstanceCreditSpecifications"
        if _instanceCreditSpecificationSet_key:
            param_data = data[_instanceCreditSpecificationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceCreditSpecificationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceCreditSpecificationSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceCreditSpecificationSet/>')
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
        xml_parts.append(f'</DescribeInstanceCreditSpecificationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize reservationSet
        _reservationSet_key = None
        if "reservationSet" in data:
            _reservationSet_key = "reservationSet"
        elif "ReservationSet" in data:
            _reservationSet_key = "ReservationSet"
        elif "Reservations" in data:
            _reservationSet_key = "Reservations"
        if _reservationSet_key:
            param_data = data[_reservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservationSet>')
            else:
                xml_parts.append(f'{indent_str}<reservationSet/>')
        xml_parts.append(f'</DescribeInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceStatusSet
        _instanceStatusSet_key = None
        if "instanceStatusSet" in data:
            _instanceStatusSet_key = "instanceStatusSet"
        elif "InstanceStatusSet" in data:
            _instanceStatusSet_key = "InstanceStatusSet"
        elif "InstanceStatuss" in data:
            _instanceStatusSet_key = "InstanceStatuss"
        if _instanceStatusSet_key:
            param_data = data[_instanceStatusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceStatusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceStatusSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceStatusSet/>')
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
        xml_parts.append(f'</DescribeInstanceStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_iam_instance_profile_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateIamInstanceProfileResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize iamInstanceProfileAssociation
        _iamInstanceProfileAssociation_key = None
        if "iamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "iamInstanceProfileAssociation"
        elif "IamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "IamInstanceProfileAssociation"
        if _iamInstanceProfileAssociation_key:
            param_data = data[_iamInstanceProfileAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<iamInstanceProfileAssociation>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</iamInstanceProfileAssociation>')
        xml_parts.append(f'</DisassociateIamInstanceProfileResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_console_output_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetConsoleOutputResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize output
        _output_key = None
        if "output" in data:
            _output_key = "output"
        elif "Output" in data:
            _output_key = "Output"
        if _output_key:
            param_data = data[_output_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<output>{esc(str(param_data))}</output>')
        # Serialize timestamp
        _timestamp_key = None
        if "timestamp" in data:
            _timestamp_key = "timestamp"
        elif "Timestamp" in data:
            _timestamp_key = "Timestamp"
        if _timestamp_key:
            param_data = data[_timestamp_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<timestamp>{esc(str(param_data))}</timestamp>')
        xml_parts.append(f'</GetConsoleOutputResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_console_screenshot_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetConsoleScreenshotResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize imageData
        _imageData_key = None
        if "imageData" in data:
            _imageData_key = "imageData"
        elif "ImageData" in data:
            _imageData_key = "ImageData"
        if _imageData_key:
            param_data = data[_imageData_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<imageData>{esc(str(param_data))}</imageData>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        xml_parts.append(f'</GetConsoleScreenshotResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_default_credit_specification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetDefaultCreditSpecificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceFamilyCreditSpecification
        _instanceFamilyCreditSpecification_key = None
        if "instanceFamilyCreditSpecification" in data:
            _instanceFamilyCreditSpecification_key = "instanceFamilyCreditSpecification"
        elif "InstanceFamilyCreditSpecification" in data:
            _instanceFamilyCreditSpecification_key = "InstanceFamilyCreditSpecification"
        if _instanceFamilyCreditSpecification_key:
            param_data = data[_instanceFamilyCreditSpecification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceFamilyCreditSpecification>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceFamilyCreditSpecification>')
        xml_parts.append(f'</GetDefaultCreditSpecificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_instance_metadata_defaults_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize accountLevel
        _accountLevel_key = None
        if "accountLevel" in data:
            _accountLevel_key = "accountLevel"
        elif "AccountLevel" in data:
            _accountLevel_key = "AccountLevel"
        if _accountLevel_key:
            param_data = data[_accountLevel_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<accountLevel>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</accountLevel>')
        xml_parts.append(f'</GetInstanceMetadataDefaultsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_instance_uefi_data_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetInstanceUefiDataResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize uefiData
        _uefiData_key = None
        if "uefiData" in data:
            _uefiData_key = "uefiData"
        elif "UefiData" in data:
            _uefiData_key = "UefiData"
        if _uefiData_key:
            param_data = data[_uefiData_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<uefiData>{esc(str(param_data))}</uefiData>')
        xml_parts.append(f'</GetInstanceUefiDataResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_password_data_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetPasswordDataResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize passwordData
        _passwordData_key = None
        if "passwordData" in data:
            _passwordData_key = "passwordData"
        elif "PasswordData" in data:
            _passwordData_key = "PasswordData"
        if _passwordData_key:
            param_data = data[_passwordData_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<passwordData>{esc(str(param_data))}</passwordData>')
        # Serialize timestamp
        _timestamp_key = None
        if "timestamp" in data:
            _timestamp_key = "timestamp"
        elif "Timestamp" in data:
            _timestamp_key = "Timestamp"
        if _timestamp_key:
            param_data = data[_timestamp_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<timestamp>{esc(str(param_data))}</timestamp>')
        xml_parts.append(f'</GetPasswordDataResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_default_credit_specification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyDefaultCreditSpecificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceFamilyCreditSpecification
        _instanceFamilyCreditSpecification_key = None
        if "instanceFamilyCreditSpecification" in data:
            _instanceFamilyCreditSpecification_key = "instanceFamilyCreditSpecification"
        elif "InstanceFamilyCreditSpecification" in data:
            _instanceFamilyCreditSpecification_key = "InstanceFamilyCreditSpecification"
        if _instanceFamilyCreditSpecification_key:
            param_data = data[_instanceFamilyCreditSpecification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceFamilyCreditSpecification>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceFamilyCreditSpecification>')
        xml_parts.append(f'</ModifyDefaultCreditSpecificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyInstanceAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_cpu_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceCpuOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coreCount
        _coreCount_key = None
        if "coreCount" in data:
            _coreCount_key = "coreCount"
        elif "CoreCount" in data:
            _coreCount_key = "CoreCount"
        if _coreCount_key:
            param_data = data[_coreCount_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coreCount>{esc(str(param_data))}</coreCount>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize threadsPerCore
        _threadsPerCore_key = None
        if "threadsPerCore" in data:
            _threadsPerCore_key = "threadsPerCore"
        elif "ThreadsPerCore" in data:
            _threadsPerCore_key = "ThreadsPerCore"
        if _threadsPerCore_key:
            param_data = data[_threadsPerCore_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<threadsPerCore>{esc(str(param_data))}</threadsPerCore>')
        xml_parts.append(f'</ModifyInstanceCpuOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_credit_specification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceCreditSpecificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successfulInstanceCreditSpecificationSet
        _successfulInstanceCreditSpecificationSet_key = None
        if "successfulInstanceCreditSpecificationSet" in data:
            _successfulInstanceCreditSpecificationSet_key = "successfulInstanceCreditSpecificationSet"
        elif "SuccessfulInstanceCreditSpecificationSet" in data:
            _successfulInstanceCreditSpecificationSet_key = "SuccessfulInstanceCreditSpecificationSet"
        elif "SuccessfulInstanceCreditSpecifications" in data:
            _successfulInstanceCreditSpecificationSet_key = "SuccessfulInstanceCreditSpecifications"
        if _successfulInstanceCreditSpecificationSet_key:
            param_data = data[_successfulInstanceCreditSpecificationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulInstanceCreditSpecificationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulInstanceCreditSpecificationSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulInstanceCreditSpecificationSet/>')
        # Serialize unsuccessfulInstanceCreditSpecificationSet
        _unsuccessfulInstanceCreditSpecificationSet_key = None
        if "unsuccessfulInstanceCreditSpecificationSet" in data:
            _unsuccessfulInstanceCreditSpecificationSet_key = "unsuccessfulInstanceCreditSpecificationSet"
        elif "UnsuccessfulInstanceCreditSpecificationSet" in data:
            _unsuccessfulInstanceCreditSpecificationSet_key = "UnsuccessfulInstanceCreditSpecificationSet"
        elif "UnsuccessfulInstanceCreditSpecifications" in data:
            _unsuccessfulInstanceCreditSpecificationSet_key = "UnsuccessfulInstanceCreditSpecifications"
        if _unsuccessfulInstanceCreditSpecificationSet_key:
            param_data = data[_unsuccessfulInstanceCreditSpecificationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulInstanceCreditSpecificationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulInstanceCreditSpecificationSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulInstanceCreditSpecificationSet/>')
        xml_parts.append(f'</ModifyInstanceCreditSpecificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_event_start_time_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceEventStartTimeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize event
        _event_key = None
        if "event" in data:
            _event_key = "event"
        elif "Event" in data:
            _event_key = "Event"
        if _event_key:
            param_data = data[_event_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<event>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</event>')
        xml_parts.append(f'</ModifyInstanceEventStartTimeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_maintenance_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceMaintenanceOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize autoRecovery
        _autoRecovery_key = None
        if "autoRecovery" in data:
            _autoRecovery_key = "autoRecovery"
        elif "AutoRecovery" in data:
            _autoRecovery_key = "AutoRecovery"
        if _autoRecovery_key:
            param_data = data[_autoRecovery_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<autoRecovery>{esc(str(param_data))}</autoRecovery>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize rebootMigration
        _rebootMigration_key = None
        if "rebootMigration" in data:
            _rebootMigration_key = "rebootMigration"
        elif "RebootMigration" in data:
            _rebootMigration_key = "RebootMigration"
        if _rebootMigration_key:
            param_data = data[_rebootMigration_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<rebootMigration>{esc(str(param_data))}</rebootMigration>')
        xml_parts.append(f'</ModifyInstanceMaintenanceOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_metadata_defaults_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceMetadataDefaultsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyInstanceMetadataDefaultsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_metadata_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceMetadataOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize instanceMetadataOptions
        _instanceMetadataOptions_key = None
        if "instanceMetadataOptions" in data:
            _instanceMetadataOptions_key = "instanceMetadataOptions"
        elif "InstanceMetadataOptions" in data:
            _instanceMetadataOptions_key = "InstanceMetadataOptions"
        if _instanceMetadataOptions_key:
            param_data = data[_instanceMetadataOptions_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceMetadataOptionsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceMetadataOptionsSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceMetadataOptionsSet/>')
        xml_parts.append(f'</ModifyInstanceMetadataOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_network_performance_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceNetworkPerformanceOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize bandwidthWeighting
        _bandwidthWeighting_key = None
        if "bandwidthWeighting" in data:
            _bandwidthWeighting_key = "bandwidthWeighting"
        elif "BandwidthWeighting" in data:
            _bandwidthWeighting_key = "BandwidthWeighting"
        if _bandwidthWeighting_key:
            param_data = data[_bandwidthWeighting_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<bandwidthWeighting>{esc(str(param_data))}</bandwidthWeighting>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        xml_parts.append(f'</ModifyInstanceNetworkPerformanceOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_private_dns_name_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyPrivateDnsNameOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyPrivateDnsNameOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_public_ip_dns_name_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyPublicIpDnsNameOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successful
        _successful_key = None
        if "successful" in data:
            _successful_key = "successful"
        elif "Successful" in data:
            _successful_key = "Successful"
        if _successful_key:
            param_data = data[_successful_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<successful>{esc(str(param_data))}</successful>')
        xml_parts.append(f'</ModifyPublicIpDnsNameOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_monitor_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<MonitorInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        xml_parts.append(f'</MonitorInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reboot_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RebootInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</RebootInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_iam_instance_profile_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceIamInstanceProfileAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize iamInstanceProfileAssociation
        _iamInstanceProfileAssociation_key = None
        if "iamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "iamInstanceProfileAssociation"
        elif "IamInstanceProfileAssociation" in data:
            _iamInstanceProfileAssociation_key = "IamInstanceProfileAssociation"
        if _iamInstanceProfileAssociation_key:
            param_data = data[_iamInstanceProfileAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<iamInstanceProfileAssociation>')
            xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</iamInstanceProfileAssociation>')
        xml_parts.append(f'</ReplaceIamInstanceProfileAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_report_instance_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReportInstanceStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ReportInstanceStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reset_instance_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ResetInstanceAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ResetInstanceAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_run_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RunInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize groupSet
        _groupSet_key = None
        if "groupSet" in data:
            _groupSet_key = "groupSet"
        elif "GroupSet" in data:
            _groupSet_key = "GroupSet"
        elif "Groups" in data:
            _groupSet_key = "Groups"
        if _groupSet_key:
            param_data = data[_groupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<groupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</groupSet>')
            else:
                xml_parts.append(f'{indent_str}<groupSet/>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        # Serialize ownerId
        _ownerId_key = None
        if "ownerId" in data:
            _ownerId_key = "ownerId"
        elif "OwnerId" in data:
            _ownerId_key = "OwnerId"
        if _ownerId_key:
            param_data = data[_ownerId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ownerId>{esc(str(param_data))}</ownerId>')
        # Serialize requesterId
        _requesterId_key = None
        if "requesterId" in data:
            _requesterId_key = "requesterId"
        elif "RequesterId" in data:
            _requesterId_key = "RequesterId"
        if _requesterId_key:
            param_data = data[_requesterId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<requesterId>{esc(str(param_data))}</requesterId>')
        # Serialize reservationId
        _reservationId_key = None
        if "reservationId" in data:
            _reservationId_key = "reservationId"
        elif "ReservationId" in data:
            _reservationId_key = "ReservationId"
        if _reservationId_key:
            param_data = data[_reservationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reservationId>{esc(str(param_data))}</reservationId>')
        xml_parts.append(f'</RunInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_send_diagnostic_interrupt_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<SendDiagnosticInterruptResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</SendDiagnosticInterruptResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_start_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StartInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        xml_parts.append(f'</StartInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_stop_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StopInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        xml_parts.append(f'</StopInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_terminate_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<TerminateInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        xml_parts.append(f'</TerminateInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_unmonitor_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<UnmonitorInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instancesSet
        _instancesSet_key = None
        if "instancesSet" in data:
            _instancesSet_key = "instancesSet"
        elif "InstancesSet" in data:
            _instancesSet_key = "InstancesSet"
        elif "Instancess" in data:
            _instancesSet_key = "Instancess"
        if _instancesSet_key:
            param_data = data[_instancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instancesSet>')
            else:
                xml_parts.append(f'{indent_str}<instancesSet/>')
        xml_parts.append(f'</UnmonitorInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateIamInstanceProfile": instance_ResponseSerializer.serialize_associate_iam_instance_profile_response,
            "CreateDelegateMacVolumeOwnershipTask": instance_ResponseSerializer.serialize_create_delegate_mac_volume_ownership_task_response,
            "CreateMacSystemIntegrityProtectionModificationTask": instance_ResponseSerializer.serialize_create_mac_system_integrity_protection_modification_task_response,
            "DescribeIamInstanceProfileAssociations": instance_ResponseSerializer.serialize_describe_iam_instance_profile_associations_response,
            "DescribeInstanceAttribute": instance_ResponseSerializer.serialize_describe_instance_attribute_response,
            "DescribeInstanceCreditSpecifications": instance_ResponseSerializer.serialize_describe_instance_credit_specifications_response,
            "DescribeInstances": instance_ResponseSerializer.serialize_describe_instances_response,
            "DescribeInstanceStatus": instance_ResponseSerializer.serialize_describe_instance_status_response,
            "DisassociateIamInstanceProfile": instance_ResponseSerializer.serialize_disassociate_iam_instance_profile_response,
            "GetConsoleOutput": instance_ResponseSerializer.serialize_get_console_output_response,
            "GetConsoleScreenshot": instance_ResponseSerializer.serialize_get_console_screenshot_response,
            "GetDefaultCreditSpecification": instance_ResponseSerializer.serialize_get_default_credit_specification_response,
            "GetInstanceMetadataDefaults": instance_ResponseSerializer.serialize_get_instance_metadata_defaults_response,
            "GetInstanceUefiData": instance_ResponseSerializer.serialize_get_instance_uefi_data_response,
            "GetPasswordData": instance_ResponseSerializer.serialize_get_password_data_response,
            "ModifyDefaultCreditSpecification": instance_ResponseSerializer.serialize_modify_default_credit_specification_response,
            "ModifyInstanceAttribute": instance_ResponseSerializer.serialize_modify_instance_attribute_response,
            "ModifyInstanceCpuOptions": instance_ResponseSerializer.serialize_modify_instance_cpu_options_response,
            "ModifyInstanceCreditSpecification": instance_ResponseSerializer.serialize_modify_instance_credit_specification_response,
            "ModifyInstanceEventStartTime": instance_ResponseSerializer.serialize_modify_instance_event_start_time_response,
            "ModifyInstanceMaintenanceOptions": instance_ResponseSerializer.serialize_modify_instance_maintenance_options_response,
            "ModifyInstanceMetadataDefaults": instance_ResponseSerializer.serialize_modify_instance_metadata_defaults_response,
            "ModifyInstanceMetadataOptions": instance_ResponseSerializer.serialize_modify_instance_metadata_options_response,
            "ModifyInstanceNetworkPerformanceOptions": instance_ResponseSerializer.serialize_modify_instance_network_performance_options_response,
            "ModifyPrivateDnsNameOptions": instance_ResponseSerializer.serialize_modify_private_dns_name_options_response,
            "ModifyPublicIpDnsNameOptions": instance_ResponseSerializer.serialize_modify_public_ip_dns_name_options_response,
            "MonitorInstances": instance_ResponseSerializer.serialize_monitor_instances_response,
            "RebootInstances": instance_ResponseSerializer.serialize_reboot_instances_response,
            "ReplaceIamInstanceProfileAssociation": instance_ResponseSerializer.serialize_replace_iam_instance_profile_association_response,
            "ReportInstanceStatus": instance_ResponseSerializer.serialize_report_instance_status_response,
            "ResetInstanceAttribute": instance_ResponseSerializer.serialize_reset_instance_attribute_response,
            "RunInstances": instance_ResponseSerializer.serialize_run_instances_response,
            "SendDiagnosticInterrupt": instance_ResponseSerializer.serialize_send_diagnostic_interrupt_response,
            "StartInstances": instance_ResponseSerializer.serialize_start_instances_response,
            "StopInstances": instance_ResponseSerializer.serialize_stop_instances_response,
            "TerminateInstances": instance_ResponseSerializer.serialize_terminate_instances_response,
            "UnmonitorInstances": instance_ResponseSerializer.serialize_unmonitor_instances_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

