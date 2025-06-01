#!/usr/bin/env python3
"""
初始化章节生成提示词模板
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


def init_chapter_prompts():
    """初始化章节生成提示词模板"""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已存在章节生成提示词
        existing_chapter = db.execute(text("SELECT COUNT(*) FROM prompts WHERE type = :type"),
                                     {"type": PromptType.CHAPTER.value}).scalar()
        
        prompts_to_create = []
        
        # 章节生成提示词模板
        if existing_chapter == 0:
            chapter_prompt = {
                "name": "默认章节内容生成器",
                "type": PromptType.CHAPTER,
                "template": """请为小说《{novel_title}》生成第{chapter_number}章的内容。

小说基本信息：
- 标题：{novel_title}
- 类型：{novel_genre}
- 简介：{novel_description}

章节要求：
- 章节序号：第{chapter_number}章
- 目标字数：{target_word_count}字左右
- 用户建议：{user_suggestion}

上下文信息：
{worldview_info}

{character_info}

{outline_info}

{previous_chapters}

写作要求：
1. 保持与前文的连贯性和风格一致性
2. 根据大纲推进情节发展，确保章节内容符合整体故事走向
3. 角色行为和对话要符合其性格设定和背景
4. 融入世界观设定，确保场景描述和背景设定的一致性
5. 控制章节节奏，平衡叙述、对话、动作和心理描写
6. 为下一章埋下伏笔或制造悬念

章节类型分析：
- 如果是第1章：注重世界观介绍、主角出场、故事背景建立
- 如果是发展章节：注重情节推进、角色成长、矛盾冲突
- 如果是高潮章节：注重紧张感营造、冲突爆发、情感起伏
- 如果是结尾章节：注重情节收束、角色命运、情感升华

请生成完整的章节内容，包含章节标题。

请按照以下JSON格式返回：
{{
  "title": "第{chapter_number}章 章节标题",
  "content": "完整的章节内容，包含段落分隔...",
  "word_count": 实际字数,
  "chapter_summary": "本章内容简介",
  "key_events": ["本章关键事件1", "本章关键事件2"],
  "character_development": "角色发展情况",
  "plot_advancement": "情节推进情况"
}}""",
                "description": "用于生成完整章节内容的默认模板，支持多种章节类型和上下文感知",
                "response_format": '{"title": "string", "content": "string", "word_count": "number", "chapter_summary": "string", "key_events": ["string"], "character_development": "string", "plot_advancement": "string"}',
                "default_max_tokens": 4000,
                "default_temperature": 75
            }
            prompts_to_create.append(chapter_prompt)
            
            # 章节续写模板
            chapter_continuation_prompt = {
                "name": "章节续写生成器",
                "type": PromptType.CHAPTER,
                "template": """请为小说《{novel_title}》的第{chapter_number}章续写内容。

当前章节末尾内容：
{current_content_preview}

续写要求：
- 当前字数：{current_word_count}字
- 新增目标：{target_additional_words}字
- 保持文风和节奏一致
- 推进情节发展

小说信息：
- 类型：{novel_genre}
{worldview_info}
{character_info}
{outline_info}

用户建议：{user_suggestion}

续写指导：
1. 分析前文内容，理解当前情节走向
2. 保持角色性格和行为的一致性
3. 自然地推进情节，避免突兀转折
4. 维持适当的叙述节奏
5. 为后续章节留下合理的发展空间

请直接生成续写内容，不要重复已有内容：""",
                "description": "用于为现有章节续写内容的专用模板",
                "response_format": '{"content": "string", "word_count": "number"}',
                "default_max_tokens": 3000,
                "default_temperature": 70
            }
            prompts_to_create.append(chapter_continuation_prompt)
            
            # 章节重写模板
            chapter_rewrite_prompt = {
                "name": "章节重写生成器", 
                "type": PromptType.CHAPTER,
                "template": """请重写小说《{novel_title}》的第{chapter_number}章。

原始章节内容：
{original_content}

重写要求：
- 原版字数：{original_word_count}字
- 目标字数：{target_word_count}字
- 重写建议：{rewrite_suggestions}
- 用户建议：{user_suggestion}

小说信息：
- 类型：{novel_genre}
{worldview_info}
{character_info}
{outline_info}

重写指导：
1. 保持核心情节不变，优化表达方式
2. 提升文笔质量和可读性
3. 加强人物刻画和情感表达
4. 优化对话的自然性和代入感
5. 增强场景描写的画面感
6. 完善细节描述和氛围营造
7. 确保与整体故事的一致性

