#!/usr/bin/env python3
"""
初始化世界观生成提示词模板
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.prompt import Prompt, PromptType
import json

def init_worldview_prompt():
    """初始化世界观生成提示词"""
    db = next(get_db())
    
    # 检查是否已存在
    existing = db.query(Prompt).filter(Prompt.type == PromptType.WORLD_VIEW).first()
    if existing:
        print("世界观生成提示词模板已存在")
        return
    
    # 世界观生成提示词模板
    worldview_template = """你是一个专业的世界观创造师，请根据以下信息为小说创建一个完整的世界观：

**创作要求：**
- 小说类型：{genre}
- 主要主题：{themes}
- 创作风格：{style}
- 世界观名称：{worldview_name}
- 用户建议：{user_input}

**生成内容包括：**
{generation_types}

请创建一个丰富、连贯且符合小说类型的世界观。"""

    # 响应格式
    response_format = {
        "world_base": {
            "name": "世界名称",
            "description": "世界总体描述",
            "background": "历史背景和基础设定",
            "rules": ["核心规则1", "核心规则2"],
            "characteristics": ["世界特色1", "世界特色2"]
        },
        "geography": {
            "map_regions": [],
            "special_locations": []
        },
        "power_system": {
            "name": "力量体系名称",
            "description": "体系描述",
            "levels": [],
            "unique_features": [],
            "cultivation_methods": []
        },
        "history": {
            "eras": [],
            "significant_artifacts": []
        },
        "factions": []
    }
    
    # 创建提示词
    prompt = Prompt(
        name="默认世界观生成器",
        type=PromptType.WORLD_VIEW,
        template=worldview_template,
        description="用于生成小说世界观的AI提示词模板",
        default_max_tokens=30000,
        default_temperature=75,
        response_format=json.dumps(response_format, ensure_ascii=False, indent=2),
        is_active=True,
        version="1.0"
    )
    
    db.add(prompt)
    db.commit()
    
    print("世界观生成提示词模板创建成功")
    print(f"模板ID: {prompt.id}")

if __name__ == "__main__":
    init_worldview_prompt()
