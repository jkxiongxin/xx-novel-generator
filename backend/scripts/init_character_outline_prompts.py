#!/usr/bin/env python3
"""
初始化角色和大纲生成提示词模板
Author: AI Writer Team
Created: 2025-06-01
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.prompt import PromptType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_character_outline_prompts():
    """初始化角色和大纲生成提示词模板"""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 直接使用SQL查询，避免关系映射问题
        existing_character = db.execute(text("SELECT COUNT(*) FROM prompts WHERE type = :type"),
                                       {"type": PromptType.CHARACTER.value}).scalar()
        existing_rough = db.execute(text("SELECT COUNT(*) FROM prompts WHERE type = :type"),
                                   {"type": PromptType.ROUGH_OUTLINE.value}).scalar()
        existing_detail = db.execute(text("SELECT COUNT(*) FROM prompts WHERE type = :type"),
                                    {"type": PromptType.DETAIL_OUTLINE.value}).scalar()
        
        prompts_to_create = []
        
        # 角色生成提示词模板
        if existing_character == 0:
            character_prompt = {
                "name": "默认角色生成器",
                "type": PromptType.CHARACTER,
                "template": """请为小说生成{character_count}个角色。

生成要求：
- 小说标题：{novel_title}
- 小说类型：{novel_genre}
- 世界观信息：{worldview_info}
- 角色类型要求：{character_types}
- 用户建议：{user_suggestion}

每个角色需要包含：
1. 角色名（符合世界观设定）
2. 性别（男/女/未知）
3. 性格描述（详细的性格特点）
4. 角色类型（主角/重要配角/配角）
5. 所属阵营（如有）
6. 角色标签（3-5个关键词）
7. 角色描述（外貌、背景、经历等）
8. 特殊能力（如有力量体系）

请确保角色：
- 符合小说的世界观设定
- 性格鲜明，有独特特点
- 适合在故事中发挥作用
- 与其他角色形成互补或冲突

请按照以下JSON格式返回：
{{
  "characters": [
    {{
      "name": "角色名",
      "gender": "male/female/unknown",
      "personality": "性格描述",
      "character_type": "protagonist/major_supporting/supporting",
      "faction": "所属阵营",
      "tags": ["标签1", "标签2", "标签3"],
      "description": "角色详细描述",
      "abilities": "特殊能力描述"
    }}
  ]
}}""",
                "description": "用于生成小说角色的默认模板",
                "response_format": '{"characters": [{"name": "string", "gender": "string", "personality": "string", "character_type": "string", "faction": "string", "tags": ["string"], "description": "string", "abilities": "string"}]}',
                "default_max_tokens": 30000,
                "default_temperature": 80
            }
            prompts_to_create.append(character_prompt)
            
        # 粗略大纲生成提示词模板
        if existing_rough == 0:
            rough_outline_prompt = {
                "name": "默认粗略大纲生成器",
                "type": PromptType.ROUGH_OUTLINE,
                "template": """请为小说生成粗略大纲。

小说信息：
- 标题：{novel_title}
- 类型：{novel_genre}
- 世界观：{worldview_info}
- 主要角色：{character_info}
- 目标章节数：{target_chapters}
- 用户建议：{user_suggestion}

请生成以下类型的粗略大纲：
1. 故事线（整体故事发展脉络）
2. 角色成长路线（主要角色的发展轨迹）
3. 重大事件（关键转折点和高潮）
4. 大情节点（主要剧情节点）

每个大纲点需要包含：
- 标题（简洁明了）
- 内容描述（详细说明）
- 章节范围（大概涉及的章节）
- 重要程度（高/中/低）

请确保大纲：
- 逻辑清晰，前后连贯
- 节奏合理，张弛有度
- 角色发展有层次
- 符合小说类型特点

