#!/usr/bin/env python3
"""
更新世界观相关数据表
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.models.worldview import Worldview, WorldMap, CultivationSystem, History, Faction
from app.models.user import User
from app.models.novel import Novel

def update_worldview_tables():
    """更新世界观相关数据表"""
    
    print("开始更新世界观数据表...")
    
    try:
        # 创建所有表（如果不存在）
        Base.metadata.create_all(bind=engine)
        print("✓ 数据表创建/更新成功")
        
        # 检查表是否存在并显示结构
        with engine.connect() as conn:
            # 检查世界观主表
            result = conn.execute(text("PRAGMA table_info(worldviews)"))
            columns = result.fetchall()
            if columns:
                print("\n✓ worldviews 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            
            # 检查世界地图表
            result = conn.execute(text("PRAGMA table_info(world_maps)"))
            columns = result.fetchall()
            if columns:
                print("\n✓ world_maps 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            
            # 检查修炼体系表
            result = conn.execute(text("PRAGMA table_info(cultivation_systems)"))
            columns = result.fetchall()
            if columns:
                print("\n✓ cultivation_systems 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            
            # 检查历史事件表
            result = conn.execute(text("PRAGMA table_info(histories)"))
            columns = result.fetchall()
            if columns:
                print("\n✓ histories 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            
            # 检查阵营势力表
            result = conn.execute(text("PRAGMA table_info(factions)"))
            columns = result.fetchall()
            if columns:
                print("\n✓ factions 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
        
        print("\n所有世界观相关表更新完成！")
        return True
        
    except Exception as e:
        print(f"✗ 更新表结构失败: {e}")
        return False

def add_missing_columns():
    """添加缺失的列（如果需要）"""
    
    print("\n检查并添加缺失的列...")
    
    try:
        with engine.connect() as conn:
            # 为world_maps表添加新字段（如果不存在）
            try:
                conn.execute(text("ALTER TABLE world_maps ADD COLUMN climate VARCHAR(200)"))
                print("✓ 添加 world_maps.climate 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE world_maps ADD COLUMN terrain VARCHAR(200)"))
                print("✓ 添加 world_maps.terrain 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE world_maps ADD COLUMN resources TEXT"))
                print("✓ 添加 world_maps.resources 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE world_maps ADD COLUMN population VARCHAR(100)"))
                print("✓ 添加 world_maps.population 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE world_maps ADD COLUMN culture TEXT"))
                print("✓ 添加 world_maps.culture 字段")
            except:
                pass
            
            # 为cultivation_systems表添加新字段
            try:
                conn.execute(text("ALTER TABLE cultivation_systems ADD COLUMN cultivation_method TEXT"))
                print("✓ 添加 cultivation_systems.cultivation_method 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE cultivation_systems ADD COLUMN required_resources TEXT"))
                print("✓ 添加 cultivation_systems.required_resources 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE cultivation_systems ADD COLUMN breakthrough_condition TEXT"))
                print("✓ 添加 cultivation_systems.breakthrough_condition 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE cultivation_systems ADD COLUMN power_description TEXT"))
                print("✓ 添加 cultivation_systems.power_description 字段")
            except:
                pass
            
            # 为histories表添加新字段
            try:
                conn.execute(text("ALTER TABLE histories ADD COLUMN participants TEXT"))
                print("✓ 添加 histories.participants 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE histories ADD COLUMN consequences TEXT"))
                print("✓ 添加 histories.consequences 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE histories ADD COLUMN related_locations TEXT"))
                print("✓ 添加 histories.related_locations 字段")
            except:
                pass
            
            # 为factions表添加新字段
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN leader VARCHAR(100)"))
                print("✓ 添加 factions.leader 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN territory TEXT"))
                print("✓ 添加 factions.territory 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN power_level VARCHAR(50)"))
                print("✓ 添加 factions.power_level 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN ideology TEXT"))
                print("✓ 添加 factions.ideology 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN allies JSON"))
                print("✓ 添加 factions.allies 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN enemies JSON"))
                print("✓ 添加 factions.enemies 字段")
            except:
                pass
            
            try:
                conn.execute(text("ALTER TABLE factions ADD COLUMN member_count VARCHAR(50)"))
                print("✓ 添加 factions.member_count 字段")
            except:
                pass
            
            conn.commit()
        
        print("✓ 列添加检查完成")
        return True
        
    except Exception as e:
        print(f"✗ 添加列失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("世界观数据表更新脚本")
    print("=" * 50)
    
    # 更新表结构
    if not update_worldview_tables():
        sys.exit(1)
    
    # 添加缺失的列
    if not add_missing_columns():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("世界观数据表更新完成!")
    print("=" * 50)

if __name__ == "__main__":
    main()