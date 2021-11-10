# AWS EventBridge Daylight Savings Time Updater

Lambda Function which can be executed to updated EventBridge rules to compensate for Daylight Saving changes.

## How to use

* Tie an EventBridge rule to run every Sunday at 2:15AM ( DST changes occur on Sunday's at 2AM ). 
    * This cron rule would be `cron(15 7 ? * SUN *)`
* Add this Lambda Function as a trigger for that rule
* Add all relevant EventBridge rules (including the one outlined above) into the array `eventbridge_rules` such that they will be covered by this function