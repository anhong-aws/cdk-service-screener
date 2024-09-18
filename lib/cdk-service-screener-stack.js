"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CdkServiceScreenerStack = void 0;
const cdk = require("aws-cdk-lib");
const sqs = require("aws-cdk-lib/aws-sqs");
const lambda = require("aws-cdk-lib/aws-lambda");
const s3 = require("aws-cdk-lib/aws-s3");
const lambdaEventSources = require("aws-cdk-lib/aws-lambda-event-sources");
const sns = require("aws-cdk-lib/aws-sns");
const iam = require("aws-cdk-lib/aws-iam");
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
class CdkServiceScreenerStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        // 创建 FIFO SQS 队列
        const queue = new sqs.Queue(this, 'ServiceScreenerQueue', {
            visibilityTimeout: cdk.Duration.seconds(300),
            queueName: 'service-screener-queue.fifo',
            fifo: true,
            contentBasedDeduplication: true, // 启用基于内容的重复数据删除
        });
        // 创建 S3 存储桶
        const bucket = new s3.Bucket(this, 'ServiceScreenerBucket', {
            bucketName: 'service-screener-bucket',
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
            actions: ['sts:AssumeRole'],
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
        lambdaExecutionRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLambdaInsightsExecutionRolePolicy'));
        // 为 Lambda 执行角色添加上传 S3 权限
        lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
            actions: [
                's3:PutObject',
                's3:GetObject',
                's3:ListBucket'
            ],
            resources: [
                `${bucket.bucketArn}/*`,
                bucket.bucketArn // 允许 Lambda 列出存储桶内容
            ],
        }));
        // 创建 Lambda 层
        // 使用./package_lambda_layer.sh脚本来生成依赖层的包
        const screenerDepsLayer = new lambda.LayerVersion(this, 'ScreenerDepsLayer', {
            code: lambda.Code.fromAsset('./lambda-code/layer-deps'),
            compatibleRuntimes: [lambda.Runtime.PYTHON_3_10],
            description: 'Screener Python dependencies layer'
        });
        // 创建 Python Lambda 函数
        const screenerLambda = new lambda.Function(this, 'ScreenerLambda', {
            runtime: lambda.Runtime.PYTHON_3_10,
            handler: 'index.handler',
            code: lambda.Code.fromAsset('lambda_code/service-screener-v2'),
            role: lambdaExecutionRole,
            memorySize: 256,
            timeout: cdk.Duration.minutes(3),
            environment: {
                BUCKET_NAME: bucket.bucketName,
                LOG_LEVEL: 'INFO'
            },
            layers: [screenerDepsLayer] // 添加依赖项层
        });
        // 为 Lambda 函数添加 SQS 事件源映射
        const eventSource = new lambdaEventSources.SqsEventSource(queue);
        screenerLambda.addEventSource(eventSource);
        // 创建 SNS 主题
        const topic = new sns.Topic(this, 'ServiceScreenerTopic', {
            topicName: 'service-screener-topic',
        });
    }
}
exports.CdkServiceScreenerStack = CdkServiceScreenerStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiY2RrLXNlcnZpY2Utc2NyZWVuZXItc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJjZGstc2VydmljZS1zY3JlZW5lci1zdGFjay50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSxtQ0FBbUM7QUFFbkMsMkNBQTJDO0FBQzNDLGlEQUFpRDtBQUNqRCx5Q0FBeUM7QUFDekMsMkVBQTJFO0FBRTNFLDJDQUEyQztBQUUzQywyQ0FBMkM7QUFDM0M7Ozs7Ozs7Ozs7O0dBV0c7QUFDSCxNQUFhLHVCQUF3QixTQUFRLEdBQUcsQ0FBQyxLQUFLO0lBQ3BELFlBQVksS0FBZ0IsRUFBRSxFQUFVLEVBQUUsS0FBc0I7UUFDOUQsS0FBSyxDQUFDLEtBQUssRUFBRSxFQUFFLEVBQUUsS0FBSyxDQUFDLENBQUM7UUFFeEIsaUJBQWlCO1FBQ2pCLE1BQU0sS0FBSyxHQUFHLElBQUksR0FBRyxDQUFDLEtBQUssQ0FBQyxJQUFJLEVBQUUsc0JBQXNCLEVBQUU7WUFDeEQsaUJBQWlCLEVBQUUsR0FBRyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUMsR0FBRyxDQUFDO1lBQzVDLFNBQVMsRUFBRSw2QkFBNkI7WUFDeEMsSUFBSSxFQUFFLElBQUk7WUFDVix5QkFBeUIsRUFBRSxJQUFJLEVBQUUsZ0JBQWdCO1NBQ2xELENBQUMsQ0FBQztRQUdILFlBQVk7UUFDWixNQUFNLE1BQU0sR0FBRyxJQUFJLEVBQUUsQ0FBQyxNQUFNLENBQUMsSUFBSSxFQUFFLHVCQUF1QixFQUFFO1lBQzFELFVBQVUsRUFBRSx5QkFBeUI7WUFDckMsYUFBYSxFQUFFLEdBQUcsQ0FBQyxhQUFhLENBQUMsT0FBTztTQUN6QyxDQUFDLENBQUM7UUFFSCxzQkFBc0I7UUFDdEIsTUFBTSxtQkFBbUIsR0FBRyxJQUFJLEdBQUcsQ0FBQyxJQUFJLENBQUMsSUFBSSxFQUFFLDhCQUE4QixFQUFFO1lBQzdFLFNBQVMsRUFBRSxJQUFJLEdBQUcsQ0FBQyxnQkFBZ0IsQ0FBQyxzQkFBc0IsQ0FB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UyxFQUFFLHdCQUF3QjtTQUNwQyxDQUFDLENBQUM7SUFFTCxDQUFDO0NBQ0Y7QUFuR0QsMERBbUdDIiwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcbmltcG9ydCB7IENvbnN0cnVjdCB9IGZyb20gJ2NvbnN0cnVjdHMnO1xuaW1wb3J0ICogYXMgc3FzIGZyb20gJ2F3cy1jZGstbGliL2F3cy1zcXMnO1xuaW1wb3J0ICogYXMgbGFtYmRhIGZyb20gJ2F3cy1jZGstbGliL2F3cy1sYW1iZGEnO1xuaW1wb3J0ICogYXMgczMgZnJvbSAnYXdzLWNkay1saWIvYXdzLXMzJztcbmltcG9ydCAqIGFzIGxhbWJkYUV2ZW50U291cmNlcyBmcm9tICdhd3MtY2RrLWxpYi9hd3MtbGFtYmRhLWV2ZW50LXNvdXJjZXMnO1xuaW1wb3J0ICogYXMgczNOb3RpZmljYXRpb25zIGZyb20gJ2F3cy1jZGstbGliL2F3cy1zMy1ub3RpZmljYXRpb25zJztcbmltcG9ydCAqIGFzIHNucyBmcm9tICdhd3MtY2RrLWxpYi9hd3Mtc25zJztcbmltcG9ydCAqIGFzIHN1YnNjcmlwdGlvbnMgZnJvbSAnYXdzLWNkay1saWIvYXdzLXNucy1zdWJzY3JpcHRpb25zJztcbmltcG9ydCAqIGFzIGlhbSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtaWFtJztcbi8qKlxuICogXG7lr7zlhaXmiYDpnIDnmoQgQVdTIENESyDlupNcbuWIm+W7uiBTUVMg6Zif5YiXXG7liJvlu7ogTGFtYmRhIOWHveaVsCzlubbmt7vliqDkuIDkuKogUHl0aG9uIOWxglxu5Yib5bu6IFMzIOWtmOWCqOahtlxu5Li6IExhbWJkYSDlh73mlbDmt7vliqAgU1FTIOS6i+S7tua6kOaYoOWwhFxu5Yib5bu6IFNOUyDkuLvpophcbuS4uiBMYW1iZGEg5Ye95pWw5re75YqgIFMzIOS6i+S7tumAmuefpVxu5Li6IExhbWJkYSDlh73mlbDmt7vliqAgU05TIOS4u+mimOiuoumYhVxu5Li6IFNRUyDpmJ/liJfmt7vliqDmrbvkv6HpmJ/liJdcbiAqL1xuZXhwb3J0IGNsYXNzIENka1NlcnZpY2VTY3JlZW5lclN0YWNrIGV4dGVuZHMgY2RrLlN0YWNrIHtcbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBjZGsuU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgLy8g5Yib5bu6IEZJRk8gU1FTIOmYn+WIl1xuICAgIGNvbnN0IHF1ZXVlID0gbmV3IHNxcy5RdWV1ZSh0aGlzLCAnU2VydmljZVNjcmVlbmVyUXVldWUnLCB7XG4gICAgICB2aXNpYmlsaXR5VGltZW91dDogY2RrLkR1cmF0aW9uLnNlY29uZHMoMzAwKSxcbiAgICAgIHF1ZXVlTmFtZTogJ3NlcnZpY2Utc2NyZWVuZXItcXVldWUuZmlmbycsXG4gICAgICBmaWZvOiB0cnVlLCAvLyDorr7nva7kuLogRklGTyDpmJ/liJdcbiAgICAgIGNvbnRlbnRCYXNlZERlZHVwbGljYXRpb246IHRydWUsIC8vIOWQr+eUqOWfuuS6juWGheWuueeahOmHjeWkjeaVsOaNruWIoOmZpFxuICAgIH0pO1xuXG5cbiAgICAvLyDliJvlu7ogUzMg5a2Y5YKo5qG2XG4gICAgY29uc3QgYnVja2V0ID0gbmV3IHMzLkJ1Y2tldCh0aGlzLCAnU2VydmljZVNjcmVlbmVyQnVja2V0Jywge1xuICAgICAgYnVja2V0TmFtZTogJ3NlcnZpY2Utc2NyZWVuZXItYnVja2V0JyxcbiAgICAgIHJlbW92YWxQb2xpY3k6IGNkay5SZW1vdmFsUG9saWN5LkRFU1RST1ksXG4gICAgfSk7XG5cbiAgICAvLyDliJvlu7ogTGFtYmRhIOaJp+ihjOinkuiJsuW5tumZhOWKoOetlueVpVxuICAgIGNvbnN0IGxhbWJkYUV4ZWN1dGlvblJvbGUgPSBuZXcgaWFtLlJvbGUodGhpcywgJ1NjcmVlbm5lckxhbWJkYUV4ZWN1dGlvblJvbGUnLCB7XG4gICAgICBhc3N1bWVkQnk6IG5ldyBpYW0uU2VydmljZVByaW5jaXBhbCgnbGFtYmRhLmFtYXpvbmF3cy5jb20nKSwgLy8gTGFtYmRhIOacjeWKoeeahOi6q+S7veagh+ivhlxuICAgIH0pO1xuXG4gICAgLy8g5Li6IExhbWJkYSDmiafooYzop5LoibLmt7vliqDnrZbnlaVcbiAgICBsYW1iZGFFeGVjdXRpb25Sb2xlLmFkZFRvUG9saWN5KG5ldyBpYW0uUG9saWN5U3RhdGVtZW50KHtcbiAgICAgIGFjdGlvbnM6IFsnbG9nczpDcmVhdGVMb2dHcm91cCcsICdsb2dzOkNyZWF0ZUxvZ1N0cmVhbScsICdsb2dzOlB1dExvZ0V2ZW50cycsICdjbG91ZHdhdGNoOionXSxcbiAgICAgIHJlc291cmNlczogWycqJ10sIC8vIOWFgeiuuCBMYW1iZGEg5YaZ5YWlIENsb3VkV2F0Y2ggTG9nc1xuICAgIH0pKTtcblxuICAgIC8vIOS4uiBMYW1iZGEg5omn6KGM6KeS6Imy5re75YqgIHN0czpBc3N1bWVSb2xlIOadg+mZkO+8jOWFgeiuuOWIh+aNouinkuiJslxuICAgIGxhbWJkYUV4ZWN1dGlvblJvbGUuYWRkVG9Qb2xpY3kobmV3IGlhbS5Qb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgYWN0aW9uczogWydzdHM6QXNzdW1lUm9sZSddLFxuICAgICAgcmVzb3VyY2VzOiBbJyonXSwgLy8g5YWB6K645omu5ryU5Lu75L2V6KeS6ImyXG4gICAgfSkpO1xuXG4gICAgLy8g5Li6IExhbWJkYSDmiafooYzop5LoibLmt7vliqDmiYDmnIkgU05TIOadg+mZkFxuICAgIGxhbWJkYUV4ZWN1dGlvblJvbGUuYWRkVG9Qb2xpY3kobmV3IGlhbS5Qb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgYWN0aW9uczogW1xuICAgICAgICAnc25zOkxpc3RUb3BpY3MnLFxuICAgICAgICAnc25zOkdldFRvcGljQXR0cmlidXRlcycsXG4gICAgICAgICdzbnM6TGlzdFN1YnNjcmlwdGlvbnNCeVRvcGljJyxcbiAgICAgICAgJ3NuczpQdWJsaXNoJyxcbiAgICAgICAgJ3NuczpSZWNlaXZlJ1xuICAgICAgXSxcbiAgICAgIHJlc291cmNlczogWycqJ10sIC8vIOi/memHjOi1hOa6kOWPr+S7peagueaNruS9oOeahOWunumZhemcgOaxgui/m+ihjOmZkOWItlxuICAgIH0pKTtcbiAgICAvLyDlkK/liqhsYW1iZGEgaW5zaWdodFxuICAgIGxhbWJkYUV4ZWN1dGlvblJvbGUuYWRkTWFuYWdlZFBvbGljeShcbiAgICAgIGlhbS5NYW5hZ2VkUG9saWN5LmZyb21Bd3NNYW5hZ2VkUG9saWN5TmFtZSgnQ2xvdWRXYXRjaExhbWJkYUluc2lnaHRzRXhlY3V0aW9uUm9sZVBvbGljeScpXG4gICAgKTtcbiAgICAvLyDkuLogTGFtYmRhIOaJp+ihjOinkuiJsua3u+WKoOS4iuS8oCBTMyDmnYPpmZBcbiAgICBsYW1iZGFFeGVjdXRpb25Sb2xlLmFkZFRvUG9saWN5KG5ldyBpYW0uUG9saWN5U3RhdGVtZW50KHtcbiAgICAgIGFjdGlvbnM6IFtcbiAgICAgICAgJ3MzOlB1dE9iamVjdCcsXG4gICAgICAgICdzMzpHZXRPYmplY3QnLFxuICAgICAgICAnczM6TGlzdEJ1Y2tldCdcbiAgICAgIF0sXG4gICAgICByZXNvdXJjZXM6IFtcbiAgICAgICAgYCR7YnVja2V0LmJ1Y2tldEFybn0vKmAsIC8vIOWFgeiuuCBMYW1iZGEg5LiK5Lyg5ZKM6I635Y+W5a+56LGhXG4gICAgICAgIGJ1Y2tldC5idWNrZXRBcm4gLy8g5YWB6K64IExhbWJkYSDliJflh7rlrZjlgqjmobblhoXlrrlcbiAgICAgIF0sXG4gICAgfSkpO1xuXG4gICAgXG4gICAgLy8g5Yib5bu6IExhbWJkYSDlsYJcbiAgICAvLyDkvb/nlKguL3BhY2thZ2VfbGFtYmRhX2xheWVyLnNo6ISa5pys5p2l55Sf5oiQ5L6d6LWW5bGC55qE5YyFXG4gICAgY29uc3Qgc2NyZWVuZXJEZXBzTGF5ZXIgPSBuZXcgbGFtYmRhLkxheWVyVmVyc2lvbih0aGlzLCAnU2NyZWVuZXJEZXBzTGF5ZXInLCB7XG4gICAgICBjb2RlOiBsYW1iZGEuQ29kZS5mcm9tQXNzZXQoJy4vbGFtYmRhLWNvZGUvbGF5ZXItZGVwcycpLCAvLyDmm7/mjaLkuLrmgqjnmoTkvp3otZbpobnnm67lvZXot6/lvoRcbiAgICAgIGNvbXBhdGlibGVSdW50aW1lczogW2xhbWJkYS5SdW50aW1lLlBZVEhPTl8zXzEwXSwgLy8g5oyH5a6a5YW85a6555qEIFB5dGhvbiDov5DooYzml7bniYjmnKxcbiAgICAgIGRlc2NyaXB0aW9uOiAnU2NyZWVuZXIgUHl0aG9uIGRlcGVuZGVuY2llcyBsYXllcidcbiAgICB9KTtcblxuICAgIC8vIOWIm+W7uiBQeXRob24gTGFtYmRhIOWHveaVsFxuICAgIGNvbnN0IHNjcmVlbmVyTGFtYmRhID0gbmV3IGxhbWJkYS5GdW5jdGlvbih0aGlzLCAnU2NyZWVuZXJMYW1iZGEnLCB7XG4gICAgICBydW50aW1lOiBsYW1iZGEuUnVudGltZS5QWVRIT05fM18xMCxcbiAgICAgIGhhbmRsZXI6ICdpbmRleC5oYW5kbGVyJywgICAgICAgICAvLyDmjIflrpogTGFtYmRhIOWkhOeQhueoi+W6j+eahOWFpeWPo+WHveaVsFxuICAgICAgY29kZTogbGFtYmRhLkNvZGUuZnJvbUFzc2V0KCdsYW1iZGFfY29kZS9zZXJ2aWNlLXNjcmVlbmVyLXYyJyksXG4gICAgICByb2xlOiBsYW1iZGFFeGVjdXRpb25Sb2xlLCAgICAgICAgLy8g5YWz6IGUIExhbWJkYSDmiafooYzop5LoibJcbiAgICAgIG1lbW9yeVNpemU6IDI1NiwgICAgICAgICAgICAgICAgICAvLyDlhoXlrZgyNTZNXG4gICAgICB0aW1lb3V0OiBjZGsuRHVyYXRpb24ubWludXRlcygzKSwgLy8g6K6+572u6LaF5pe25pe26Ze05Li6IDMg5YiG6ZKfXG4gICAgICBlbnZpcm9ubWVudDoge1xuICAgICAgICBCVUNLRVRfTkFNRTogYnVja2V0LmJ1Y2tldE5hbWUsXG4gICAgICAgIExPR19MRVZFTDogJ0lORk8nXG4gICAgICB9LFxuICAgICAgbGF5ZXJzOiBbc2NyZWVuZXJEZXBzTGF5ZXJdICAgICAgICAgLy8g5re75Yqg5L6d6LWW6aG55bGCXG4gICAgfSk7XG5cblxuICAgIC8vIOS4uiBMYW1iZGEg5Ye95pWw5re75YqgIFNRUyDkuovku7bmupDmmKDlsIRcbiAgICBjb25zdCBldmVudFNvdXJjZSA9IG5ldyBsYW1iZGFFdmVudFNvdXJjZXMuU3FzRXZlbnRTb3VyY2UocXVldWUpO1xuICAgIHNjcmVlbmVyTGFtYmRhLmFkZEV2ZW50U291cmNlKGV2ZW50U291cmNlKTtcblxuICAgIC8vIOWIm+W7uiBTTlMg5Li76aKYXG4gICAgY29uc3QgdG9waWMgPSBuZXcgc25zLlRvcGljKHRoaXMsICdTZXJ2aWNlU2NyZWVuZXJUb3BpYycsIHtcbiAgICAgIHRvcGljTmFtZTogJ3NlcnZpY2Utc2NyZWVuZXItdG9waWMnLFxuICAgIH0pO1xuXG4gIH1cbn1cbiJdfQ==