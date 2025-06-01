#!/usr/bin/env python3
"""
简单初始化提示词模板脚本
Author: AI Writer Team
Created: 2025-06-01
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.prompt import Prompt, PromptType
from app.models.base import Base

# 创建数据库连接
DATABASE_URL = "sqlite:///./ai_writer.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_prompts():
    """初始化提示词模板"""
    print("开始初始化提示词模板...")
    
    db = SessionLocal()
    try:
        # 检查是否已有提示词
        existing = db.query(Prompt).first()
        if existing:
            print("提示词模板已存在，跳过初始化")
            return True
        
        # 创建默认提示词
        prompts = [
            Prompt(
                name="默认小说名生成器",
                type=PromptType.NOVEL_NAME,
                template="""请为小说生成5个有吸引力的标题。

生成要求：
- 类型：{genre}
- 关键词：{keywords}
- 风格：{style}
- 用户需求：{user_input}

请确保标题：
1. 吸引读者注意力
2. 体现小说的核心主题
3. 符合类型特点
4. 朗朗上口，易于记忆

请按照以下JSON格式返回：
{{
  "titles": [
    {{"title": "标题1", "reason": "推荐理由"}},
    {{"title": "标题2", "reason": "推荐理由"}},
    {{"title": "标题3", "reason": "推荐理由"}},
    {{"title": "标题4", "reason": "推荐理由"}},
    {{"title": "标题5", "reason": "推荐理由"}}
  ]
}}""",
                description="用于生成小说标题的默认模板",
                response_format='{"titles": [{"title": "string", "reason": "string"}]}',
                default_max_tokens=1000,
                default_temperature=80,
                is_active=True,
                version="1.0"
            ),
            Prompt(
                name="默认小说创意生成器",
                type=PromptType.NOVEL_IDEA,
                template="""请生成一个完整的小说创意。

生成要求：
- 类型：{genre}
- 主题：{themes}
- 篇幅：{length}
- 用户需求：{user_input}

请包含以下要素：
1. 核心设定和背景
2. 主要角色设定
3. 核心冲突
4. 故事主线
5. 独特卖点

请按照以下JSON格式返回：
{{
  "idea": {{
    "title": "建议标题",
    "setting": "世界设定和背景",
    "main_character": "主角设定",
    "conflict": "核心冲突",
    "plot": "故事主线",
    "unique_selling_point": "独特卖点",
    "target_audience": "目标读者"
  }}
}}""",
                description="用于生成小说创意的默认模板",
                response_format='{"idea": {"title": "string", "setting": "string", "main_character": "string", "conflict": "string", "plot": "string", "unique_selling_point": "string", "target_audience": "string"}}',
                default_max_tokens=1500,
                default_temperature=85,
                is_active=True,
                version="1.0"
            ),
            Prompt(
                name="默认脑洞生成器",
                type=PromptType.BRAIN_STORM,
                template="""请发挥创意，基于给定要素生成有趣的脑洞创意。

生成要求：
- 主题：{topic}
- 要素：{elements}
- 创意程度：{creativity_level}/100
- 用户想法：{user_input}

请生成3个不同风格的创意：
1. 一个偏现实的创意
2. 一个充满想象力的创意
3. 一个颠覆性的创意

每个创意要包含：
- 核心概念
- 实现方式
- 可能的发展方向

请按照以下JSON格式返回：
{{
  "brainstorms": [
    {{
      "style": "现实向",
      "concept": "核心概念",
      "implementation": "实现方式", 
      "development": "发展方向"
    }},
    {{
      "style": "想象向",
      "concept": "核心概念",
      "implementation": "实现方式",
      "development": "发展方向"
    }},
    {{
      "style": "颠覆向", 
      "concept": "核心概念",
      "implementation": "实现方式",
      "development": "发展方向"
    }}
  ]
}}""",
                description="用于生成创意脑洞的默认模板",
                response_format='{"brainstorms": [{"style": "string", "concept": "string", "implementation": "string", "development": "string"}]}',
                default_max_tokens=2000,
                default_temperature=90,
                is_active=True,
                version="1.0"
            )
        ]
        
        # 添加到数据库
        for prompt in prompts:
            db.add(prompt)
        
        db.commit()
        print(f"✅ 成功创建 {len(prompts)} 个提示词模板！")
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("=" * 50)
    print("🚀 AI智能小说创作平台 - 提示词初始化工具")
    print("=" * 50)
    
    success = init_prompts()
    
    if success:
        print("\n🎉 初始化完成！可以开始使用AI生成功能了。")
    else:
        print("\n💥 初始化失败，请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()