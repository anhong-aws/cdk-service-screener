
import boto3
import json
import boto3
import datetime

def getMessages(params,resultInfo):
    custCode = params.get('custCode', 'NONE')
    outputUrl = params.get('outputUrl', 'NONE')
    transactionId = params.get('transactionId', 'NONE')
    now = datetime.datetime.now()
    formatted_time = f"{now:%Y-%m-%d %H:%M:%S}"
    message = {
                "transactionId": transactionId,
                "parentType": "service-screener",
                "subType": "reporter-completed",
                "statusCode": resultInfo["statusCode"],
                "body": resultInfo["body"],
                "custCode": custCode,
                "outputUrl": outputUrl,
                "responseTime": formatted_time
            }
    return json.dumps(message)

def run_sns_operations(params, resultInfo):
    topic_name="service-screener-topic"
    topic_arn = check_topic_existence(topic_name)
    message = getMessages(params,resultInfo)
    # 发布消息到主题
    subject = 'notify report status'
    type = 'notify'
    custCode = params.get('custCode', 'NONE')
    publish_message_to_topic(topic_arn, subject, message, custCode, type)



def get_sns():
    sns_client = boto3.client('sns')
    return sns_client

def check_topic_existence(topic_name):
    sns_client = get_sns()
    response = sns_client.list_topics()
    topics = response['Topics']
    for topic in topics:
        if topic_name in topic['TopicArn']:
            return topic['TopicArn']  # 如果主题已存在，返回现有主题的 ARN
    return None

def publish_message_to_topic(topic_arn, subject, default_message, cust_code, type='alarm'):
    print(f"开始发布sns, 邮件标题: {subject}")
    if topic_arn:
        # 发布消息到 SNS 主题
        sns_client = get_sns()
        message = {
            "default": default_message,
            # "sms": sms_message,
            # "email": email_message,
        }
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=json.dumps(message),
            MessageStructure="json",
            MessageAttributes={
                'type': {
                    'DataType': 'String',
                    'StringValue': type
                },
                'account_id': {
                    'DataType': 'String',
                    'StringValue': cust_code
                }
            }
        )
        print(response['MessageId'])
        print(f"Message published successfully.Message: {default_message}")
        print("发布sns结束")

