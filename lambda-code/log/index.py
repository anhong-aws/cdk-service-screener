# index.py
import json
from log_main import save_log

def handler(event: dict, context: dict) -> dict:
    """
    Handles SNS messages and saves logs.

    Args:
        event (dict): The event data.
        context (dict): The context data.

    Returns:
        dict: A response or an empty dictionary.
    """
    print("event:", event)
    if 'Records' in event and len(event['Records']) > 0:
        try:
            # 解析 SNS 消息
            sns_message = event['Records'][0]['Sns']['Message']
            # 在这里处理 SNS 消息
            print("Received SNS message:", sns_message)
            # 保存日志或执行其他操作
            save_log(sns_message)
        except KeyError:
            return {"error": "Invalid SNS message format"}
    else:
        return {}
