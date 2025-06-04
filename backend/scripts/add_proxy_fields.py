"""
添加代理配置字段到AI模型配置表
Author: AI Writer Team
Created: 2025-06-03
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from sqlalchemy import text
from app.core.database import get_db, engine

def add_proxy_fields():
    """添加代理配置字段"""
    print("开始添加代理配置字段...")
    
    try:
        with engine.connect() as connection:
            # 检查字段是否已存在
            result = connection.execute(text("PRAGMA table_info(ai_model_configs)"))
            columns = [row[1] for row in result.fetchall()]
            
            # 添加代理相关字段
            if 'proxy_enabled' not in columns:
                connection.execute(text(
                    "ALTER TABLE ai_model_configs ADD COLUMN proxy_enabled BOOLEAN DEFAULT FALSE"
                ))
                print("✓ 添加 proxy_enabled 字段")
            
            if 'proxy_url' not in columns:
                connection.execute(text(
                    "ALTER TABLE ai_model_configs ADD COLUMN proxy_url VARCHAR(500)"
                ))
                print("✓ 添加 proxy_url 字段")
            
            if 'proxy_username' not in columns:
                connection.execute(text(
                    "ALTER TABLE ai_model_configs ADD COLUMN proxy_username VARCHAR(200)"
                ))
                print("✓ 添加 proxy_username 字段")
            
            if 'proxy_password' not in columns:
                connection.execute(text(
                    "ALTER TABLE ai_model_configs ADD COLUMN proxy_password VARCHAR(200)"
                ))
                print("✓ 添加 proxy_password 字段")
            
            connection.commit()
            print("代理配置字段添加完成!")
            
    except Exception as e:
        print(f"添加代理配置字段失败: {str(e)}")
        raise

if __name__ == "__main__":
    add_proxy_fields()