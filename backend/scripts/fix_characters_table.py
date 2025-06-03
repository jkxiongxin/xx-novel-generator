#!/usr/bin/env python3
"""
修复characters表结构，添加缺失的列
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os

# 添加父目录到路径，以便导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

def fix_characters_table():
    """修复characters表结构"""
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("=" * 60)
    print("修复characters表结构")
    print("=" * 60)
    
    try:
        with engine.connect() as connection:
            # 检查from_template_id列是否存在
            print("1. 检查characters表结构...")
            result = connection.execute(text("PRAGMA table_info(characters)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"   当前列: {', '.join(columns)}")
            
            if 'from_template_id' not in columns:
                print("\n2. 添加from_template_id列...")
                try:
                    connection.execute(text("""
                        ALTER TABLE characters 
                        ADD COLUMN from_template_id INTEGER
                    """))
                    print("   ✓ from_template_id列添加成功")
                except Exception as e:
                    print(f"   ✗ 添加from_template_id列失败: {e}")
                    return False
            else:
                print("   ✓ from_template_id列已存在")
            
            # 提交更改
            connection.commit()
            
            # 验证修复结果
            print("\n3. 验证修复结果...")
            result = connection.execute(text("PRAGMA table_info(characters)"))
            columns_after = [row[1] for row in result.fetchall()]
            
            print(f"   修复后的列: {', '.join(columns_after)}")
            
            if 'from_template_id' in columns_after:
                print("   ✓ characters表结构修复成功")
                return True
            else:
                print("   ✗ characters表结构修复失败")
                return False
                
    except Exception as e:
        print(f"\n✗ 修复过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("Characters表结构修复脚本")
    
    success = fix_characters_table()
    
    if success:
        print("\n✓ Characters表结构修复完成！")
        print("现在可以正常使用角色模板功能。")
    else:
        print("\n✗ Characters表结构修复失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()