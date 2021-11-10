import os
import time
import boto3

client = boto3.client('events')

eventbridge_rules = [
    '<EVENT BRIDGE RULES HERE>'
]

os.environ['TZ'] = 'EST5EDT'
time.tzset()

## Returns the offset when compared to UTC time
# Returns 0: No change
# Returns -1: Gained an hour against UTC (going into Daylight Savings Time)
# Returns 1: Lost an hour against UTC (going into Standard Time)
def daylight_offset(day_offset=1):
    today_is_daylight_savings = time.localtime().tm_isdst
    yesterday_is_daylight_savings = time.localtime(time.time()-(day_offset*86400)).tm_isdst
    offset = today_is_daylight_savings-yesterday_is_daylight_savings
    return offset * -1

## Given a cron string update it if the offset is different
def cronjob_update(crontime, offset):
    # Get the hour and update it with the offset
    crontime_split = crontime.split(' ')
    hour_idx = int(crontime_split[1])
    modified_hour = hour_idx + offset
    
    # Edge Cases
    if modified_hour == 24:
        modified_hour = 0
    elif modified_hour == 25:
        modified_hour = 1
    elif modified_hour == -1:
        modified_hour = 23
        
    # Create new crontime string
    crontime_split[1] = str(modified_hour)
    return ' '.join(crontime_split)

def lambda_handler(event, context):
    offset = daylight_offset()
    
    if offset != 0:
        print('Offset = %s' % str(offset))
        
        for rule in eventbridge_rules:
            describe_response = client.describe_rule(
                Name=rule
            )

            crontime = describe_response['ScheduleExpression']

            if 'cron' in crontime:
                new_crontime = cronjob_update(crontime, offset)
            
                if new_crontime != None:
                    print('[%s] %s (original) --> %s (new)' % (rule, crontime, new_crontime))
                    
                    update_response = client.put_rule(
                        Name=rule,
                        ScheduleExpression=new_crontime
                    )
                    
                    print(update_response)
                else:
                    print('[%s] No Change', rule)

