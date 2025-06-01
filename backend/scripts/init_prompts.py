#!/usr/bin/env python3
"""
初始化默认提示词模板脚本
Author: AI Writer Team
Created: 2025-06-01
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.prompt_service import get_prompt_service


async def init_default_prompts():
    """初始化默认提示词模板"""
    print("开始初始化默认提示词模板...")
    
    try:
        # 获取数据库会话
        db_gen = get_db()
        db: Session = next(db_gen)
        
        # 获取提示词服务
        prompt_service = get_prompt_service(db)
        
        # 初始化默认提示词
        await prompt_service.init_default_prompts()
        
        print("✅ 默认提示词模板初始化完成！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return False
    finally:
        try:
            db.close()
        except:
            pass
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 AI智能小说创作平台 - 提示词初始化工具")
    print("=" * 50)
    
    # 运行异步初始化
    success = asyncio.run(init_default_prompts())
    
    if success:
        print("\n🎉 初始化完成！可以开始使用AI生成功能了。")
    else:
        print("\n💥 初始化失败，请检查错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()