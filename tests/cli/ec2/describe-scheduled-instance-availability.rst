**To describe an available schedule**

This example describes a schedule that occurs every week on Sunday, starting on the specified date.

Command::

  aws ec2 describe-scheduled-instance-availability --recurrence Frequency=Weekly,Interval=1,OccurrenceDays=[1] --first-slot-start-time-range EarliestTime=2016-01-31T00:00:00Z,LatestTime=2016-01-31T04:00:00Z

Output::

  {
    "ScheduledInstanceAvailabilitySet": [
      {
          "AvailabilityZone": "us-west-2b",
          "TotalScheduledInstanceHours": 1219,
          "PurchaseToken": "eyJ2IjoiMSIsInMiOjEsImMiOi...",
          "MinTermDurationInDays": 366,
          "AvailableInstanceCount": 20,
          "Recurrence": {
              "OccurrenceDaySet": [
                  1
              ],
              "Interval": 1,
              "Frequency": "Weekly",
              "OccurrenceRelativeToEnd": false
          },
          "Platform": "Linux/UNIX",
          "FirstSlotStartTime": "2016-01-31T00:00:00Z",
          "MaxTermDurationInDays": 366,
          "SlotDurationInHours": 23,
          "NetworkPlatform": "EC2-VPC",
          "InstanceType": "c4.large",
          "HourlyPrice": "0.095"
      },
      ...
    ]
  }

To narrow the results, you can add filters that specify the operating system, network, and instance type.

Command:

  --filters Name=platform,Values=Linux/UNIX Name=network-platform,Values=EC2-VPC Name=instance-type,Values=c4.large

**To describe available schedules for a specific instance type**

This example narrows the results to Linux/UNIX ``c4.large`` schedules in EC2-VPC.

Command::

  aws ec2 describe-scheduled-instance-availability --recurrence Frequency=Weekly,Interval=1,OccurrenceDays=[1] --first-slot-start-time-range EarliestTime=2016-01-31T00:00:00Z,LatestTime=2016-01-31T04:00:00Z --filters Name=platform,Values=Linux/UNIX Name=network-platform,Values=EC2-VPC Name=instance-type,Values=c4.large
