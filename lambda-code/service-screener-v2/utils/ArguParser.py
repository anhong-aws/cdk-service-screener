import argparse

class ArguParser:
    OPTLISTS = {
        "r": "regions",
        "s": "services",
        "l": "log",
        "d": "debug",
        "t": "test",
        "p": "profile",
        "b": "bucketName",
        "m": "mode",
        "f": "filters"
    }

    CLI_ARGUMENT_RULES = {
        "regions": {
            "required": False, 
            # "errmsg": "Please key in --region, example: --region ap-southeast-1",
            "default": None,
            "help": "--regions ap-southeast-1,ap-southeast-2"
        },
        "services": {
            "required": False,
            "emptymsg": "Missing --services, using default value: $defaultValue",
            "default": "rds,ec2,iam,s3,efs,lambda,guardduty,cloudfront,cloudtrail,elasticache,eks,dynamodb,opensearch,kms,cloudwatch,redshift,apigateway",
            "help": "--services ec2,iam"
        },
        "debug": {
            "required": False,
            "default": False,
            "help": "--debug True|False"
        },
        "log": {
            "required": False,
            "default": None
        },
        ## Removing Feedback
        # "feedback": {
        #     "required": False,
        #    "default": False
        # },
        ## Conflict params
        #"dev": {
        #    "required": False,
        #    "default": False
        #},
        "ztestmode": {
            "required": False,
            "default": False
        },
        "mode": {
            "required": False,
            "default": "report",
            "help": "--mode report|api|api_full"
        },
        "profile": {
            "required": False,
            "default": False
        },
        "tags": {
            "required": False,
            "default": False
        },
        "frameworks": {
            "required": False,
            "default": 'MSR,FTR,SSB,WAFS,CIS'
        },
        "others":{
            "required": False,
            "default": None,
            "help": "reserved for future development"
        },
        "bucketName":{
            "required": False,
            "default": None,
            "help": "for upload to s3"
        },
        'crossAccounts':{
            "required": False,
            "default": False,
            "help": "Screener to run multiple accounts"
        },
        'workerCounts':{
            "required": False,
            "default": 4,
            "help": "Number of parallel threads, recommend 4 for Cloudshell"
        }
    }

    @staticmethod
    def Load():
        parser = argparse.ArgumentParser(prog='Screener', description='Service-Screener, open-source to check your AWS environment against AWS Well-Architected Pillars')

        for k, v in ArguParser.CLI_ARGUMENT_RULES.items():
            parser.add_argument('-' + k[:1], '--' + k, required=v['required'], default=v['default'], help=v.get('help', None))

        args = vars(parser.parse_args())

        return args

    @staticmethod
    def parse_params(params):
        for key, rule in ArguParser.CLI_ARGUMENT_RULES.items():
            value = params.get(key, rule.get('default'))
            if value is None and rule.get('required', True):
                raise ValueError(f"Missing required parameter: {key}")
            params[key] = value
        return params

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Screener', description='Service-Screener, open-source to check your AWS environment against AWS Well-Architected Pillars')

    for k, v in ArguParser.CLI_ARGUMENT_RULES.items():
        parser.add_argument('-' + k[:1], '--' + k, required=v['required'], default=v['default'], help=v.get('help', None))

    args = parser.parse_args()
    print(args.regions)

    params = {
        "regions": "us-east-1",
        "crossAccounts": False,
        "includeCurrentAccount": False,
        "crossAccountsInfo": {
            "general": {
                "IncludeThisAccount": True,
                "RoleName": "OrganizationAccountAccessRole",
                "ExternalId": ""
            },
            "accountLists": {
                "722350150383": {}
            }
        }
    }
    ArguParser.parse_params(params)
    print(params)
