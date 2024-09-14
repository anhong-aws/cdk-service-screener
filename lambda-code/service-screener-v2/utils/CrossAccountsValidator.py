import os
import json
import boto3
import time
import botocore
from botocore.config import Config as bConfig

from utils.Config import Config
from utils.Tools import _warn, _info
import constants as _C

class CrossAccountsValidator():
    DEFAULT_ROLENAME = 'ServiceScreenerAutomationRole'
    DEFAULT_ROLESESSIONNAME = 'ServiceScreenerCrossAcct'    #For CloudTrail tracking purpose, does not impact any logic
    DEFAULT_DURATIONSECONDS = 3600
    ROLEARN_PREFIX = 'arn:aws:iam::{accountId}:role/{roleName}'

    ## Remove sample in future
    CONFIGJSON = _C.ROOT_DIR + '/crossAccounts.json'
    ROLEINFO = {}

    VALIDATED = False
    IncludeThisAccount = True
    MAXTOKENCHECKRETRY = 5
    WAIT_TOKENCHECKRETRY = 3

    def __init__(self):
        iam = boto3.client('iam', region_name = 'us-east-1')
        self.iamClient = iam

    def setIamGlobalEndpointTokenVersion(self):
        resp = self.iamClient.get_account_summary()
        SummaryMap = resp.get('SummaryMap')
        token = 1
        if 'GlobalEndpointTokenVersion' in SummaryMap:
            token = SummaryMap['GlobalEndpointTokenVersion']

        self.GlobalEndpointTokenVersion = token
        if self.GlobalEndpointTokenVersion == 1:
            print('Detected GlobalEndpointTokenVersion=1, changing to 2...')
            self.iamClient.set_security_token_service_preferences(
                GlobalEndpointTokenVersion='v2Token'
            )
            time.sleep(5)

    def runValidation(self, data = None):
        fileValidation = self.readConfig(data)

        if fileValidation == True:
            roleValidation = self.validateRoles()

        if fileValidation == True and roleValidation == True:
            self.VALIDATED = True
        else:
            print('Cross Account Roles failed')

    def isValidated(self):
        return self.VALIDATED

    def getCred(self):
        return self.ROLEINFO

    def resetIamGlobalEndpointTokenVersion(self):
        if self.GlobalEndpointTokenVersion == 1:
            print('Cross Accounts Validation completed. Resetting GlobalEndpointTokenVersion=1')
            self.iamClient.set_security_token_service_preferences(
                GlobalEndpointTokenVersion='v1Token'    
            )

    def validateRoles(self):
        canProceedFlag = True

        generalDicts = self.crossAccountsDict['general']

        for acct, cfg in self.crossAccountsDict['accountLists'].items():
            params = {**generalDicts, **cfg}
            res = {k: v for k, v in params.items() if v}

            res['RoleSessionName'] = self.DEFAULT_ROLESESSIONNAME    
            res['RoleArn'] = self.getRoleArn(acct, None if not 'RoleName' in res else res['RoleName'])
            res['DurationSeconds'] = self.DEFAULT_DURATIONSECONDS
            res.pop('RoleName')


            sts = boto3.client('sts')

            tokenCheckPass = False
            tokenCheckCounter = 1
            try:
                while(tokenCheckPass == False and tokenCheckCounter <= self.MAXTOKENCHECKRETRY):
                    resp = sts.assume_role(**res)
                    cred = resp.get('Credentials')
                    if len(cred['SessionToken']) < 700:
                        print('Attempt #{}. Waiting IAM GlobalEndpointTokenVersion to reflect V2 token, retry in {} seconds'.format(tokenCheckCounter, self.WAIT_TOKENCHECKRETRY))
                        tokenCheckCounter = tokenCheckCounter + 1
                        time.sleep(self.WAIT_TOKENCHECKRETRY)
                    else:
                        tokenCheckPass = True

                if tokenCheckPass == False:
                    print('... unable to acquired V2 token ...')
                    canProceedFlag = False
                    break

                if 'AccessKeyId' in cred and 'SecretAccessKey' in cred and 'SessionToken' in cred:
                    print('[\u2714] {}, assume_role passed'.format(acct))

                    self.ROLEINFO[acct] = {
                        'aws_access_key_id': cred['AccessKeyId'],
                        'aws_secret_access_key': cred['SecretAccessKey'],
                        'aws_session_token': cred['SessionToken']
                    }

            except botocore.exceptions.ClientError as err:
                canProceedFlag = False
                _warn("Unable to assume role, read more below")
                print('AcctId: {}'.format(acct), str(err))
                print(res)

                break

        return canProceedFlag

    def getRoleArn(self, acctId, roleName):
        if roleName == None:
            roleName = self.DEFAULT_ROLENAME

        return self.ROLEARN_PREFIX.format(accountId=acctId, roleName=roleName)

    def checkIfIncludeThisAccount(self):
        return self.IncludeThisAccount

    def readConfig(self, data = None):
        if os.path.exists(self.CONFIGJSON) == False:
            _warn('{} is not found, multiple accounts scan halted'.format(self.CONFIGJSON))
            return False

        generalErrMsg = "Unable to process {}, encounters error: {}"
        try:
            if data == None:
            f = open(self.CONFIGJSON)
            data = json.load(f)
            f.close()

            self.IncludeThisAccount = True
            if 'general' in data and 'IncludeThisAccount' in data['general']:
                self.IncludeThisAccount = data['general']['IncludeThisAccount']
                del data['general']['IncludeThisAccount']

            self.crossAccountsDict = data
            if 'general' not in self.crossAccountsDict:
                _warn( generalErrMsg.format(self.CONFIGJSON, 'Missing <general> key') )
                return False
            if 'accountLists' not in self.crossAccountsDict:
                _warn( generalErrMsg.format(self.CONFIGJSON, 'Missing <accountLists> key') )
                return False

            return True
        except json.decoder.JSONDecodeError as err:
            _warn( generalErrMsg.format(self.CONFIGJSON, str(err)) )
            return False
        except Exception as err:
            _warn( generalErrMsg.format(self.CONFIGJSON, str(err)) )
            return False
