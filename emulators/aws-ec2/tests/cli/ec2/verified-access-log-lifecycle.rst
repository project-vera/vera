**Example 1: To create a Verified Access instance with a Name tag**

The following ``create-verified-access-instance`` example creates a Verified Access instance tagged with a Name for identification. ::

    aws ec2 create-verified-access-instance \
        --tag-specifications 'ResourceType=verified-access-instance,Tags=[{Key=Name,Value=my-va-instance}]'

Output::

    {
        "VerifiedAccessInstance": {
            "VerifiedAccessInstanceId": "vai-0ce000c0b7643abea",
            "Description": "",
            "VerifiedAccessTrustProviders": [],
            "CreationTime": "2023-08-25T18:27:56",
            "LastUpdatedTime": "2023-08-25T18:27:56",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-va-instance"
                }
            ]
        }
    }

**Example 2: To create a Verified Access trust provider using AWS Identity Center**

The following ``create-verified-access-trust-provider`` example creates a user-type trust provider backed by IAM Identity Center and associates a policy reference name. ::

    aws ec2 create-verified-access-trust-provider \
        --trust-provider-type user \
        --user-trust-provider-type iam-identity-center \
        --policy-reference-name idc \
        --tag-specifications 'ResourceType=verified-access-trust-provider,Tags=[{Key=Name,Value=my-va-trust-provider}]'

Output::

    {
        "VerifiedAccessTrustProvider": {
            "VerifiedAccessTrustProviderId": "vatp-0bb32de759a3e19e7",
            "Description": "",
            "TrustProviderType": "user",
            "UserTrustProviderType": "iam-identity-center",
            "PolicyReferenceName": "idc",
            "CreationTime": "2023-08-25T18:40:36",
            "LastUpdatedTime": "2023-08-25T18:40:36",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "my-va-trust-provider"
                }
            ]
        }
    }

**Example 3: To attach a trust provider to a Verified Access instance**

The following ``attach-verified-access-trust-provider`` example attaches the trust provider created in Example 2 to the Verified Access instance created in Example 1. ::

    aws ec2 attach-verified-access-trust-provider \
        --verified-access-instance-id vai-0ce000c0b7643abea \
        --verified-access-trust-provider-id vatp-0bb32de759a3e19e7

Output::

    {
        "VerifiedAccessTrustProvider": {
            "VerifiedAccessTrustProviderId": "vatp-0bb32de759a3e19e7",
            "Description": "",
            "TrustProviderType": "user",
            "UserTrustProviderType": "iam-identity-center",
            "PolicyReferenceName": "idc",
            "CreationTime": "2023-08-25T18:40:36",
            "LastUpdatedTime": "2023-08-25T18:40:36"
        },
        "VerifiedAccessInstance": {
            "VerifiedAccessInstanceId": "vai-0ce000c0b7643abea",
            "Description": "",
            "VerifiedAccessTrustProviders": [
                {
                    "VerifiedAccessTrustProviderId": "vatp-0bb32de759a3e19e7",
                    "TrustProviderType": "user",
                    "UserTrustProviderType": "iam-identity-center"
                }
            ],
            "CreationTime": "2023-08-25T18:27:56",
            "LastUpdatedTime": "2023-08-25T18:27:56"
        }
    }

**Example 4: To enable CloudWatch access logging for a Verified Access instance**

The following ``modify-verified-access-instance-logging-configuration`` example enables access logging for Verified Access instance ``vai-0ce000c0b7643abea``, directing logs to the CloudWatch Logs group ``my-va-log-group``. ::

    aws ec2 modify-verified-access-instance-logging-configuration \
        --verified-access-instance-id vai-0ce000c0b7643abea \
        --access-logs CloudWatchLogs={Enabled=true,LogGroup=my-va-log-group}

Output::

    {
        "LoggingConfiguration": {
            "VerifiedAccessInstanceId": "vai-0ce000c0b7643abea",
            "AccessLogs": {
                "S3": {
                    "Enabled": false
                },
                "CloudWatchLogs": {
                    "Enabled": true,
                    "DeliveryStatus": {
                        "Code": "success"
                    },
                    "LogGroup": "my-va-log-group"
                },
                "KinesisDataFirehose": {
                    "Enabled": false
                },
                "LogVersion": "ocsf-1.0.0-rc.2",
                "IncludeTrustContext": false
            }
        }
    }

**Example 5: To verify the logging configuration for a Verified Access instance**

The following ``describe-verified-access-instance-logging-configurations`` example retrieves the current logging configuration for the Verified Access instance to confirm that CloudWatch logging is active. ::

    aws ec2 describe-verified-access-instance-logging-configurations \
        --verified-access-instance-ids vai-0ce000c0b7643abea

Output::

    {
        "LoggingConfigurations": [
            {
                "VerifiedAccessInstanceId": "vai-0ce000c0b7643abea",
                "AccessLogs": {
                    "S3": {
                        "Enabled": false
                    },
                    "CloudWatchLogs": {
                        "Enabled": true,
                        "DeliveryStatus": {
                            "Code": "success"
                        },
                        "LogGroup": "my-va-log-group"
                    },
                    "KinesisDataFirehose": {
                        "Enabled": false
                    },
                    "LogVersion": "ocsf-1.0.0-rc.2",
                    "IncludeTrustContext": false
                }
            }
        ]
    }

**Example 6: To describe the Verified Access trust provider**

The following ``describe-verified-access-trust-providers`` example retrieves details about the trust provider to confirm its configuration. ::

    aws ec2 describe-verified-access-trust-providers \
        --verified-access-trust-provider-ids vatp-0bb32de759a3e19e7

Output::

    {
        "VerifiedAccessTrustProviders": [
            {
                "VerifiedAccessTrustProviderId": "vatp-0bb32de759a3e19e7",
                "Description": "",
                "TrustProviderType": "user",
                "UserTrustProviderType": "iam-identity-center",
                "PolicyReferenceName": "idc",
                "CreationTime": "2023-08-25T18:40:36",
                "LastUpdatedTime": "2023-08-25T18:40:36",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "my-va-trust-provider"
                    }
                ]
            }
        ]
    }

**Example 7: To detach a trust provider from a Verified Access instance**

The following ``detach-verified-access-trust-provider`` example detaches the trust provider from the Verified Access instance before cleanup. ::

    aws ec2 detach-verified-access-trust-provider \
        --verified-access-instance-id vai-0ce000c0b7643abea \
        --verified-access-trust-provider-id vatp-0bb32de759a3e19e7

Output::

    {
        "VerifiedAccessTrustProvider": {
            "VerifiedAccessTrustProviderId": "vatp-0bb32de759a3e19e7",
            "Description": "",
            "TrustProviderType": "user",
            "UserTrustProviderType": "iam-identity-center",
            "PolicyReferenceName": "idc",
            "CreationTime": "2023-08-25T18:40:36",
            "LastUpdatedTime": "2023-08-25T18:40:36"
        },
        "VerifiedAccessInstance": {
            "VerifiedAccessInstanceId": "vai-0ce000c0b7643abea",
            "Description": "",
            "VerifiedAccessTrustProviders": [],
            "CreationTime": "2023-08-25T18:27:56",
            "LastUpdatedTime": "2023-08-25T18:27:56"
        }
    }
