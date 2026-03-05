**Example 1: To import a VM image file as an AMI**

The following ``import-image`` example imports a virtual machine OVA file from Amazon S3 to create an AMI. ::

    aws ec2 import-image \
        --disk-containers 'Format=ova,UserBucket={S3Bucket=my-import-bucket,S3Key=vms/my-server-vm.ova}' \
        --description "My imported server VM"

Output::

    {
        "ImportTaskId": "import-ami-1234567890abcdef0",
        "Progress": "2",
        "SnapshotDetails": [
            {
                "DiskImageSize": 0.0,
                "Format": "ova",
                "UserBucket": {
                    "S3Bucket": "my-import-bucket",
                    "S3Key": "vms/my-server-vm.ova"
                }
            }
        ],
        "Status": "active",
        "StatusMessage": "pending"
    }

**Example 2: To monitor the import image task progress**

The following ``describe-import-image-tasks`` example checks the status of the import task created in Example 1 while it is in progress. ::

    aws ec2 describe-import-image-tasks \
        --import-task-ids import-ami-1234567890abcdef0

Output for an import task that is in progress::

    {
        "ImportImageTasks": [
            {
                "ImportTaskId": "import-ami-1234567890abcdef0",
                "Progress": "28",
                "SnapshotDetails": [
                    {
                        "DiskImageSize": 705638400.0,
                        "Format": "ova",
                        "Status": "completed",
                        "UserBucket": {
                            "S3Bucket": "my-import-bucket",
                            "S3Key": "vms/my-server-vm.ova"
                        }
                    }
                ],
                "Status": "active",
                "StatusMessage": "converting"
            }
        ]
    }

**Example 3: To confirm the import task is complete and retrieve the AMI ID**

The following ``describe-import-image-tasks`` example checks the import task again after it has finished, returning the resulting AMI ID in the ``ImageId`` field. ::

    aws ec2 describe-import-image-tasks \
        --import-task-ids import-ami-1234567890abcdef0

Output for a completed import task::

    {
        "ImportImageTasks": [
            {
                "ImportTaskId": "import-ami-1234567890abcdef0",
                "ImageId": "ami-1234567890abcdef0",
                "SnapshotDetails": [
                    {
                        "DiskImageSize": 705638400.0,
                        "Format": "ova",
                        "SnapshotId": "snap-1234567890abcdef0",
                        "Status": "completed",
                        "UserBucket": {
                            "S3Bucket": "my-import-bucket",
                            "S3Key": "vms/my-server-vm.ova"
                        }
                    }
                ],
                "Status": "completed"
            }
        ]
    }

**Example 4: To export the imported AMI back to Amazon S3 as a VMDK**

The following ``export-image`` example exports the AMI from Example 3 to an S3 bucket in VMDK format. ::

    aws ec2 export-image \
        --image-id ami-1234567890abcdef0 \
        --disk-image-format VMDK \
        --s3-export-location S3Bucket=my-export-bucket,S3Prefix=exports/

Output::

    {
        "DiskImageFormat": "vmdk",
        "ExportImageTaskId": "export-ami-1234567890abcdef0",
        "ImageId": "ami-1234567890abcdef0",
        "RoleName": "vmimport",
        "Progress": "0",
        "S3ExportLocation": {
            "S3Bucket": "my-export-bucket",
            "S3Prefix": "exports/"
        },
        "Status": "active",
        "StatusMessage": "validating"
    }

**Example 5: To monitor the export image task progress**

The following ``describe-export-image-tasks`` example checks the status of the export task created in Example 4 while it is still running. ::

    aws ec2 describe-export-image-tasks \
        --export-image-task-ids export-ami-1234567890abcdef0

Output for an export task that is in progress::

    {
        "ExportImageTasks": [
            {
                "ExportImageTaskId": "export-ami-1234567890abcdef0",
                "Progress": "21",
                "S3ExportLocation": {
                    "S3Bucket": "my-export-bucket",
                    "S3Prefix": "exports/"
                },
                "Status": "active",
                "StatusMessage": "updating"
            }
        ]
    }

**Example 6: To confirm the export task is complete**

The following ``describe-export-image-tasks`` example confirms the export task has finished and the resulting VMDK file is available in S3 at ``my-export-bucket/exports/export-ami-1234567890abcdef0.vmdk``. ::

    aws ec2 describe-export-image-tasks \
        --export-image-task-ids export-ami-1234567890abcdef0

Output for a completed export task::

    {
        "ExportImageTasks": [
            {
                "ExportImageTaskId": "export-ami-1234567890abcdef0",
                "S3ExportLocation": {
                    "S3Bucket": "my-export-bucket",
                    "S3Prefix": "exports/"
                },
                "Status": "completed"
            }
        ]
    }

For more information, see `VM Import/Export <https://docs.aws.amazon.com/vm-import/latest/userguide/>`__ in the *VM Import/Export User Guide*.
