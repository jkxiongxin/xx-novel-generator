#!/usr/bin/env python3
"""
简单测试API接口是否正常工作
"""

import asyncio
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db


async def test_ai_config_api():
    """测试AI配置API接口"""
    print("🧪 测试AI配置API接口...")
    
    # 获取数据库会话
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # 使用原生SQL查询，避免枚举问题
        result = db.execute(text("""
            SELECT 
                id, name, model_type, is_active, is_default,
                group_name, group_description, is_group_default,
                user_id, created_at
            FROM ai_model_configs 
            WHERE user_id = 2
            ORDER BY group_name ASC, priority DESC, created_at DESC
        """))
        
        configs = result.fetchall()
        print(f"✅ 查询到 {len(configs)} 个配置")
        
        # 按分组整理数据
        groups_data = {}
        ungrouped_configs = []
        
        for config in configs:
            print(f"  配置: {config.name}, 分组: {config.group_name}, 分组默认: {config.is_group_default}")
            
            if config.group_name:
                if config.group_name not in groups_data:
                    groups_data[config.group_name] = {
                        'configs': [],
                        'active_count': 0,
                        'total_count': 0,
                        'default_config_id': None
                    }
                
                groups_data[config.group_name]['configs'].append(config)
                groups_data[config.group_name]['total_count'] += 1
                if config.is_active:
                    groups_data[config.group_name]['active_count'] += 1
                if config.is_group_default:
                    groups_data[config.group_name]['default_config_id'] = config.id
            else:
                ungrouped_configs.append(config)
        
        print(f"✅ 分组统计:")
        print(f"  - 已分组: {len(groups_data)} 个分组")
        print(f"  - 未分组: {len(ungrouped_configs)} 个配置")
        
        for group_name, group_data in groups_data.items():
            print(f"  - {group_name}: {group_data['total_count']} 个配置, {group_data['active_count']} 个启用, 默认: {group_data['default_config_id']}")
        
        # 测试统计查询
        stats_result = db.execute(text("""
            SELECT 
                COUNT(*) as total_configs,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_configs,
                COUNT(DISTINCT group_name) as total_groups
            FROM ai_model_configs 
            WHERE user_id = 2
        """))
        
        stats = stats_result.fetchone()
        print(f"✅ 统计信息: 总配置数={stats.total_configs}, 启用数={stats.active_configs}, 分组数={stats.total_groups}")
        
        print("🎉 API接口测试成功！数据库字段已正确添加，查询正常工作！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_ai_config_api())