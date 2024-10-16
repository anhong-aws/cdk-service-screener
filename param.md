## 调用接口参数
### SQS参数说明：
| <font style="color:rgb(36, 41, 47);">参数名</font> | <font style="color:rgb(36, 41, 47);">参数值例子</font> | <font style="color:rgb(36, 41, 47);">required/option</font> | <font style="color:rgb(36, 41, 47);">后端默认值</font> | <font style="color:rgb(36, 41, 47);">解释</font> |
| --- | --- | --- | --- | --- |
| **<font style="color:#DF2A3F;">transactionId</font>** | **<font style="color:#DF2A3F;">123</font>** | **<font style="color:#DF2A3F;">required</font>** | **<font style="color:#DF2A3F;">None</font>** | **<font style="color:#DF2A3F;">请求事务ID</font>** |
| **<font style="color:#DF2A3F;">custCode</font>** | **<font style="color:#DF2A3F;">cust01</font>** | **<font style="color:#DF2A3F;">required</font>** | **<font style="color:#DF2A3F;">None</font>** | **<font style="color:#DF2A3F;">给一个唯一客户标志作为文件保存的目录</font>** |
| **<font style="color:#DF2A3F;">regions</font>** | **<font style="color:#DF2A3F;">us-east-1,us-west-1或者ALL</font>** | **<font style="color:#DF2A3F;">required</font>** | **<font style="color:#DF2A3F;">None</font>** | **<font style="color:#DF2A3F;">ALL</font>**<br/>**<font style="color:#DF2A3F;">或者指定区域</font>**<br/>**<font style="color:#DF2A3F;">多区域用逗号隔开</font>** |
| **<font style="color:#DF2A3F;">services</font>** | **<font style="color:#DF2A3F;">EC2,S3</font>** | **<font style="color:#DF2A3F;">option</font>** | **<font style="color:#DF2A3F;">rds,ec2,iam,s3,efs,lambda,guardduty,<br>cloudfront,cloudtrail,elasticache,eks,dynamodb,<br>opensearch,kms,cloudwatch,redshift,apigateway</font>** | **<font style="color:#DF2A3F;">指定要扫描的 AWS 服务为 EC2 和 S3</font>** |
| **<font style="color:#DF2A3F;">aiReport</font>** | **<font style="color:#DF2A3F;">true</font>** | **<font style="color:#DF2A3F;">option</font>** | **<font style="color:#DF2A3F;">true</font>** | **<font style="color:#DF2A3F;">是否要AI汇总报告，默认汇总</font>** |
| <font style="color:rgb(36, 41, 47);">debug</font> | <font style="color:rgb(36, 41, 47);">true</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">False</font> | <font style="color:rgb(36, 41, 47);">启用调试模式</font> |
| <font style="color:rgb(36, 41, 47);">bucket</font> | <font style="color:rgb(36, 41, 47);">service-screener-bucket-123</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">service-screener-bucket-${accountId}</font><br/><font style="color:rgb(36, 41, 47);">存储桶目前创建在lambda所在账号上</font> | <font style="color:rgb(36, 41, 47);">指定 S3 存储桶的名称</font> |
| <font style="color:rgb(36, 41, 47);">mode</font> | <font style="color:rgb(36, 41, 47);">report</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">report</font> | <font style="color:rgb(36, 41, 47);">指定运行模式为 API 模式</font> |
| <font style="color:rgb(36, 41, 47);">tags</font> | <font style="color:rgb(36, 41, 47);">env=prod%department=hr,coe</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">None</font> | <font style="color:rgb(36, 41, 47);">指定资源标签,包括环境为生产环境和部门为人力资源和 COE</font> |
| <font style="color:rgb(36, 41, 47);">crossAccounts</font> | <font style="color:rgb(36, 41, 47);">true</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">命令行模式默认值false</font><br/><font style="color:rgb(36, 41, 47);">lambda模式默认值true</font> | <font style="color:rgb(36, 41, 47);">启用跨账户操作</font> |
| <font style="color:rgb(36, 41, 47);">workerCounts</font> | <font style="color:rgb(36, 41, 47);">5</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">4</font> | <font style="color:rgb(36, 41, 47);">指定工作线程数为 5</font> |
| <font style="color:rgb(36, 41, 47);">frameworks</font> | <font style="color:rgb(36, 41, 47);">CIS,PCI</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">None</font> | <font style="color:rgb(36, 41, 47);">指定要使用的合规性框架为 CIS 和 PCI</font> |
| <font style="color:rgb(36, 41, 47);">profile</font> | <font style="color:rgb(36, 41, 47);">true</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">false</font> | <font style="color:rgb(36, 41, 47);">启用机器中aws config的配置文件模式，比如指定default等</font> |
| <font style="color:rgb(36, 41, 47);">ztestmode</font> | <font style="color:rgb(36, 41, 47);">false</font> | <font style="color:rgb(36, 41, 47);">option</font> | <font style="color:rgb(36, 41, 47);">false</font> | <font style="color:rgb(36, 41, 47);">禁用测试模式</font> |
| **<font style="color:#DF2A3F;">crossAccountsInfo</font>** | **<font style="color:#DF2A3F;">josn object</font>** | **<font style="color:#DF2A3F;">命令行模式：option</font>**<br/>**<font style="color:#DF2A3F;">lambda模式：required</font>** | **<font style="color:#DF2A3F;">None</font>** | **<font style="color:#DF2A3F;">跨帐号检查的帐号角色配置</font>** |
|  |  |  |  |  |


