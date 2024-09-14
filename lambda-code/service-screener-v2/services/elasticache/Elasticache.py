import boto3
import botocore
from packaging.version import Version

from utils.Config import Config
from utils.Tools import _pr, aws_get_latest_instance_generations
from services.Service import Service
from services.elasticache.drivers.ElasticacheMemcached import ElasticacheMemcached
from services.elasticache.drivers.ElasticacheRedis import ElasticacheRedis
from services.elasticache.drivers.ElasticacheReplicationGroup import ElasticacheReplicationGroup
from typing import Dict, List, Set


class Elasticache(Service):
    def __init__(self, region) -> None:
        super().__init__(region)
        ssBoto = self.ssBoto
        self.elasticacheClient = ssBoto.client('elasticache', config=self.bConfig)

    def getECClusterInfo(self):
        # list all Elasticahe clusters
        arr = []
        try:
            while True:
                if len(arr) == 0:
                    # init
                    resp = self.elasticacheClient.describe_cache_clusters(
                        ShowCacheNodeInfo=True)
                else:
                    # subsequent
                    resp = self.elasticacheClient.describe_cache_clusters(
                        ShowCacheNodeInfo=True, Marker=resp.get('Marker'))

                arr.extend(resp.get('CacheClusters'))

                if resp.get('Marker') is None:
                    break
        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)
            
        fArr = []    
        for i, detail in enumerate(arr):
            if detail['CacheClusterStatus'] == 'available':
                fArr.append(arr[i])

        if not self.tags:
            return fArr
            
        finalArr = []
        for i, detail in enumerate(fArr):
            tag = self.elasticacheClient.list_tags_for_resource(ResourceName=detail['ARN'])
            nTag = tag.get('TagList')
            if self.resourceHasTags(nTag):
                finalArr.append(arr[i])
                
        return finalArr    

    def getEngineVersions(self) -> Dict[str, List]:
        lookup = {}

        def get_version(engine):
            ret = self.elasticacheClient.describe_cache_engine_versions(
                Engine=engine)
            engine_versions = [engine_version.get(
                'EngineVersion') for engine_version in ret.get('CacheEngineVersions')]
            return sorted([Version(v) for v in engine_versions], reverse=True)

        try:
            for i in ['memcached', 'redis']:
                lookup[i] = get_version(i)
        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)

        return lookup

    def getAllInstanceOfferings(self) -> Dict[str, Set[str]]:
        offering = {}

        while True:
            if len(offering) == 0:
                # init
                resp = self.elasticacheClient.describe_reserved_cache_nodes_offerings()
            else:
                # subsequent
                resp = self.elasticacheClient.describe_reserved_cache_nodes_offerings(
                    Marker=resp.get('Marker'))

            for i in resp.get('ReservedCacheNodesOfferings'):
                if i.get('ProductDescription') not in offering.keys():
                    offering[i.get('ProductDescription')] = set(
                        [i.get('CacheNodeType')])
                else:
                    offering[i.get('ProductDescription')].add(
                        i.get('CacheNodeType'))

            if resp.get('Marker') is None:
                break

        return offering

    def getLatestInstanceTypes(self):
        all_instance_offerings = self.getAllInstanceOfferings()
        families = {k: set([i.split(".")[1] for i in v])
                    for (k, v) in all_instance_offerings.items()}
        return ({k: aws_get_latest_instance_generations(v) for (k, v) in families.items()})

    def getReplicationGroupInfo(self):
        results = self.elasticacheClient.describe_replication_groups()
        
        arr = results.get("ReplicationGroups")
        while results.get("Marker") is not None:
            results = self.elasticacheClient.describe_replication_groups(
                Marker=results.get("Marker")
            )
            arr = arr + results.get("ReplicationGroups")
        
        fArr = []    
        for i, detail in enumerate(arr):
            if detail['Status'] == 'available':
                fArr.append(arr[i])    
        
        if not self.tags:
            return fArr
        
        finalArr = []
        for i, detail in enumerate(fArr):
            tag = self.elasticacheClient.list_tags_for_resource(ResourceName=detail['ARN'])
            nTag = tag.get('TagList')
            if self.resourceHasTags(nTag):
                finalArr.append(arr[i])
        
        return finalArr

    ## NOT IN USED
    def getSnapshots(self):
        replicationGroupId = set()
        last_updated = {}
        try:
            while True:
                if len(replicationGroupId) == 0:
                    # init
                    resp = self.elasticacheClient.describe_snapshots()
                else:
                    # subsequent
                    resp = self.elasticacheClient.describe_snapshots(
                        Marker=resp.get('Marker'))

                for i in resp.get('Snapshots'):
                    if i['ReplicationGroupId'] not in replicationGroupId:
                        replicationGroupId.add(i['ReplicationGroupId'])
                        last_updated[i['ReplicationGroupId']
                                     ] = i['NodeSnapshots'][0]['SnapshotCreateTime']

                    for j in i['NodeSnapshots']:
                        if j['SnapshotCreateTime'] > last_updated[i['ReplicationGroupId']]:
                            last_updated[i['ReplicationGroupId']
                                         ] = j['NodeSnapshot']['SnapshotCreateTime']

                if resp.get('Marker') is None:
                    break
        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)

        return last_updated

    def advise(self):
        objs = {}
        
        repGroups = self.getReplicationGroupInfo()
        for group in repGroups:
            print(f"... (ElastiCache::ReplicationGroup) inspecting {group.get('ReplicationGroupId')}")
            obj = ElasticacheReplicationGroup(group, self.elasticacheClient)
            obj.run(self.__class__)
            objs[f"ElastiCache::{group.get('ReplicationGroupId')}"] = obj.getInfo()
        
        self.cluster_info = self.getECClusterInfo()

        # loop through EC nodes
        if len(self.cluster_info) > 0:
            # print("evaluating Elasticache Clusters")
            self.driverInfo = {}
            self.driverInfo['engine_veresions'] = self.getEngineVersions()
            self.driverInfo['latest_instances'] = self.getLatestInstanceTypes()
        else:
            return objs

        for cluster in self.cluster_info:
            if cluster.get('Engine') == 'memcached':
                obj = ElasticacheMemcached(
                    cluster, self.elasticacheClient, self.driverInfo)
            if cluster.get('Engine') == 'redis':
                obj = ElasticacheRedis(
                    cluster, self.elasticacheClient, self.driverInfo)

            if obj is not None:
                objName = cluster.get('Engine') + f"{cluster.get('ARN')}"
                print("... (ElastiCache:" + cluster.get('Engine') + ') ' + f"{cluster.get('ARN')}")
                obj.run(self.__class__)
                objs[objName] = obj.getInfo()
                del obj
            else:
                print(
                    f"Engine {cluster.get('Engine')} of Cluster {cluster.get('CacheClusterId')} is not recognised")
        return objs
    pass


# unit testing/invoke for class
if __name__ == "__main__":
    Config.init()
    o = Elasticache('us-east-1')
    # _pr(o.getAllInstanceOfferings())
    # out = o.advise()
    out = o.getReplicationGroupInfo()
    # _pr(out)
