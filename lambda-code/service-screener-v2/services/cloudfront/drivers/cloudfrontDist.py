import urllib.parse
from datetime import date

from utils.Config import Config
from services.Evaluator import Evaluator

class cloudfrontDist(Evaluator):
    def __init__(self, dist, cloudfrontClient):
        super().__init__()
        self.dist = dist
        self.cloudfrontClient = cloudfrontClient
        self._configPrefix = 'cloudfront::distribution::'
        
        self.distConfig = cloudfrontClient.get_distribution_config(Id=dist)
        
        self.init()
        
    def _checkAccessLogsEnabled(self):
        dist = self.dist
        resp = self.distConfig
        logging = str(resp['DistributionConfig']['Logging']['Enabled'])
        if logging == 'False':
            self.results['accessLogging'] = [-1, '']
            
    def _checkWAFAssociation(self):
        dist = self.dist
        resp = self.distConfig
        webACL = resp['DistributionConfig']['WebACLId']
        if webACL == '':
            self.results['WAFAssociation'] = [-1, '']
            
    def _checkDefaultRootObject(self):
        dist = self.dist
        resp = self.distConfig
        rootObj = resp['DistributionConfig']['DefaultRootObject']
        if rootObj == '':
            self.results['defaultRootObject'] = [-1, '']
            
    def _checkCompressedObjects(self):
        dist = self.dist
        resp = self.distConfig
        compress = resp['DistributionConfig']['DefaultCacheBehavior']['Compress']
        if compress == False:
            self.results['compressObjectsAutomatically'] = [-1, '']
            
    def _checkDeprecatedSSL(self):
        dist = self.dist
        resp = self.distConfig
        
        for y in resp['DistributionConfig']['Origins']['Items']:
            if not 'CustomOriginConfig' in y:
                continue
            
            if y['CustomOriginConfig']['OriginProtocolPolicy'] == 'http-only':
                continue
            
            if 'SSLv3' in y['CustomOriginConfig']['OriginSslProtocols']['Items']:
                self.results['DeprecatedSSLProtocol'] = [-1, '']
                break
    
    def _checkOriginFailover(self):
        dist = self.dist
        resp = self.distConfig
        origin = resp['DistributionConfig']['OriginGroups']['Quantity']
        if origin < 1:
            self.results['originFailover'] = [-1, '']
            
    def _checkFieldLevelEncryption(self):
        dist = self.dist
        resp = self.distConfig
        encryption = resp['DistributionConfig']['DefaultCacheBehavior']['FieldLevelEncryptionId']
        if encryption == '':
            self.results['fieldLevelEncryption'] = [-1, '']
            
    def _checkViewerPolicyHttps(self):
        dist = self.dist
        resp = self.distConfig
        policy = resp['DistributionConfig']['DefaultCacheBehavior']['ViewerProtocolPolicy']
        if policy == 'allow-all':
            self.results['viewerPolicyHttps'] = [-1, '']
    
    
    
if __name__ == "__main__":
    ssBoto = Config.get('ssBoto')
    c = ssBoto.client('cloudfront')
    o = cloudfrontDist('ok', c)