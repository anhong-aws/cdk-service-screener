import json
from ddb_screener_log_items import DdbScreenerLogItems

def save_log(sns_message):
    print(f'sns_message: {sns_message[:30]}')
    print(f'prepare save log')
    json_obj = json.loads(sns_message)
    print(json_obj)
    screener_log = DdbScreenerLogItems()
    screener_log.create_item(json_obj)
    return json_obj


# if __name__ == '__main__':
#     json_message = save_log(sns_message)
#     print(json_message)