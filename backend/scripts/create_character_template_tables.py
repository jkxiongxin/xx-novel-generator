#!/usr/bin/env python3
"""
创建角色模板相关的数据库表
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os

# 添加父目录到路径，以便导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.core.database import Base
from app.models import (
    CharacterTemplateDetail, UsageExample, 
    CharacterTemplateFavorite, CharacterTemplateUsage
)

def create_character_template_tables():
    """创建角色模板相关的数据库表"""
    
    settings = get_settings()
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("开始创建角色模板相关的数据库表...")
    
    try:
        # 确保已经导入了所有模型
        print("已导入的模型:")
        print(f"- CharacterTemplateDetail: {CharacterTemplateDetail.__tablename__}")
        print(f"- UsageExample: {UsageExample.__tablename__}")
        print(f"- CharacterTemplateFavorite: {CharacterTemplateFavorite.__tablename__}")
        print(f"- CharacterTemplateUsage: {CharacterTemplateUsage.__tablename__}")
        
        # 创建所有表（只创建不存在的表）
        Base.metadata.create_all(bind=engine)
        
        # 验证表是否创建成功
        with engine.connect() as connection:
            # 检查每个表是否存在
            tables_to_check = [
                'character_template_details',
                'character_usage_examples', 
                'character_template_favorites',
                'character_template_usages'
            ]
            
            print("\n验证表创建结果:")
            for table_name in tables_to_check:
                try:
                    result = connection.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
                    if result.fetchone():
                        print(f"✓ 表 {table_name} 创建成功")
                    else:
                        print(f"✗ 表 {table_name} 创建失败")
                except Exception as e:
                    print(f"✗ 检查表 {table_name} 时出错: {e}")
        
        print("\n角色模板表创建完成！")
        
    except Exception as e:
        print(f"创建表时出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("角色模板数据库表创建脚本")
    print("=" * 50)
    
    success = create_character_template_tables()
    
    if success:
        print("\n✓ 所有操作完成！现在可以正常使用角色模板功能。")
    else:
        print("\n✗ 操作失败！请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()