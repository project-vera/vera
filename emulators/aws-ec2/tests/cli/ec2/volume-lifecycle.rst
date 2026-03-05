**Example 1: To create a gp3 EBS volume with tags**

The following ``create-volume`` example creates a 100 GiB gp3 volume in the specified Availability Zone and applies a Name tag for identification. ::

    aws ec2 create-volume \
        --volume-type gp3 \
        --size 100 \
        --availability-zone us-east-1a \
        --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=my-data-volume}]'

Output::

    {
        "AvailabilityZone": "us-east-1a",
        "Tags": [
            {
                "Key": "Name",
                "Value": "my-data-volume"
            }
        ],
        "Encrypted": false,
        "VolumeType": "gp3",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "creating",
        "Iops": 3000,
        "SnapshotId": "",
        "CreateTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "Size": 100
    }

**Example 2: To describe the volume and confirm it is available**

The following ``describe-volumes`` example retrieves details about the newly created volume to confirm its state is ``available`` before attaching it to an instance. ::

    aws ec2 describe-volumes \
        --volume-ids vol-1234567890abcdef0

Output::

    {
        "Volumes": [
            {
                "AvailabilityZone": "us-east-1a",
                "Attachments": [],
                "Encrypted": false,
                "VolumeType": "gp3",
                "VolumeId": "vol-1234567890abcdef0",
                "State": "available",
                "Iops": 3000,
                "SnapshotId": "",
                "CreateTime": "YYYY-MM-DDTHH:MM:SS.000Z",
                "Size": 100,
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "my-data-volume"
                    }
                ]
            }
        ]
    }

**Example 3: To attach the volume to an EC2 instance**

The following ``attach-volume`` example attaches the volume to the specified instance as device ``/dev/sdf``. ::

    aws ec2 attach-volume \
        --volume-id vol-1234567890abcdef0 \
        --instance-id i-01474ef662b89480 \
        --device /dev/sdf

Output::

    {
        "AttachTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "InstanceId": "i-01474ef662b89480",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "attaching",
        "Device": "/dev/sdf"
    }

**Example 4: To check the volume status**

The following ``describe-volume-status`` example checks the health status of the attached volume to confirm it is functioning correctly. ::

    aws ec2 describe-volume-status \
        --volume-ids vol-1234567890abcdef0

Output::

    {
        "VolumeStatuses": [
            {
                "VolumeStatus": {
                    "Status": "ok",
                    "Details": [
                        {
                            "Status": "passed",
                            "Name": "io-enabled"
                        },
                        {
                            "Status": "not-applicable",
                            "Name": "io-performance"
                        }
                    ]
                },
                "AvailabilityZone": "us-east-1a",
                "VolumeId": "vol-1234567890abcdef0",
                "Actions": [],
                "Events": []
            }
        ]
    }

**Example 5: To modify the volume size and type**

The following ``modify-volume`` example increases the volume size to 200 GiB and changes its type to ``io1`` with 4000 provisioned IOPS. ::

    aws ec2 modify-volume \
        --volume-id vol-1234567890abcdef0 \
        --volume-type io1 \
        --iops 4000 \
        --size 200

Output::

    {
        "VolumeModification": {
            "TargetSize": 200,
            "TargetVolumeType": "io1",
            "ModificationState": "modifying",
            "VolumeId": "vol-1234567890abcdef0",
            "TargetIops": 4000,
            "StartTime": "YYYY-MM-DDTHH:MM:SS.000Z",
            "Progress": 0,
            "OriginalVolumeType": "gp3",
            "OriginalIops": 3000,
            "OriginalSize": 100
        }
    }

**Example 6: To detach the volume from the instance**

The following ``detach-volume`` example detaches the volume from the instance in preparation for deletion. ::

    aws ec2 detach-volume \
        --volume-id vol-1234567890abcdef0

Output::

    {
        "AttachTime": "YYYY-MM-DDTHH:MM:SS.000Z",
        "InstanceId": "i-01474ef662b89480",
        "VolumeId": "vol-1234567890abcdef0",
        "State": "detaching",
        "Device": "/dev/sdf"
    }

**Example 7: To delete the volume**

The following ``delete-volume`` example deletes the detached volume. If the command succeeds, no output is returned. ::

    aws ec2 delete-volume \
        --volume-id vol-1234567890abcdef0