请生成重写后的完整章节内容：

{{
  "title": "章节标题",
  "content": "重写后的完整内容",
  "word_count": 实际字数,
  "improvements": ["改进点1", "改进点2"],
  "rewrite_summary": "重写要点总结"
}}""",
                "description": "用于重写和优化现有章节内容的专用模板",
                "response_format": '{"title": "string", "content": "string", "word_count": "number", "improvements": ["string"], "rewrite_summary": "string"}',
                "default_max_tokens": 5000,
                "default_temperature": 70
            }
            prompts_to_create.append(chapter_rewrite_prompt)
            
            # 开头章节特化模板
            chapter_opening_prompt = {
                "name": "小说开头章节生成器",
                "type": PromptType.CHAPTER,
                "template": """请为小说《{novel_title}》生成第1章（开头章节）的内容。

小说基本信息：
- 标题：{novel_title}
- 类型：{novel_genre}
- 简介：{novel_description}
- 目标字数：{target_word_count}字左右

{worldview_info}

{character_info}

{outline_info}

用户建议：{user_suggestion}

开头章节特殊要求：
1. 吸引读者注意力，建立阅读兴趣
2. 介绍世界观背景和故事设定
3. 让主角出场，展示核心特质
4. 建立故事基调和文风
5. 埋下主要矛盾或冲突的种子
6. 营造合适的开篇氛围

开头写作技巧：
- 可以从关键事件开始，制造悬念
- 或从日常场景切入，逐步展开
- 要在前几段内抓住读者注意力
- 自然地融入世界观和角色介绍
- 避免大段背景说明，要寓于情节中

请生成完整的第1章内容：

{{
  "title": "第一章 章节标题",
  "content": "完整的章节内容...",
  "word_count": 实际字数,
  "opening_hook": "开头吸引点分析",
  "world_building": "世界观建立情况",
  "character_introduction": "角色介绍方式",
  "tone_setting": "故事基调建立"
}}""",
                "description": "专门用于生成小说第一章的特化模板，注重开头的吸引力和世界观建立",
                "response_format": '{"title": "string", "content": "string", "word_count": "number", "opening_hook": "string", "world_building": "string", "character_introduction": "string", "tone_setting": "string"}',
                "default_max_tokens": 4500,
                "default_temperature": 80
            }
            prompts_to_create.append(chapter_opening_prompt)
            
            # 高潮章节特化模板
            chapter_climax_prompt = {
                "name": "高潮章节生成器",
                "type": PromptType.CHAPTER,
                "template": """请为小说《{novel_title}》生成高潮章节（第{chapter_number}章）的内容。

小说基本信息：
- 标题：{novel_title}
- 类型：{novel_genre}
- 目标字数：{target_word_count}字左右

{worldview_info}

{character_info}

{outline_info}

{previous_chapters}

用户建议：{user_suggestion}

高潮章节特殊要求：
1. 将主要矛盾推向顶点
2. 角色面临最大的挑战或选择
3. 情感冲突达到最高潮
4. 展现角色的成长和变化
5. 为故事结局做好铺垫
6. 保持紧张感和节奏感

高潮写作技巧：
- 加快叙述节奏，增强紧迫感
- 突出角色的内心挣扎和决断
- 运用环境描写烘托气氛
- 对话要简洁有力，富有冲击力
- 动作描写要精确生动
- 留下合适的悬念或转折

请生成完整的高潮章节内容：

{{
  "title": "第{chapter_number}章 章节标题",
  "content": "完整的章节内容...",
  "word_count": 实际字数,
  "climax_peak": "高潮点分析",
  "tension_build": "紧张感营造",
  "character_crisis": "角色危机处理",
  "emotional_impact": "情感冲击力"
}}""",
                "description": "专门用于生成故事高潮章节的特化模板，注重冲突和紧张感的营造",
                "response_format": '{"title": "string", "content": "string", "word_count": "number", "climax_peak": "string", "tension_build": "string", "character_crisis": "string", "emotional_impact": "string"}',
                "default_max_tokens": 4500,
                "default_temperature": 75
            }
            prompts_to_create.append(chapter_climax_prompt)
        
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
            logger.info(f"成功初始化 {created_count} 个章节生成提示词模板")
        else:
            logger.info("章节生成提示词模板已存在，跳过初始化")
            
    except Exception as e:
        db.rollback()
        logger.error(f"初始化章节提示词模板失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_chapter_prompts()