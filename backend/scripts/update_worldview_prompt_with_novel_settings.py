#!/usr/bin/env python3
"""
更新世界观生成提示词模板以包含小说设定信息
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.prompt import Prompt, PromptType
import json

def update_worldview_prompt():
    """更新世界观生成提示词模板"""
    db = next(get_db())
    
    # 查找现有的世界观提示词模板
    existing = db.query(Prompt).filter(Prompt.type == PromptType.WORLD_VIEW).first()
    
    # 增强的世界观生成提示词模板
    enhanced_worldview_template = """你是一个专业的世界观创造师，请根据以下信息为小说创建一个完整的世界观：

**小说基本信息：**
- 小说标题：{novel_settings[title]}
- 小说类型：{genre}
- 作者：{novel_settings[author]}
- 小说简介：{novel_settings[description]}
- 目标读者群体：{novel_settings[target_audience]}
- 写作风格：{novel_settings[writing_style]}
- 当前字数：{novel_settings[current_words]} / 目标字数：{novel_settings[target_words]}

**创作要求：**
- 主要主题：{themes}
- 创作风格：{style}
- 世界观名称：{worldview_name}
- 用户建议：{user_input}

**生成内容包括：**
{generation_types}

**创作指导原则：**
1. 世界观必须与小说的类型和主题保持高度一致
2. 考虑目标读者群体的偏好和接受度
3. 融合小说简介中提及的元素和设定
4. 确保世界观的复杂度与目标字数相匹配
5. 体现作者的写作风格特点

请基于以上信息创建一个丰富、连贯且完全符合小说设定的世界观。特别注意要让世界观为小说情节服务，增强故事的吸引力和可信度。"""

    # 响应格式保持不变
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
    
    if existing:
        # 更新现有模板
        existing.template = enhanced_worldview_template
        existing.description = "用于生成小说世界观的AI提示词模板（包含小说设定信息）"
        existing.response_format = json.dumps(response_format, ensure_ascii=False, indent=2)
        existing.version = "2.0"
        print("世界观生成提示词模板已更新")
    else:
        # 创建新模板
        prompt = Prompt(
            name="增强世界观生成器",
            type=PromptType.WORLD_VIEW,
            template=enhanced_worldview_template,
            description="用于生成小说世界观的AI提示词模板（包含小说设定信息）",
            default_max_tokens=30000,
            default_temperature=75,
            response_format=json.dumps(response_format, ensure_ascii=False, indent=2),
            is_active=True,
            version="2.0"
        )
        db.add(prompt)
        print("世界观生成提示词模板已创建")
    
    db.commit()
    print("操作完成")

if __name__ == "__main__":
    update_worldview_prompt()