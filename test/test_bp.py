import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bpc.branch_and_price import BranchAndPrice
from pcp_reader import PCPReader

def test_branch_and_price():
    """测试分支定价算法"""
    
        # 读取测试实例
    reader = PCPReader()
    graph = reader.read_pcp_file("data/Table2_random_instances/n60p5t2s3.pcp")
    print(f"成功读取图: {len(graph.vertices)}顶点, {len(graph.edges)}边, {len(graph.partitions)}分区")
        
        # 创建分支定价算法对象
    bp = BranchAndPrice(graph, time_limit=3600)
    result = bp.solve()
    return result
        
    

if __name__ == "__main__":
    test_branch_and_price()



