#!/usr/bin/env python3
"""
测试AI配置接口修复情况
"""

import asyncio
import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ai_model_config import AIModelConfig
from app.models.user import User


async def test_ai_config_groups():
    """测试AI配置分组功能"""
    print("🧪 测试AI配置分组功能...")
    
    # 获取数据库会话
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # 查找用户
        user = db.query(User).filter(User.id == 2).first()
        if not user:
            print("❌ 用户不存在")
            return
        
        print(f"✅ 找到用户: {user.username}")
        
        # 测试查询分组配置
        configs = db.query(AIModelConfig).filter(
            AIModelConfig.user_id == user.id
        ).order_by(
            AIModelConfig.group_name.asc(),
            AIModelConfig.priority.desc(),
            AIModelConfig.created_at.desc()
        ).all()
        
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
                        'default_config_id': None
                    }
                
                groups_data[config.group_name]['configs'].append(config)
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
            print(f"  - {group_name}: {len(group_data['configs'])} 个配置, {group_data['active_count']} 个启用, 默认: {group_data['default_config_id']}")
        
        print("🎉 分组功能测试成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_ai_config_groups())