请按照以下JSON格式返回：
{{
  "rough_outlines": [
    {{
      "outline_type": "storyline/character_growth/major_events/plot_points",
      "title": "大纲标题",
      "content": "详细内容描述",
      "start_chapter": 开始章节号,
      "end_chapter": 结束章节号,
      "importance": "high/medium/low"
    }}
  ]
}}""",
                "description": "用于生成粗略大纲的默认模板",
                "response_format": '{"rough_outlines": [{"outline_type": "string", "title": "string", "content": "string", "start_chapter": "number", "end_chapter": "number", "importance": "string"}]}',
                "default_max_tokens": 30000,
                "default_temperature": 75
            }
            prompts_to_create.append(rough_outline_prompt)
            
        # 详细大纲生成提示词模板
        if existing_detail == 0:
            detail_outline_prompt = {
                "name": "默认详细大纲生成器",
                "type": PromptType.DETAIL_OUTLINE,
                "template": """请为小说生成详细章节大纲。

小说信息：
- 标题：{novel_title}
- 类型：{novel_genre}
- 世界观：{worldview_info}
- 粗略大纲：{rough_outline_info}
- 角色信息：{character_info}
- 章节范围：第{start_chapter}章到第{end_chapter}章
- 用户建议：{user_suggestion}

请为每个章节生成详细大纲，包含：
1. 章节标题（吸引人的标题）
2. 情节点（本章的核心情节和事件）
3. 参与角色（本章出现的主要角色）
4. 入场角色（本章新出现的角色）
5. 离场角色（本章退出的角色）
6. 章节简介（本章内容概要）
7. 剧情标记（是否剧情结束/新剧情开始）

请确保章节大纲：
- 每章内容饱满但不冗长
- 角色出场合理，有逻辑性
- 情节推进自然流畅
- 与粗略大纲保持一致

请按照以下JSON格式返回：
{{
  "detailed_outlines": [
    {{
      "chapter_number": 章节号,
      "chapter_title": "章节标题",
      "plot_points": "详细情节点描述",
      "participating_characters": [角色ID列表],
      "entering_characters": [入场角色ID列表],
      "exiting_characters": [离场角色ID列表],
      "chapter_summary": "章节简介",
      "is_plot_end": false,
      "is_new_plot": false,
      "new_plot_summary": "新剧情简介"
    }}
  ]
}}""",
                "description": "用于生成详细章节大纲的默认模板",
                "response_format": '{"detailed_outlines": [{"chapter_number": "number", "chapter_title": "string", "plot_points": "string", "participating_characters": ["number"], "entering_characters": ["number"], "exiting_characters": ["number"], "chapter_summary": "string", "is_plot_end": "boolean", "is_new_plot": "boolean", "new_plot_summary": "string"}]}',
                "default_max_tokens": 30000,
                "default_temperature": 75
            }
            prompts_to_create.append(detail_outline_prompt)
        
        # 创建提示词模板
        created_count = 0
        for prompt_data in prompts_to_create:
            # 使用SQL插入，避免ORM关系问题
            sql = text("""
                INSERT INTO prompts (name, type, template, description, response_format,
                                   default_max_tokens, default_temperature, is_active, version, created_at, updated_at)
                VALUES (:name, :type, :template, :description, :response_format,
                        :default_max_tokens, :default_temperature, :is_active, :version, datetime('now'), datetime('now'))
            """)
            db.execute(sql, {
                "name": prompt_data["name"],
                "type": prompt_data["type"].value,
                "template": prompt_data["template"],
                "description": prompt_data["description"],
                "response_format": prompt_data["response_format"],
                "default_max_tokens": prompt_data["default_max_tokens"],
                "default_temperature": prompt_data["default_temperature"],
                "is_active": True,
                "version": "1.0"
            })
            created_count += 1
            logger.info(f"创建提示词模板: {prompt_data['name']}")
        
        db.commit()
        
        if created_count > 0:
            logger.info(f"成功初始化 {created_count} 个角色和大纲生成提示词模板")
        else:
            logger.info("角色和大纲提示词模板已存在，跳过初始化")
            
    except Exception as e:
        db.rollback()
        logger.error(f"初始化提示词模板失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_character_outline_prompts()