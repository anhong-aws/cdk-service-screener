from ddb_dao import DdbDao

class DdbScreenerLogItems(DdbDao):
    def __init__(self):
        super().__init__('screener-log-items')
    
    def read_item_by_status(self):
        response = self.query_items_by_attribute('status', 'enable')
        return response
    
# 测试代码
if __name__ == "__main__":
    # 创建一个 DdbScreenerLogItems 实例
    screener_log = DdbScreenerLogItems()

