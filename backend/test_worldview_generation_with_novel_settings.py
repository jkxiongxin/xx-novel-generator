#!/usr/bin/env python3
"""
测试世界观生成包含小说设定信息的功能
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.generation_service import get_generation_service
from app.services.prompt_service import get_prompt_service
from app.schemas.worldview import WorldviewGenerationRequest
from app.models.novel import Novel
from app.models.user import User
import json

async def test_worldview_generation_with_novel_settings():
    """测试包含小说设定的世界观生成"""
    db = next(get_db())
    
    try:
        # 获取第一个用户和第一部小说用于测试
        user = db.query(User).first()
        novel = db.query(Novel).first()
        
        if not user or not novel:
            print("❌ 数据库中没有用户或小说数据，无法进行测试")
            return
        
        print(f"📚 使用小说进行测试:")
        print(f"  - 小说ID: {novel.id}")
        print(f"  - 标题: {novel.title}")
        print(f"  - 类型: {novel.genre}")
        print(f"  - 简介: {novel.description[:100] if novel.description else '无'}...")
        print(f"  - 作者: {novel.author}")
        print(f"  - 目标读者: {novel.target_audience}")
        print(f"  - 写作风格: {novel.writing_style}")
        print()
        
        # 创建生成请求
        request = WorldviewGenerationRequest(
            novel_id=novel.id,
            worldview_name="测试世界观",
            generation_types=["maps", "cultivation"],
            user_suggestion="希望创建一个符合小说设定的奇幻世界",
            include_novel_settings=True,
            genre="玄幻",
            themes=["修炼", "冒险"],
            style="史诗"
        )
        
        print("🔧 生成请求参数:")
        print(f"  - novel_id: {request.novel_id}")
        print(f"  - include_novel_settings: {request.include_novel_settings}")
        print(f"  - worldview_name: {request.worldview_name}")
        print(f"  - generation_types: {request.generation_types}")
        print()
        
        # 初始化服务
        prompt_service = get_prompt_service(db)
        generation_service = get_generation_service(prompt_service)
        
        # 测试获取小说设定信息
        print("🔍 测试获取小说设定信息...")
        novel_settings = await generation_service._get_novel_settings(novel.id, db)
        print("✅ 小说设定信息获取成功:")
        for key, value in novel_settings.items():
            print(f"  - {key}: {value}")
        print()
        
        # 测试提示词构建
        print("🏗️ 测试提示词构建...")
        from app.models.prompt import PromptType
        
        # 构建上下文数据（模拟generation_service中的逻辑）
        default_novel_settings = {
            "title": "未命名小说",
            "genre": "通用", 
            "author": "佚名",
            "description": "暂无描述",
            "target_audience": "大众",
            "writing_style": "第三人称",
            "target_words": "100000",
            "current_words": "0"
        }
        
        final_novel_settings = {**default_novel_settings, **novel_settings}
        
        context_data = {
            "genre": request.genre or final_novel_settings.get("genre", "通用"),
            "themes": ", ".join(request.themes) if request.themes else "奇幻, 冒险",
            "style": request.style or final_novel_settings.get("writing_style", "史诗"),
            "worldview_name": request.worldview_name or "未命名世界观",
            "generation_types": ", ".join(request.generation_types) if request.generation_types else "完整世界观",
            "user_input": request.user_suggestion or "",
            "novel_settings": final_novel_settings
        }
        
        prompt = await prompt_service.build_prompt(
            prompt_type=PromptType.WORLD_VIEW,
            context_data=context_data,
            user_input=request.user_suggestion
        )
        
        print("✅ 提示词构建成功!")
        print("📝 生成的提示词预览:")
        print("-" * 50)
        print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
        print("-" * 50)
        print()
        
        # 检查提示词是否包含小说信息
        novel_info_included = (
            novel.title in prompt and
            novel.author in prompt and
            (novel.description in prompt if novel.description else True)
        )
        
        if novel_info_included:
            print("✅ 提示词成功包含小说基本信息")
        else:
            print("❌ 提示词未正确包含小说基本信息")
        
        print()
        print("🎉 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_worldview_generation_with_novel_settings())