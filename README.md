# Welcome to your CDK service-screener-v2 project

基于AWS现代化架构的六大支柱，对AWS服务做审计，并通过AI做报告汇总

![Local Image](./doc/service-screener-v4.png)

## Installing
### 配置

在项目目录下创建.env文件

配置范例如下
```
# 项目相关设置--保存报告输出文件的目录
DIR_PREFIX=/tmp

# AWS Bedrock相关设置
AWS_AK=123
AWS_SK=123
AWS_REGION_CODE=us-west-2
AWS_BEDROCK_CLAUDE_SONNET=anthropic.claude-3-haiku-20240307-v1:0
AWS_AI_MOCK=false
# AWS_BEDROCK_CLAUDE_SONNET=anthropic.claude-3-sonnet-20240229-v1:0
```
⚠️如果没有bedrock环境，可以把AWS_AI_MOCK设置为true
### 安装命令
```
git clone https://github.com/anhong-aws/cdk-service-screener.git
cd cdk-service-screener
# 构建lambda layer
./package_lambda_layer.sh
# deploy this stack to your default AWS account/region
cdk deploy --all --require-approval never
```
## 运行测试
1.发送请求到sqs队列

![sqs](./doc/sqs.png)

跨帐号检查请求范例：
- 默认不体检本身，
- 默认跨账户的角色名为OrganizationAccountAccessRole
```
{
  "transactionId": "123",
  "regions": "us-east-1",
  "custCode": "cust01",
  "crossAccountsInfo": {
    "accountLists": {
      "123123238899": {},
      "124124848323": {}
    }
  }
}
```

跨帐号检查请求范例：
- 体检lambda所在的aws账户+跨账户体检
- RoleName为跨账户的体检角色
```
{
  "transactionId": "123",
  "regions": "us-east-1",
  "custCode": "cust01",
  "crossAccountsInfo": {
		"general": {
			"IncludeThisAccount": true,
			"RoleName": "OrganizationAccountAccessRole",
			"ExternalId": ""
		},
    "accountLists": {
      "123123238899": {},
      "124124848323": {}
    }
  }
}
```

只检查lambda运行的aws帐号的请求范例
```
{
  "transactionId": "123",
	"regions": "us-east-1",
	"services": "ec2",
	"custCode": "cust01",
  "crossAccounts": false
}
```
针对跨账户的个别aws帐号指定不同角色
```
{
  "transactionId": "123",
	"regions": "us-east-1",
	"services": "ec2",
	"custCode": "cust01",
	"crossAccountsInfo": {
		"accountLists": {
			"123123238899": {
  			"RoleName": "SwitchAccountAccessRole"
  		}
		}
	}
}
```
这里面执行的环境需要对体检的帐号要有权限，这里采用默认角色，更多[参数说明](param.md)

2.服务体检报告处理后，发送消息到sns，比如在sns上配置邮件订阅，或者http订阅
![response](doc/response_message.png)
通过消息上的url下载报告

3.报告范例页面如下
![alt text](doc/report.png)