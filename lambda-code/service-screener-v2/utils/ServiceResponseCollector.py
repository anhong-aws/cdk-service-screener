import os
import boto3
import json
import re
import concurrent.futures

class HTMLReader:
    def __init__(self, file_path, service):
        self.file_path = file_path
        self.service = service

    def read_html(self):
        file_path = os.path.join(self.file_path, self.service + '.html')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            html_content = None  # 或者返回一个默认值
        
        if html_content is not None:
                cleaned_content = re.sub(r'\s+', '', html_content)
                # print(cleaned_content)
                if "<h3>0</h3><p>TotalFindings</p>" in cleaned_content:
                    print(f"--{self.service} 服务没有发现问题，忽略AI汇总.")
                    html_content = None
        return html_content

class AWSBedrockClient:

    # aws_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    def __init__(self):
        self.aws_ak = os.environ.get('AWS_AK')
        self.AWS_MOCK = os.environ.get('AWS_MOCK')
        self.aws_sk = os.environ.get('AWS_SK')
        self.aws_region_code = os.environ.get('AWS_REGION_CODE')
        self.aws_model_id = os.environ.get('AWS_MODEL_ID')
        if (self.aws_model_id is None):
            self.aws_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=self.aws_region_code,
            aws_access_key_id=self.aws_ak,
            aws_secret_access_key=self.aws_sk,
        )
    def is_truthy(self):
        return self.AWS_MOCK.lower() in ("true", "1", "yes")
    def invoke_model(self, prompt, system_prompt):
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0.8,
            "top_p": 0.9,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }

        request = json.dumps(native_request)
        try:
            if self.is_truthy():
                return """None"""
            else:
                response = self.client.invoke_model(modelId=self.aws_model_id, body=request)
        except (self.client.exceptions.ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.aws_model_id}'. Reason: {e}")
            return None

        body = response["body"].read()
        model_response = json.loads(body)
        response_text = model_response["content"][0]["text"]
        return response_text

class ServiceResponseCollector:
    def __init__(self, file_path, services, aiReport):
        self.file_path = file_path
        self.services = services
        self.aiReport = aiReport
        self.service_responses = {}
    def collect_responses(self):
        files_in_directory = os.listdir(self.file_path)
        filtered_folders = [folder for folder in files_in_directory if folder.isnumeric()]
        print("filtered_folders: ",filtered_folders)
        for folder in filtered_folders:
            path_to_folder = os.path.join(self.file_path, folder)
            self.service_responses = {}
            print("path_to_folder: ",path_to_folder)
            html_report = "目前没有生成AI汇总报告, 请订阅AI汇总的服务！"
            if self.aiReport:
              self.collect_responses_by_folder(path_to_folder)
              final_summary = self.get_final_summary()
              html_report = self.generate_html_report(path_to_folder, filtered_folders)
            if html_report:
                # print(html_report)
                # 将HTML写入文件
                with open(path_to_folder+'/report.html', 'w', encoding='utf-8') as file:
                    file.write(html_report)
            else:
                print("Failed to generate HTML report.")

    def collect_responses_by_folder(self, path_to_folder):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_service, path_to_folder, service) for service in self.services]

            for future in concurrent.futures.as_completed(futures):
                service, response_text = future.result()
                if response_text:
                    self.service_responses[service] = response_text

    def process_service(self, path_to_folder, service):
        html_reader = HTMLReader(path_to_folder, service)
        html_content = html_reader.read_html()
        if html_content is None:
            return service, None

        system_prompt = f"基于AWS现代化架构的六大支柱的{service}服务审计的报告，帮我做一个总结，并提供建议，按严重性或者重要性排序，使用中文回复"

        bedrock_client = AWSBedrockClient()
        response_text = bedrock_client.invoke_model(html_content, system_prompt)

        return service, response_text
    # def collect_responses_by_folder(self, path_to_folder):
    #     services = self.services
    #     for service in services:
    #         html_reader = HTMLReader(path_to_folder, service)
    #         html_content = html_reader.read_html()
    #         if html_content is None:
    #             print(f"Error: Failed to read HTML content for {service}.")
    #         else:
    #             system_prompt = f"基于AWS现代化架构的六大支柱的{service}服务审计的报告，帮我做一个总结，并提供建议，按严重性或者重要性排序，使用中文回复"

    #             bedrock_client = AWSBedrockClient()
    #             response_text = bedrock_client.invoke_model( html_content, system_prompt)

    #             if response_text:
    #                 self.service_responses[service] = response_text

    def get_combined_responses(self):
        combined_responses = '\n------------下一个服务体检总结报告---------------\n'.join(self.service_responses.values())
        return combined_responses

    def get_final_summary(self):
        combined_responses = self.get_combined_responses()

        system_prompt = "需要你在各种服务的审计报告汇总的信息里面，需要再提炼一个精华的汇总，最好是对客户最有用的部分;2.不要针对一种服务做汇总，请使用中文回复"

        bedrock_client = AWSBedrockClient()
        final_response = bedrock_client.invoke_model(combined_responses, system_prompt)

        # if final_response:
        #     self.service_responses["final"] = final_response
        return final_response

    def generate_html_report(self, path_to_folder, filtered_folders):
        html_report = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AWS服务审计AI总结报告</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
  <link rel="stylesheet" href="https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css">
  <link rel="stylesheet" href="../res/plugins/fontawesome-free/css/all.min.css">
  <link rel="stylesheet" href="../res/plugins/icheck-bootstrap/icheck-bootstrap.min.css">
  <link rel="stylesheet" href="../res/dist/css/adminlte.min.css">
  <link rel="stylesheet" href="../res/plugins/overlayScrollbars/css/OverlayScrollbars.min.css">
  <link rel="stylesheet" href="../res/plugins/select2/css/select2.min.css">
  <!-- 引入marked.js库 -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body class="hold-transition sidebar-mini layout-fixed">
