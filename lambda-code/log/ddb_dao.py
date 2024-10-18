import boto3
from boto3.dynamodb.conditions import Attr, Key
# from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

class DdbDao:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    # def deserialize_item(self, item):
    #     deserializer = TypeDeserializer()
    #     return {k: deserializer.deserialize(v) if isinstance(v, dict) else v for k, v in item.items()}
    def deserialize_item(self, item):
        # 递归函数来处理嵌套字典
        def deserialize(data):
            if isinstance(data, dict):
                return {key: deserialize(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [deserialize(element) for element in data]
            elif isinstance(data, Decimal):
                return int(data) if data % 1 == 0 else float(data)
            else:
                return data

        return deserialize(item)
    def create_item(self, item):
        response = self.table.put_item(Item=item)
        return response

    def read_item(self, key):
        response = self.table.get_item(Key=key)
        if 'Item' in response:
            return self.deserialize_item(response['Item'])
        else:
            return None
    
    def update_item(self, key, update_expression, expression_attribute_values, expression_attribute_names=None):
        params = {
            'Key': key,
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values
        }
        if expression_attribute_names:
            params['ExpressionAttributeNames'] = expression_attribute_names

        response = self.table.update_item(**params)
        return response

    def delete_item(self, key):
        response = self.table.delete_item(Key=key)
        return response
    def query_items_by_attribute(self, index_name, attribute_name, attribute_value):
        response = self.table.query(
            IndexName=index_name,  # 替换为你创建的索引名称
            KeyConditionExpression=Key(attribute_name).eq(attribute_value)
        )
        items = response['Items']
        return [self.deserialize_item(item) for item in items]
    

    def query_items_by_attribute(self, attribute_name, attribute_value):
        response = self.table.scan(
            FilterExpression=Attr(attribute_name).eq(attribute_value)
        )
        items = response['Items']
        return [self.deserialize_item(item) for item in items]
    

