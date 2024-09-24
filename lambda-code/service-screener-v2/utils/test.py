import boto3

# 创建 AWS Organizations 客户端
org_client = boto3.client('organizations')

# 定义要修改的 AWS 账号 ID
account_id = 'account_id'  # 替换为您要修改的 AWS 账号 ID

# 定义要删除的 SCP 策略 ARN
scp_arn_to_remove = 'arn:aws:organizations::aws:policy/service_control_policy/p-FullAWSAccess'  # 替换为要删除的 SCP 策略 ARN

# 定义要添加的 SCP 策略 ARN
scp_arn_to_add = 'arn:aws:organizations::456950453041:policy/o-xa9wi9ui42/service_control_policy/p-19280rn2'  # 替换为要添加的 SCP 策略 ARN

# aws帐号删除附加的 SCP 策略
org_client.detach_policy(PolicyId=scp_arn_to_remove, TargetId=account_id)

print(f"SCP 策略 {scp_arn_to_remove} 已从 AWS 账号 {account_id} 中删除")

# 添加现有的 SCP 策略

print(f"SCP 策略 {scp_arn_to_add} 已添加到 AWS 账号 {account_id}")
