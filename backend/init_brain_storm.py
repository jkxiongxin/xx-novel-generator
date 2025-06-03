"""
初始化脑洞生成器数据库
Author: AI Writer Team
Created: 2025-06-03
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.migrations.add_brain_storm_tables import upgrade


def main():
    """主函数"""
    try:
        print("开始初始化脑洞生成器数据库...")
        upgrade()
        print("脑洞生成器数据库初始化完成!")
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()