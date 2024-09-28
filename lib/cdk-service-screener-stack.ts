import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dotenv from 'dotenv' 
dotenv.config()
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
export class CdkServiceScreenerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    if (!process.env.DIR_PREFIX) throw Error('empty environment variables');

    // 创建 FIFO SQS 队列
    const queue = new sqs.Queue(this, 'ServiceScreenerQueue', {
      visibilityTimeout: cdk.Duration.seconds(1000),
      queueName: 'service-screener-queue.fifo',
      fifo: true, // 设置为 FIFO 队列
      contentBasedDeduplication: true, // 启用基于内容的重复数据删除
    });

    // Get the account ID
    const accountId = cdk.Stack.of(this).account;
    // 创建存储桶名称
    const bucketName = `service-screener-bucket-${accountId}`;
    // 创建 S3 存储桶
    const bucket = new s3.Bucket(this, 'ServiceScreenerBucket', {
      bucketName: bucketName,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 创建 Lambda 执行角色并附加策略
    const lambdaExecutionRole = new iam.Role(this, 'ScreennerLambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'), // Lambda 服务的身份标识
    });

    // 为 Lambda 执行角色添加策略
    lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents', 'cloudwatch:*'],
      resources: ['*'], // 允许 Lambda 写入 CloudWatch Logs
    }));

    // 为 Lambda 执行角色添加 sts:AssumeRole 权限，允许切换角色
    lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
      actions: ['sts:AssumeRole','iam:GetAccountSummary'],
      resources: ['*'], // 允许扮演任何角色
    }));

    // 为 Lambda 执行角色添加所有 SNS 权限
    lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        'sns:ListTopics',
        'sns:GetTopicAttributes',
        'sns:ListSubscriptionsByTopic',
        'sns:Publish',
        'sns:Receive'
      ],
      resources: ['*'], // 这里资源可以根据你的实际需求进行限制
    }));
    // 启动lambda insight
    lambdaExecutionRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLambdaInsightsExecutionRolePolicy')
    );
    // 为 Lambda 执行角色添加上传 S3 权限
    lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        's3:PutObject',
        's3:GetObject',
        's3:ListBucket'
      ],
      resources: [
        `${bucket.bucketArn}/*`, // 允许 Lambda 上传和获取对象
        bucket.bucketArn // 允许 Lambda 列出存储桶内容
      ],
    }));

    
    // 创建 Lambda 层
    // 使用./package_lambda_layer.sh脚本来生成依赖层的包
    const screenerDepsLayer = new lambda.LayerVersion(this, 'ScreenerDepsLayer', {
      code: lambda.Code.fromAsset('./lambda-code/layer-deps'), // 替换为您的依赖项目录路径
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_10], // 指定兼容的 Python 运行时版本
      description: 'Screener Python dependencies layer'
    });

    // 创建 Python Lambda 函数
    const screenerLambda = new lambda.Function(this, 'ScreenerLambda', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',         // 指定 Lambda 处理程序的入口函数
      code: lambda.Code.fromAsset('lambda-code/service-screener-v2'),
      role: lambdaExecutionRole,        // 关联 Lambda 执行角色
      memorySize: 256,                  // 内存256M
      timeout: cdk.Duration.minutes(15), // 设置超时时间为 15 分钟
      environment: {
        BUCKET_NAME: bucket.bucketName,
        DIR_PREFIX: process.env.DIR_PREFIX,
        AWS_AK: process.env.AWS_AK!,
        AWS_SK: process.env.AWS_SK!,
        AWS_REGION_CODE: process.env.AWS_REGION_CODE!,
        AWS_MODEL_ID: process.env.AWS_MODEL_ID!,
        AWS_MOCK: process.env.AWS_MOCK!,
        LOG_LEVEL: 'INFO'
      },
      layers: [screenerDepsLayer]         // 添加依赖项层
    });


    // 为 Lambda 函数添加 SQS 事件源映射
    // const eventSource = new lambdaEventSources.SqsEventSource(queue);
    const eventSource = new lambdaEventSources.SqsEventSource(queue, {
      batchSize: 1, // 设置每次批量获取 1 条消息
    });
    screenerLambda.addEventSource(eventSource);

    // 创建 SNS 主题
    const topic = new sns.Topic(this, 'ServiceScreenerTopic', {
      topicName: 'service-screener-topic',
    });
    // sns订阅一个url
    // topic.addSubscription(new subscriptions.UrlSubscription('https://example.com/'));
  }
}
