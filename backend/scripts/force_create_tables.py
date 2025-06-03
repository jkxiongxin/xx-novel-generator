#!/usr/bin/env python3
"""
强制创建角色模板相关的数据库表
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os

# 添加父目录到路径，以便导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

def create_tables_with_sql():
    """使用原生SQL创建表"""
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    # 手动创建表的SQL语句
    create_sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS character_template_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            detailed_description TEXT,
            background_story TEXT,
            relationships TEXT,
            strengths TEXT DEFAULT '[]',
            weaknesses TEXT DEFAULT '[]',
            motivation TEXT,
            character_arc TEXT,
            dialogue_style TEXT,
            appearance TEXT DEFAULT '{}',
            combat_style TEXT,
            equipment TEXT DEFAULT '[]',
            special_abilities TEXT DEFAULT '[]',
            usage_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            is_popular BOOLEAN DEFAULT 0,
            is_new BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
            UNIQUE (character_id)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS character_usage_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_detail_id INTEGER NOT NULL,
            novel_genre VARCHAR(100),
            usage_context TEXT,
            adaptation_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_detail_id) REFERENCES character_template_details(id) ON DELETE CASCADE
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS character_template_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            character_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS character_template_usages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            template_id INTEGER NOT NULL,
            target_id INTEGER,
            novel_id INTEGER NOT NULL,
            customizations TEXT DEFAULT '{}',
            adaptation_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (template_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES characters(id) ON DELETE SET NULL,
            FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
        )
        """
    ]
    
    try:
        with engine.connect() as connection:
            print("开始创建角色模板相关的数据库表...")
            
            for i, sql in enumerate(create_sql_statements, 1):
                table_name = ["character_template_details", "character_usage_examples", 
                             "character_template_favorites", "character_template_usages"][i-1]
                print(f"\n{i}. 创建表 {table_name}...")
                
                try:
                    connection.execute(text(sql))
                    print(f"✓ 表 {table_name} 创建成功")
                except Exception as e:
                    print(f"✗ 创建表 {table_name} 失败: {e}")
            
            # 提交事务
            connection.commit()
            
            # 验证表是否创建成功
            print("\n验证表创建结果:")
            tables_to_check = [
                'character_template_details',
                'character_usage_examples', 
                'character_template_favorites',
                'character_template_usages'
            ]
            
            for table_name in tables_to_check:
                result = connection.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
                if result.fetchone():
                    print(f"✓ 表 {table_name} 存在")
                else:
                    print(f"✗ 表 {table_name} 不存在")
        
        print("\n✓ 角色模板表创建完成！")
        return True
        
    except Exception as e:
        print(f"\n✗ 创建表时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("强制创建角色模板数据库表脚本")
    print("=" * 60)
    
    success = create_tables_with_sql()
    
    if success:
        print("\n✓ 所有操作完成！现在可以正常使用角色模板功能。")
    else:
        print("\n✗ 操作失败！请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()