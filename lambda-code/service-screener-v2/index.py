import json
import main
import os
import constants as _C
import traceback
from utils.sns_main import run_sns_operations
import pathlib

def handler(event, context):

    try:
        # 从 SQS 事件中获取消息
        print("event:",json.dumps(event, ensure_ascii=True))
        print("root dir:",str(pathlib.Path.cwd()))
        # 读取环境变量中的目录前缀
        dir_prefix = os.environ.get('DIR_PREFIX', '')
        bucket_name = os.environ.get('BUCKET_NAME', '')
        AWS_AK = os.environ.get('AWS_AK', '')
        print("AWS_AK:",AWS_AK)
        print("bucket_name:",bucket_name)
        # return
        resultInfo = {
            'statusCode': 200,
            'body': json.dumps('Execution completed successfully')
        }
        for record in event['Records']:
            message_id = record['messageId']
            print(f"Processing message with ID: {message_id}")
            print(f"Processing body: {record['body']}")
            params = json.loads(record['body'])
            errors = validate_json_data(params)
            if (errors is not None):
                resultInfo = {
                    'statusCode': 400,
                    'body': json.dumps(errors)
                }
                run_sns_operations(params=params, resultInfo=resultInfo)
                return resultInfo
            if not dir_prefix:
                dir_prefix = "/tmp"
            # 从 params 中获取 path,并与目录前缀拼接
            custCode = params.get('custCode', '')
            transactionId = params.get('transactionId', '')
            aiReport = params.get('aiReport', True)
            params['aiReport'] = aiReport
            params['path'] = os.path.join(dir_prefix, custCode)
            params['bucketName'] = bucket_name;
            params['crossAccounts'] = True;
            _C.TMP_DIR=params['path']
            _C.ADMINLTE_TMP_DIR = _C.TMP_DIR + '/adminlte'
            _C.ADMINLTE_DIR = _C.ADMINLTE_TMP_DIR + '/aws'
            _C.FORK_DIR = _C.TMP_DIR + '/__fork'
            _C.API_JSON = _C.FORK_DIR + '/api.json'
            
            if os.path.exists(_C.ADMINLTE_DIR):
                print(f"临时目录 '{_C.ADMINLTE_DIR}' 已存在")
            else:
                # 如果不存在,则创建目录
                os.makedirs(_C.ADMINLTE_DIR)
                print(f"临时目录 '{_C.ADMINLTE_DIR}' 已创建")
            
            if os.path.exists(_C.FORK_DIR):
                print(f"临时目录FORK_DIR '{_C.FORK_DIR}' 已存在")
            else:
                # 如果不存在,则创建目录
                os.makedirs(_C.FORK_DIR)
                print(f"临时目录FORK_DIR '{_C.FORK_DIR}' 已创建")
            # 调用main.py中的main函数
            uploadToS3Result = main.main(params)
            params['transactionId'] = transactionId
            # 回调通知
            if uploadToS3Result:
                run_sns_operations(params=params, resultInfo=resultInfo)
            else:
                resultInfo={
                    'statusCode': 500,
                    'body': 'Error occurred while processing the request'
                }
                run_sns_operations(params=params, resultInfo=resultInfo)
    
    except Exception as e:
        # 获取堆栈跟踪信息
        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print(f"Error occurred while executing main function: {str(e)}")
        print(traceback_str)
        resultInfo = {
            'statusCode': 500,
            'body': f"Error occurred while executing main function: {str(e)}"
        }
        params['transactionId'] = transactionId
        run_sns_operations(params=params, resultInfo=resultInfo)
        return resultInfo
    return resultInfo

def validate_json_data(data):
    errors = []

    # 检查必需字段是否存在
    required_fields = ["regions", "custCode", "crossAccountsInfo"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
            return errors

    # 检查字段值是否符合要求
    regions = data.get("regions")
    if not isinstance(regions, str) or not regions:
        errors.append("Invalid value for 'regions': must be a non-empty string")


    custCode = data.get("custCode")
    if not isinstance(custCode, str) or not custCode:
        errors.append("Invalid value for 'custCode': must be a non-empty string")

    if "crossAccountsInfo" in data:
        if not isinstance(data["crossAccountsInfo"], dict):
            errors.append("Invalid value for 'crossAccountsInfo': must be an object")
        else:
            if "general" not in data["crossAccountsInfo"] or not isinstance(data["crossAccountsInfo"]["general"], dict):
                data["crossAccountsInfo"]["general"] = {
                    "IncludeThisAccount": False,
                    "RoleName": "OrganizationAccountAccessRole",
                    "ExternalId": ""
                }
            if "accountLists" not in data["crossAccountsInfo"] or not isinstance(data["crossAccountsInfo"]["accountLists"], dict):
                errors.append("Invalid value for 'crossAccountsInfo.accountLists': must be an object")
            else:
                for account_id, account_info in data["crossAccountsInfo"]["accountLists"].items():
                    if not account_id.isdigit():
                        errors.append(f"Invalid account ID '{account_id}': must be a string of digits")
                    if not isinstance(account_info, dict):
                        errors.append(f"Invalid value for 'crossAccountsInfo.accountLists.{account_id}': must be an object")

    if errors:
        return errors
    else:
        return None


# 示例输入
# params = {
#     "regions": "us-east-1",
#     # "services": "dynamodb,eks,ec2",
#     "custCode": f"{_C.ROOT_DIR}/../tmp/cust01",
#     "aiReport": True,
#     # "profile": "payer01",
#     "crossAccountsInfo": {
#       "general": {
#           "IncludeThisAccount": False,
#           "RoleName": "OrganizationAccountAccessRole",
#           "ExternalId": ""
#       },
#       "accountLists": {
#           "722350150383": {}
#         #   "611234940057": {}
#       }
#   }
# }

# example_event = {
#     "Records": [
#         {
#             "messageId": "1234567890abcdef",
#             "body": json.dumps(params, ensure_ascii=True)
#         }
#         ]
#     }

# handler(example_event, None)

# from utils.PromptHelper import PromptHelper

# def test():

#     promptHelper = PromptHelper()
#     promptHelper.getPromptByService("default", "EC2")
#     promptHelper.getPromptByServices("default", "EC2,lambda")

# test()