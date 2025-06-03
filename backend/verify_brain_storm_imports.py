"""
验证脑洞生成器模块导入
Author: AI Writer Team
Created: 2025-06-03
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """验证所有脑洞生成器相关模块的导入"""
    
    print("开始验证脑洞生成器模块导入...")
    
    try:
        # 验证模型导入
        print("1. 验证数据模型导入...")
        from app.models.brain_storm import (
            BrainStormHistory, BrainStormIdea, BrainStormPreferences,
            BrainStormElements, BrainStormTopicSuggestion
        )
        print("✓ 数据模型导入成功")
        
        # 验证模式导入
        print("2. 验证数据模式导入...")
        from app.schemas.brain_storm import (
            BrainStormRequest, BrainStormResponse, GeneratedIdea,
            BrainStormHistoryResponse, ElementSuggestionsResponse,
            UserPreferences, SavePreferencesRequest
        )
        print("✓ 数据模式导入成功")
        
        # 验证服务导入
        print("3. 验证服务层导入...")
        from app.services.brain_storm_service import BrainStormService, get_brain_storm_service
        print("✓ 服务层导入成功")
        
        # 验证API导入（部分验证，因为需要数据库连接）
        print("4. 验证API模块结构...")
        import app.api.v1.generation
        print("✓ API模块结构正确")
        
        # 验证更新的用户模型
        print("5. 验证用户模型关系...")
        from app.models.user import User
        print("✓ 用户模型关系正确")
        
        print("\n所有模块导入验证通过! ✓")
        return True
        
    except ImportError as e:
        print(f"✗ 导入错误: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {str(e)}")
        return False


def verify_model_relationships():
    """验证模型关系"""
    print("\n验证模型关系...")
    
    try:
        from app.models.brain_storm import BrainStormHistory, BrainStormIdea
        from app.models.user import User
        
        # 检查模型类是否正确定义
        assert hasattr(BrainStormHistory, '__tablename__')
        assert hasattr(BrainStormIdea, '__tablename__')
        assert hasattr(User, 'brain_storm_history')
        assert hasattr(User, 'brain_storm_preferences')
        
        print("✓ 模型关系验证通过")
        return True
        
    except Exception as e:
        print(f"✗ 模型关系验证失败: {str(e)}")
        return False


def verify_schema_validation():
    """验证模式验证"""
    print("\n验证数据模式验证...")
    
    try:
        from app.schemas.brain_storm import BrainStormRequest, GeneratedIdea
        
        # 测试请求模式验证
        valid_request = BrainStormRequest(
            topic="测试主题",
            creativity_level=8,
            idea_count=5,
            idea_type=["plot"],
            elements=["测试要素"]
        )
        
        # 测试创意模式
        valid_idea = GeneratedIdea(
            id="test_id",
            content="测试创意内容",
            type="plot",
            tags=["测试标签"],
            creativity_score=8.5
        )
        
        print("✓ 数据模式验证通过")
        return True
        
    except Exception as e:
        print(f"✗ 数据模式验证失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=== 脑洞生成器模块验证 ===")
    
    success = True
    
    # 验证导入
    if not verify_imports():
        success = False
    
    # 验证模型关系
    if not verify_model_relationships():
        success = False
    
    # 验证模式验证
    if not verify_schema_validation():
        success = False
    
    if success:
        print("\n🎉 所有验证通过！脑洞生成器后端实现已准备就绪。")
        print("\n下一步操作：")
        print("1. 运行数据库迁移: python init_brain_storm.py")
        print("2. 启动后端服务: uvicorn app.main:app --reload")
        print("3. 运行API测试: python test_brain_storm_api.py")
    else:
        print("\n❌ 验证失败，请检查错误信息并修复问题。")
        sys.exit(1)


if __name__ == "__main__":
    main()