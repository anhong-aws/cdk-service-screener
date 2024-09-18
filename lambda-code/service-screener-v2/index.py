import json
import main
import os
import constants as _C
import traceback


def handler(event, context):
    # 从 SQS 事件中获取消息
    print("event:",json.dumps(event, ensure_ascii=True))
    # return
    for record in event['Records']:
        message_id = record['messageId']
        print(f"Processing message with ID: {message_id}")
        print(f"Processing body: {record['body']}")
        params = json.loads(record['body'])
        errors = validate_json_data(params)
        if (errors is not None):
            return {
                'statusCode': 500,
                'body': json.dumps(errors)
            }
        # 读取环境变量中的目录前缀
        dir_prefix = os.environ.get('DIR_PREFIX', '')
        bucket_name = os.environ.get('BUCKET_NAME', '')

        # 从 params 中获取 path,并与目录前缀拼接
        path = params.get('path', '')
        params['path'] = os.path.join(dir_prefix, path)
        if 'bucketName' not in params or not params['bucketName']:
            params['bucketName'] = bucket_name;
        params['includeCurrentAccount'] = False;
        params['crossAccounts'] = True;
        _C.TMP_DIR=params['path']
        _C.ADMINLTE_TMP_DIR = _C.TMP_DIR + '/adminlte'
        _C.ADMINLTE_DIR = _C.ADMINLTE_TMP_DIR + '/aws'
        _C.FORK_DIR = _C.TMP_DIR + '/__fork'
        _C.API_JSON = _C.FORK_DIR + '/api.json'
        # print(f"临时目录1: {_C.ADMINLTE_DIR}")
        # print(f"临时目录2: {_C.TMP_DIR}")
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
            traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
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

def validate_json_data(data):
    errors = []

    # 检查必需字段是否存在
    required_fields = ["regions", "path", "crossAccountsInfo"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # 检查字段值是否符合要求
    if "regions" in data and not isinstance(data["regions"], str) or not data["regions"]:
        errors.append("Invalid value for 'regions': must be a non-empty string")

    if "path" in data and not isinstance(data["path"], str) or not data["path"]:
        errors.append("Invalid value for 'path': must be a non-empty string")

    if "crossAccountsInfo" in data:
        if not isinstance(data["crossAccountsInfo"], dict):
            errors.append("Invalid value for 'crossAccountsInfo': must be an object")
        else:
            if "general" not in data["crossAccountsInfo"] or not isinstance(data["crossAccountsInfo"]["general"], dict):
                errors.append("Invalid value for 'crossAccountsInfo.general': must be an object")
            else:
                general = data["crossAccountsInfo"]["general"]
                if "IncludeThisAccount" not in general or not isinstance(general["IncludeThisAccount"], bool):
                    errors.append("Invalid value for 'crossAccountsInfo.general.IncludeThisAccount': must be a boolean")
                if "RoleName" not in general or not isinstance(general["RoleName"], str) or not general["RoleName"]:
                    errors.append("Invalid value for 'crossAccountsInfo.general.RoleName': must be a non-empty string")

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

# 示例 JSON 数据
json_data = {
    "regions": "us-east-1",
    "services": "ec2",
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

# 校验 JSON 数据
errors = validate_json_data(json_data)
if errors:
    print("JSON 数据不符合要求:")
    for error in errors:
        print(f"- {error}")
else:
    print("JSON 数据符合要求。")

# 示例输入

# params = {
#     "regions": "us-east-1",
#     "services": "ec2",
#     "crossAccounts": True,
#     "includeCurrentAccount": False,
#     "path": "cust01",
#     "crossAccountsInfo": {
#       "general": {
#           "IncludeThisAccount": False,
#           "RoleName": "OrganizationAccountAccessRole",
#           "ExternalId": ""
#       },
#       "accountLists": {
#           "722350150381113": {}
#       }
#   }
# }

# example_event = {
#     "Records": [
#         {
#             "messageId": "1234567890abcdef",
#             "body": json.dumps({
#                 "params": params
#             }, ensure_ascii=True)
#         }
#         ]
#     }

# 测试
# lambda_handler(example_event, None)
