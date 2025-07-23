class PerformanceStats:
    """收集和计算touchAutoClick方法的性能数据"""
    
    def __init__(self):
        self.interval1_data = []  # 存储所有interval1的值
        self.interval2_data = []  # 存储所有interval2的值
        self.interval3_data = []  # 存储所有interval3的值
        self.interval4_data = []  # 存储所有interval4的值
        
    def add_sample(self, interval1, interval2, interval3, interval4):
        """添加一组新的时间间隔数据"""
        if interval1 > 0:
            self.interval1_data.append(interval1)
        if interval2 > 0:
            self.interval2_data.append(interval2)
        if interval3 > 0:
            self.interval3_data.append(interval3)
        if interval4 > 0:
            self.interval4_data.append(interval4)
        
    def get_averages(self):
        """计算并返回所有时间间隔的平均值"""
        count = len(self.interval1_data)
        if count == 0:
            return {
                "interval1_avg": 0,
                "interval2_avg": 0,
                "interval3_avg": 0,
                "interval4_avg": 0,
                "sample_count": 0
            }
        
        v1, v2, v3, v4 = 0,0,0,0
        if len(self.interval1_data) > 0:
            v1 = sum(self.interval1_data) / len(self.interval1_data)
        if len(self.interval2_data) > 0:
            v2 = sum(self.interval2_data) / len(self.interval2_data)
        if len(self.interval3_data) > 0:
            v3 = sum(self.interval3_data) / len(self.interval3_data)
        if len(self.interval4_data) > 0:
            v4 = sum(self.interval4_data) / len(self.interval4_data)

        return {
            "interval1_avg": v1,
            "interval2_avg": v2,
            "interval3_avg": v3,
            "interval4_avg": v4,
            "sample_count": count
        }

    def printStats(self):
        stats = self.get_averages()
        print(f"[    总调用次数: {stats['sample_count']}interval1 平均耗时: {stats['interval1_avg']:.2f} 毫秒interval2 平均耗时: {stats['interval2_avg']:.2f} 毫秒interval3 平均耗时: {stats['interval3_avg']:.2f} 毫秒interval4 平均耗时: {stats['interval4_avg']:.2f} 毫秒")


    def clear(self):
        """清空所有收集的数据"""
        self.interval1_data = []
        self.interval2_data = []
        self.interval3_data = []
        self.interval4_data = []