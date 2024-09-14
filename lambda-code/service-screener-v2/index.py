import json
import main
import os
import constants as _C
import traceback


def lambda_handler(event, context):
    # 从 SQS 事件中获取消息
    for record in event['Records']:
        message_id = record['messageId']
        print(f"Processing message with ID: {message_id}")

        message_body = json.loads(record['body'])
        params = message_body.get('params', {})
        # 读取环境变量中的目录前缀
        dir_prefix = os.environ.get('DIR_PREFIX', '')

        # 从 params 中获取 path,并与目录前缀拼接
        path = params.get('path', '')
        params['path'] = os.path.join(dir_prefix, path)
        _C.TMP_DIR=params['path']
        _C.ADMINLTE_TMP_DIR = _C.TMP_DIR + '/adminlte'
        _C.ADMINLTE_DIR = _C.ADMINLTE_TMP_DIR + '/aws'
        _C.FORK_DIR = _C.TMP_DIR + '/__fork'
        _C.API_JSON = _C.FORK_DIR + '/api.json'
        print(f"临时目录1: {_C.ADMINLTE_DIR}")

        print(f"临时目录2: {_C.TMP_DIR}")
        # return
        if os.path.exists(_C.ADMINLTE_DIR):
            print(f"临时目录 '{_C.ADMINLTE_DIR}' 已存在")
        else:
            try:
                # 如果不存在,则创建目录
                os.makedirs(_C.ADMINLTE_DIR)
                print(f"临时目录 '{_C.ADMINLTE_DIR}' 已创建")
            except OSError as e:
                print(f"无法创建临时目录 '{_C.ADMINLTE_DIR}': {e.strerror}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('Error occurred while creating temporary directory')
                }
        
        if os.path.exists(_C.FORK_DIR):
            print(f"临时目录FORK_DIR '{_C.FORK_DIR}' 已存在")
        else:
            try:
                # 如果不存在,则创建目录
                os.makedirs(_C.FORK_DIR)
                print(f"临时目录FORK_DIR '{_C.FORK_DIR}' 已创建")
            except OSError as e:
                print(f"无法创建临时目录FORK_DIR '{_C.FORK_DIR}': {e.strerror}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('Error occurred while creating FORK_DIR temporary directory')
                }
        try:
            # 调用main.py中的main函数
            main.main(params)
        except Exception as e:
            # 获取堆栈跟踪信息
            traceback_str = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
            print(f"Error occurred while executing main function: {str(e)}")
            print(traceback_str)
            return {
                'statusCode': 500,
                'body': json.dumps('Error occurred while processing the request')
            }
    return {
        'statusCode': 200,
        'body': json.dumps('Execution completed successfully')
    }

# 示例输入

params = {
    "regions": "us-east-1",
    "services": "ec2",
    "bucketName": "anhongtest1",
    "crossAccounts": True,
    "includeCurrentAccount": False,
    "path": "cust01",
    "crossAccountsInfo": {
      "general": {
          "IncludeThisAccount": False,
          "RoleName": "OrganizationAccountAccessRole",
          "ExternalId": ""
      },
      "accountLists": {
          "722350150383": {}
      }
  }
}

example_event = {
    'Records': [
        {
            'messageId': '1234567890abcdef',
            'body': json.dumps({
                'params': params
            })
        }
    ]
}

# 测试
lambda_handler(example_event, None)
