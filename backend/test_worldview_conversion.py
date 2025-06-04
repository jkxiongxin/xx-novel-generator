#!/usr/bin/env python3
"""
世界观数据转换测试
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.worldview_converter import WorldviewConverter

def test_conversion():
    """测试数据转换功能"""
    
    # 加载测试数据
    with open("worldview.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取JSON部分
    import re
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        json_str = match.group(1)
        test_data = json.loads(json_str)
        
        try:
            # 测试转换
            result = WorldviewConverter.convert_ai_response(
                test_data, user_id=1, novel_id=1
            )
            
            print("✅ 数据转换成功")
            print(f"转换结果包含 {len(result)} 个顶级字段")
            
            # 验证必要字段
            required_fields = ["worldview", "world_maps", "cultivation_system", "factions"]
            for field in required_fields:
                if field in result:
                    print(f"✅ {field} 字段存在")
                else:
                    print(f"❌ {field} 字段缺失")
            
            return True
            
        except Exception as e:
            print(f"❌ 转换失败: {str(e)}")
            return False
    else:
        print("❌ 无法提取JSON数据")
        return False

if __name__ == "__main__":
    test_conversion()