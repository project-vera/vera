**To describe the snapshot attributes for a snapshot**

The following ``describe-snapshot-attribute`` example lists the accounts with which a snapshot is shared. ::

    aws ec2 describe-snapshot-attribute \
        --snapshot-id snap-01234567890abcedf \
        --attribute createVolumePermission

Output::

    {
        "SnapshotId": "snap-01234567890abcedf",
        "CreateVolumePermissions": [
            {
                "UserId": "123456789012"
            }
        ]
    }

**To describe the snapshot attributes for a public snapshot**

The following ``describe-snapshot-attribute`` example lists the create volume permissions for a public snapshot. ::

    aws ec2 describe-snapshot-attribute \
        --snapshot-id snap-0abc1234def567890 \
        --attribute createVolumePermission

Output::

    {
        "SnapshotId": "snap-0abc1234def567890",
        "CreateVolumePermissions": [
            {
                "Group": "all"
            }
        ]
    }

For more information, see `Share an Amazon EBS snapshot <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html#share-unencrypted-snapshot>`__ in the *Amazon Elastic Compute Cloud User Guide*.