<div class="wrapper">
      <!-- Navbar -->
      <nav class="main-header navbar navbar-expand navbar-white navbar-light">
        <!-- Left navbar links -->
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" data-widget="pushmenu" href="#" role="button"><i class="fas fa-bars"></i></a>
          </li>
          <li class="nav-item d-none d-sm-inline-block">
            <a href="https://github.com/anhong-aws/cdk-service-screener" target=_blank rel="noopener noreferrer" class="nav-link">Visit Github</a>
          </li>
        </ul>
    
        <!-- Right navbar links -->
        <ul class="ml-auto navbar-nav">
          <li class="nav-item d-none d-sm-inline-block">
            <span class="nav-link">Change Account ID: </span>
          </li>
          <li class="nav-item">
            <select class="form-control" id='changeAcctId'>
            """
        c=0
        for acctId in filtered_folders:
            selected=""
            if acctId in path_to_folder:
                selected="selected"
            html_report += f"""
              <option value='{acctId}' {selected}>{acctId}</option>
            """
        html_report += f"""
            </select>
          </li>
          <li class="nav-item">
            <a class="nav-link" data-widget="fullscreen" href="#" role="button">
              <i class="fas fa-expand-arrows-alt"></i>
            </a>
          </li>
        </ul>
      </nav>

  <!-- /.navbar --><!-- Main Sidebar Container -->
  <aside class="main-sidebar sidebar-dark-primary elevation-4">
   <!-- Brand Logo -->
   <a href="#" class="brand-link">
     <img src="../res/dist/img/AdminLTELogo.png" alt="AdminLTE Logo" class="brand-image img-circle elevation-3" style="opacity: .8">
     <span class="brand-text font-weight-light">Service Screener</span>
   </a>

   <!-- Sidebar -->
   <div class="sidebar">
     <!-- Sidebar user panel (optional) -->
     <div class="pb-3 mt-3 mb-3 user-panel d-flex" style="padding-bottom:0px !important">
       <div class="image">
         <img src="https://a0.awsstatic.com/libra-css/images/logos/aws_smile-header-desktop-en-white_59x35.png" class="" alt="AWS Logo">
       </div>
       <div class="info">
         <a href="#" class="d-block" style="color: #ec902e">- <strong>Open Source Project</strong></a>
       </div>
     </div>
     <!-- Sidebar Menu -->
     <nav class="mt-2">
       <ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu" data-accordion="false">
       <li class="nav-item">
       <a href="index.html" class="nav-link ">
         <i class="nav-icon fas fa-home"></i>
         <p>
           Home
         </p>
       </a>
     </li>
     <li class="nav-item">
       <a href="report.html" target="_blank" rel="noopener noreferrer" class="nav-link">
         <i class="nav-icon fas fa-magic" style="color: gold;"></i>AI Report
       </a>
     </li>
       </ul>
     </nav>
   </div>
 </aside>
        <!-- 页面内容 -->
        <div class="content-wrapper">
            <div class="content-header">
              <div class="container-fluid">
                <div class="mb-2 row">
                  <div class="col-sm-6">
                    <h1 class="m-0">AI汇总-AWS服务审计报告</h1>
                  </div>
                  <div class="col-sm-6">
                    <ol class="breadcrumb float-sm-right">
                      <li class="breadcrumb-item"><a href="#">Home</a></li>
                      <li class="breadcrumb-item active">AI Reporter</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
            <section class="content">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-body">
        """
        colors = ["dark","warning","info","pink","primary","secondary","success","danger"]
        c=0
        for service, response in self.service_responses.items():
            color = colors[c%8]
            c=c+1
            html_report += f"""
                                    <div class="service-report">
                                        <div id='Framework' class='card card-{color} '>
                                        <div class='card-header'><h3 class='card-title'>{service.upper()}</h3>
                                        <div class='card-tools'><button type='button' class='btn btn-tool' data-card-widget='collapse'><i class='fas fa-minus'></i></button></div>
                                        </div>
                                        <div class="card-body markdown-content-{service}"></div>
                                    </div>
                                    <script>
                                        var markdownContent = document.querySelectorAll('.markdown-content-{service}');
                                        markdownContent[markdownContent.length - 1].innerHTML = marked.parse(`{response}`);
                                    </script>
            """
        final_summary = self.get_final_summary()
        html_report += f"""
                                    <div class="final-summary">
                                        <div id='Framework' class='card card-warning '>
                                        <div class='card-header'><h3 class='card-title'>汇总</h3>
                                        <div class='card-tools'><button type='button' class='btn btn-tool' data-card-widget='collapse'><i class='fas fa-minus'></i></button></div>
                                        </div>
                                        <div class="card-body markdown-content-final"></div>
                                    </div>
                                    <script>
                                        var markdownContent = document.querySelectorAll('.markdown-content-final');
                                        markdownContent[markdownContent.length - 1].innerHTML = marked.parse(`{final_summary}`);
                                    </script>"""
        html_report += f"""
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
            </section>
        </div>
        <footer class='main-footer'>
            <div class='float-right d-none d-sm-inline-block'>
              <strong>Service Screener</strong>, <b>Version</b> 2.2.0 is distributed under the <strong><a target=_blank rel='noopener noreferrer' href='https://www.apache.org/licenses/LICENSE-2.0'>Apache 2.0 License</a>, powered by <a target=_blank rel='noopener noreferrer' href='https://adminlte.io'>AdminLTE.io</a></strong>
            </div>
        </footer>
    
    <script src='../res/plugins/jquery/jquery.js'></script>
    <script src='../res/plugins/bootstrap/js/bootstrap.bundle.min.js'></script>
    <script src='../res/plugins/chart.js/Chart.min.js'></script>
    <script src='../res/plugins/overlayScrollbars/js/jquery.overlayScrollbars.min.js'></script>
    <script src='../res/plugins/select2/js/select2.full.min.js'></script>
    <script src='../res/dist/js/adminlte.js'></script>
    <script src='../res/dist/js/demo.js'></script>
    
    <script src='../res/plugins/datatables/jquery.dataTables.min.js'></script>
    <script src='../res/plugins/datatables-bs4/js/dataTables.bootstrap4.min.js'></script>
    <script src='../res/plugins/datatables-responsive/js/dataTables.responsive.min.js'></script>
    <script src='../res/plugins/datatables-responsive/js/responsive.bootstrap4.min.js'></script>
    <script src='../res/plugins/datatables-buttons/js/dataTables.buttons.min.js'></script>
    <script src='../res/plugins/datatables-buttons/js/buttons.bootstrap4.min.js'></script>
    <script src='../res/plugins/datatables-buttons/js/buttons.html5.min.js'></script>
    <script src='../res/plugins/datatables-buttons/js/buttons.print.min.js'></script>
    <script src='../res/plugins/datatables-buttons/js/buttons.colVis.min.js'></script>"""
        html_report += """
    <script>$(function(){
    $('#changeAcctId').change(function(){
        var url = window.location.href
        var arr = url.split("/")
        arr[arr.length - 2] = $(this).val()
        var newLink = arr.join('/')
        window.location.href = newLink
    })
    myTab = $("#findings-table").DataTable({
          "responsive": true, "lengthChange": true, "autoWidth": false,
          "pageLength": 50,
          "buttons": ["copy", "csv", "colvis"]
        })
    ; 
    myTab = $("#findings-table").DataTable({
          "responsive": true, "lengthChange": true, "autoWidth": false,
          "pageLength": 50,
          "buttons": ["copy", "csv", "colvis"]
        })
    myTab.buttons().container().appendTo('#findings-table_wrapper .col-md-6:eq(0)');
    
    var hash = window.location.hash.slice(1);
    if (hash){
      myTab.search(decodeURI(hash)).draw()
    }
    })</script>"""
        html_report += f"""
</body>
</html>
        """

        return html_report
    
# 使用示例
if __name__ == "__main__":
    services_str = "rds,ec2,iam,s3,efs,lambda,guardduty,cloudfront,cloudtrail,elasticache,eks,dynamodb,opensearch,kms,cloudwatch,redshift,apigateway"
    # services_str = "lambda"
    services = services_str.split(',')
    file_path = '/Users/jarrywen/Downloads/aws/learn/jupyter/bedrock/aws'
    service_response_collector = ServiceResponseCollector(file_path,services,True)
    service_response_collector.collect_responses()

    
    # if final_summary:
    #     print(final_summary)