| <font style="color:rgb(36, 41, 47);">参数名</font> | <font style="color:rgb(36, 41, 47);">参数值</font> | <font style="color:rgb(36, 41, 47);">required/option</font> | <font style="color:rgb(36, 41, 47);">默认值</font> | <font style="color:rgb(36, 41, 47);">解释</font> |
| --- | --- | --- | --- | --- |
| crossAccountsInfo.general | josn object | Option | {"IncludeThisAccount": false,		"RoleName": "OrganizationAccountAccessRole",			"ExternalId": ""} | 所有账号通用配置 |
| general.IncludeThisAccount | true | required | False | 是否包含当前账户 |
| general.RoleName | OrganizationAccountAccessRole | required | OrganizationAccountAccessRole | 角色名称 |
| general.ExternalId | (空字符串) | required | 空字符串 | 外部 ID |
| crossAccountsInfo.accountLists | Array | required |  | 跨张户列表 |
| **<font style="color:#DF2A3F;">accountLists[i].key</font>** | **<font style="color:#DF2A3F;">xxxxx1</font>** | **<font style="color:#DF2A3F;">required</font>** | **<font style="color:#DF2A3F;">空</font>** | **<font style="color:#DF2A3F;">账号 ID</font>** |
| **<font style="color:#DF2A3F;">accountLists[i].value</font>** | **<font style="color:#DF2A3F;">josn object</font>** | **<font style="color:#DF2A3F;">required</font>** | **<font style="color:#DF2A3F;">{}(空对象)</font>** | **<font style="color:#DF2A3F;">schema跟</font>****<font style="color:#DF2A3F;">crossAccountsInfo.</font>****<font style="color:#DF2A3F;">general相同，如果角色不同，可以单独指定</font>** |
| <font style="color:#C99103;"></font> | <font style="color:#C99103;"></font> | <font style="color:#C99103;"></font> | <font style="color:#C99103;"></font> | <font style="color:#C99103;"></font> |




### 报文范例
#### sqs发送消息报文
```json
{
  "transactionId": "1234",
  "regions": "us-east-1",
  "services": "ec2",
  "custCode": "cust01",
  "aiReport": false,
  "crossAccountsInfo": {
    "accountLists": {
      "xxxxx1": {},
      "xxxxx2": {}
    }
  }
}
```

针对不同aws帐号指定不同角色

```shell
{
  "transactionId": "1234",
	"regions": "us-east-1",
	"services": "ec2",
	"custCode": "cust01",
	"crossAccountsInfo": {
		"general": {
			"IncludeThisAccount": false,
			"RoleName": "OrganizationAccountAccessRole",
			"ExternalId": ""
		},
		"accountLists": {
			"xxxxx3": {
  			"IncludeThisAccount": false,
  			"RoleName": "SwitchAccountAccessRole",
  			"ExternalId": ""
  		}
		}
	}
}
```

## 回调接口内容范例
```json
{"transactionId": "123", "parentType": "service-screener", "subType": "reporter-completed", "statusCode": 200, "body": "\"Execution completed successfully\"", "custCode": "cust01", "outputUrl": "https://service-screener-bucket-123123.s3.amazonaws.com//tmp/cust01/output.zip?AWSAccessKeyId=ASIAWUZC6SMYXB7LZGRG&Signature=K%2CA%3D%3D&Expires=1727174216", "responseTime": "2024-09-24 09:36:57"}
```

```json
{
  "transactionId": "123",
  "parentType": "service-screener",
  "subType": "ai-summary-completed",
  "statusCode": 200,
  "body": "Execution completed successfully",
  "custCode": "cust01",
  "outputUrl": "https://xxx.s3.aws.com/xxxx", 
  "responseTime": "2024-09-24 09:36:57"
}
```

