"""
提示词管理服务
Author: AI Writer Team
Created: 2025-06-01
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.prompt import Prompt, PromptType
from app.schemas.prompt import PromptCreate, PromptUpdate

logger = logging.getLogger(__name__)


class PromptService:
    """提示词管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_prompt(self, prompt_data: PromptCreate) -> Prompt:
        """创建提示词模板"""
        try:
            prompt = Prompt(**prompt_data.dict())
            self.db.add(prompt)
            self.db.commit()
            self.db.refresh(prompt)
            logger.info(f"创建提示词模板成功: {prompt.name}")
            return prompt
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建提示词模板失败: {str(e)}")
            raise
    
    async def get_prompt_by_id(self, prompt_id: int) -> Optional[Prompt]:
        """根据ID获取提示词模板"""
        return self.db.query(Prompt).filter(Prompt.id == prompt_id).first()
    
    async def get_prompts_by_type(
        self, 
        prompt_type: PromptType, 
        active_only: bool = True
    ) -> List[Prompt]:
        """根据类型获取提示词模板列表"""
        query = self.db.query(Prompt).filter(Prompt.type == prompt_type)
        
        if active_only:
            query = query.filter(Prompt.is_active == True)
        
        return query.order_by(Prompt.created_at.desc()).all()
    
    async def get_default_prompt_by_type(self, prompt_type: PromptType) -> Optional[Prompt]:
        """获取指定类型的默认提示词模板"""
        return self.db.query(Prompt).filter(
            and_(
                Prompt.type == prompt_type,
                Prompt.is_active == True
            )
        ).order_by(Prompt.created_at.desc()).first()
    
    async def update_prompt(
        self, 
        prompt_id: int, 
        prompt_data: PromptUpdate
    ) -> Optional[Prompt]:
        """更新提示词模板"""
        try:
            prompt = await self.get_prompt_by_id(prompt_id)
            if not prompt:
                return None
            
            update_data = prompt_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(prompt, field, value)
            
            self.db.commit()
            self.db.refresh(prompt)
            logger.info(f"更新提示词模板成功: {prompt.name}")
            return prompt
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新提示词模板失败: {str(e)}")
            raise
    
    async def delete_prompt(self, prompt_id: int) -> bool:
        """删除提示词模板"""
        try:
            prompt = await self.get_prompt_by_id(prompt_id)
            if not prompt:
                return False
            
            self.db.delete(prompt)
            self.db.commit()
            logger.info(f"删除提示词模板成功: {prompt.name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除提示词模板失败: {str(e)}")
            raise
    
    async def get_all_prompts(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> List[Prompt]:
        """获取所有提示词模板"""
        query = self.db.query(Prompt)
        
        if active_only:
            query = query.filter(Prompt.is_active == True)
        
        return query.offset(skip).limit(limit).order_by(Prompt.created_at.desc()).all()
    
    async def build_prompt(
        self,
        prompt_type: PromptType,
        context_data: Dict[str, Any],
        user_input: Optional[str] = None
    ) -> str:
        """构建完整的提示词"""
        try:
            # 获取提示词模板
            prompt_template = await self.get_default_prompt_by_type(prompt_type)
            if not prompt_template:
                raise ValueError(f"未找到类型为 {prompt_type} 的提示词模板")
            
            # 构建上下文变量
            template_vars = {
                "user_input": user_input or "",
                **context_data
            }
            
            # 替换模板中的变量
            final_prompt = prompt_template.template.format(**template_vars)
            
            logger.info(f"构建提示词成功: {prompt_type}")
            return final_prompt
            
        except Exception as e:
            logger.error(f"构建提示词失败: {str(e)}")
            raise
    
    async def init_default_prompts(self):
        """初始化默认提示词模板"""
        try:
            # 检查是否已有提示词模板
            existing_prompts = self.db.query(Prompt).all()
            if len(existing_prompts) > 0:
                logger.info("提示词模板已存在，跳过初始化")
                return
            
            # 创建默认提示词模板
            default_prompts = self._get_default_prompt_templates()
            
            for prompt_data in default_prompts:
                prompt = Prompt(**prompt_data)
                self.db.add(prompt)
            
            self.db.commit()
            logger.info(f"初始化默认提示词模板成功，共创建 {len(default_prompts)} 个模板")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"初始化默认提示词模板失败: {str(e)}")
            raise
    
    def _get_default_prompt_templates(self) -> List[Dict[str, Any]]:
        """获取默认提示词模板配置"""
        return [
            {
                "name": "默认世界观生成器",
                "type": PromptType.WORLD_VIEW,
                "template": """请根据以下要求生成一个完整、合理、有特色的世界观体系。

生成要求：
- 小说类型：{genre}
- 小说主题：{themes}
- 写作风格：{style}
- 用户需求：{user_input}

请生成一个包含以下要素的完整世界观体系，并按JSON格式返回：

{
  "world_base": {
    "name": "世界名称",
    "description": "基本世界观描述",
    "background": "历史背景和基础设定",
    "rules": ["核心规则1", "核心规则2", "..."],
    "characteristics": ["世界特色1", "世界特色2", "..."]
  },
  "geography": {
    "map_regions": [
      {
        "name": "区域名称",
        "type": "区域类型(大陆/海域/空域等)",
        "description": "区域描述",
        "features": ["地理特征1", "地理特征2", "..."],
        "resources": ["特色资源1", "特色资源2", "..."]
      }
    ],
    "special_locations": [
      {
        "name": "特殊地点名称",
        "description": "地点描述",
        "significance": "地点重要性",
        "mysteries": ["相关谜团1", "相关谜团2", "..."]
      }
    ]
  },
  "power_system": {
    "name": "修炼/力量体系名称",
    "description": "体系整体描述",
    "levels": [
      {
        "name": "等级名称",
        "description": "等级描述",
        "requirements": "晋升要求",
        "abilities": ["能力1", "能力2", "..."]
      }
    ],
    "unique_features": ["特色1", "特色2", "..."],
    "cultivation_methods": ["修炼方法1", "修炼方法2", "..."]
  },
  "history": {
    "eras": [
      {
        "name": "时代名称",
        "description": "时代概述",
        "major_events": [
          {
            "name": "事件名称",
            "description": "事件描述",
            "impact": "历史影响",
            "key_figures": ["重要人物1", "重要人物2", "..."]
          }
        ]
      }
    ],
    "significant_artifacts": [
      {
        "name": "神器/遗物名称",
        "description": "描述",
        "powers": ["能力1", "能力2", "..."],
        "history": "来历"
      }
    ]
  },
  "factions": [
    {
      "name": "势力名称",
      "type": "势力类型",
      "description": "势力描述",
      "ideology": "理念和目标",
      "strength": "势力实力",
      "territory": "势力范围",
      "relationships": [
        {
          "faction": "相关势力名称",
          "type": "关系类型(同盟/敌对/竞争等)",
          "description": "关系描述"
        }
      ]
    }
  ]
}""",
                "description": "用于生成完整世界观体系的默认模板",
                "response_format": '''
{
  "world_base": {
    "name": "string",
    "description": "string",
    "background": "string",
    "rules": ["string"],
    "characteristics": ["string"]
  },
  "geography": {
    "map_regions": [{
      "name": "string",
      "type": "string",
      "description": "string",
      "features": ["string"],
      "resources": ["string"]
    }],
    "special_locations": [{
      "name": "string",
      "description": "string",
      "significance": "string",
      "mysteries": ["string"]
    }]
  },
  "power_system": {
    "name": "string",
    "description": "string",
    "levels": [{
      "name": "string",
      "description": "string",
      "requirements": "string",
      "abilities": ["string"]
    }],
    "unique_features": ["string"],
    "cultivation_methods": ["string"]
  },
  "history": {
    "eras": [{
      "name": "string",
      "description": "string",
      "major_events": [{
        "name": "string",
        "description": "string",
        "impact": "string",
        "key_figures": ["string"]
      }]
    }],
    "significant_artifacts": [{
      "name": "string",
      "description": "string",
      "powers": ["string"],
      "history": "string"
    }]
  },
  "factions": [{
    "name": "string",
    "type": "string",
    "description": "string",
    "ideology": "string",
    "strength": "string",
    "territory": "string",
    "relationships": [{
      "faction": "string",
      "type": "string",
      "description": "string"
    }]
  }]
}''',
                "default_max_tokens": 30000,
                "default_temperature": 75
            },
            {
                "name": "默认小说名生成器",
                "type": PromptType.NOVEL_NAME,
                "template": """请为小说生成5个有吸引力的标题。

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
                "description": "用于生成小说标题的默认模板",
                "response_format": '{"titles": [{"title": "string", "reason": "string"}]}',
                "default_max_tokens": 30000,
                "default_temperature": 80
            },
            {
                "name": "默认小说创意生成器",
                "type": PromptType.NOVEL_IDEA,
                "template": """请生成一个完整的小说创意。

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
                "description": "用于生成小说创意的默认模板",
                "response_format": '{"idea": {"title": "string", "setting": "string", "main_character": "string", "conflict": "string", "plot": "string", "unique_selling_point": "string", "target_audience": "string"}}',
                "default_max_tokens": 30000,
                "default_temperature": 85
            },
            {
                "name": "默认脑洞生成器",
                "type": PromptType.BRAIN_STORM,
                "template": """请发挥创意，基于给定要素生成有趣的脑洞创意。

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
                "description": "用于生成创意脑洞的默认模板",
                "response_format": '{"brainstorms": [{"style": "string", "concept": "string", "implementation": "string", "development": "string"}]}',
                "default_max_tokens": 30000,
                "default_temperature": 90
            }
        ]


def get_prompt_service(db: Session) -> PromptService:
    """获取提示词服务实例"""
    return PromptService(db)