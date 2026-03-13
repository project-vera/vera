**To view the status of account access to the serial console**

The following ``get-serial-console-access-status`` example determines whether serial console access is enabled for your account. ::

    aws ec2 get-serial-console-access-status

Output::

    {
        "SerialConsoleAccessEnabled": true
    }

**To return the serial console access flag as text**

The following ``get-serial-console-access-status`` example returns only the access flag for machine-consumable checks. ::

    aws ec2 get-serial-console-access-status \
        --query "SerialConsoleAccessEnabled" \
        --output text

Output::

    true

For more information, see `EC2 Serial Console <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-serial-console.html>`__ in the *Amazon EC2 User Guide*.
