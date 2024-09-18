import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
/**
 *
导入所需的 AWS CDK 库
创建 SQS 队列
创建 Lambda 函数,并添加一个 Python 层
创建 S3 存储桶
为 Lambda 函数添加 SQS 事件源映射
创建 SNS 主题
为 Lambda 函数添加 S3 事件通知
为 Lambda 函数添加 SNS 主题订阅
为 SQS 队列添加死信队列
 */
export declare class CdkServiceScreenerStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps);
}
