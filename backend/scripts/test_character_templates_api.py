#!/usr/bin/env python3
"""
测试角色模板API功能
Author: AI Assistant
Created: 2025-06-03
"""

import sys
import os

# 添加父目录到路径，以便导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.character import Character
from app.models.character_template import CharacterTemplateFavorite

def test_character_templates_query():
    """测试角色模板查询功能"""
    
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("测试角色模板数据库查询")
        print("=" * 50)
        
        # 1. 测试基础查询 - 查找所有模板角色
        print("1. 测试基础模板角色查询...")
        templates = db.query(Character).filter(Character.is_template == True).all()
        print(f"   找到 {len(templates)} 个模板角色")
        
        # 2. 测试用户查询
        print("\n2. 测试用户查询...")
        users = db.query(User).all()
        print(f"   找到 {len(users)} 个用户")
        if users:
            test_user = users[0]
            print(f"   测试用户: {test_user.username} (ID: {test_user.id})")
        else:
            print("   ⚠️  没有找到用户，创建一个测试用户...")
            test_user = User(
                username="test_user",
                email="test@example.com",
                password_hash="test_hash"
            )
            db.add(test_user)
            db.commit()
            print(f"   ✓ 创建测试用户: {test_user.username}")
        
        # 3. 测试收藏表查询（这是之前失败的查询）
        print("\n3. 测试收藏表查询...")
        try:
            favorites = db.query(CharacterTemplateFavorite.character_id).filter(
                CharacterTemplateFavorite.user_id == test_user.id
            ).all()
            print(f"   ✓ 收藏表查询成功，找到 {len(favorites)} 个收藏")
        except Exception as e:
            print(f"   ✗ 收藏表查询失败: {e}")
            return False
        
        # 4. 测试带JOIN的查询（模拟API中的查询）
        print("\n4. 测试带JOIN的查询...")
        try:
            from app.models.character_template import CharacterTemplateDetail
            
            query = db.query(Character).join(
                CharacterTemplateDetail, 
                Character.id == CharacterTemplateDetail.character_id,
                isouter=True  # 使用左连接
            ).filter(Character.is_template == True)
            
            result_count = query.count()
            print(f"   ✓ JOIN查询成功，找到 {result_count} 个结果")
            
            # 获取前几个结果查看
            results = query.limit(3).all()
            for char in results:
                print(f"   - 角色: {char.name}, 模板详情: {'有' if char.template_detail else '无'}")
                
        except Exception as e:
            print(f"   ✗ JOIN查询失败: {e}")
            return False
        
        # 5. 创建一个测试模板角色（如果没有的话）
        print("\n5. 检查并创建测试模板角色...")
        if len(templates) == 0:
            print("   没有模板角色，创建一个测试模板角色...")
            test_character = Character(
                name="测试模板角色",
                user_id=test_user.id,
                gender="male",
                personality="勇敢、正义",
                character_type="protagonist",
                description="这是一个测试用的模板角色",
                is_template=True,
                tags=["英雄", "勇者"]
            )
            db.add(test_character)
            db.commit()
            print(f"   ✓ 创建测试模板角色: {test_character.name} (ID: {test_character.id})")
            
            # 为这个角色创建模板详情
            from app.models.character_template import CharacterTemplateDetail
            detail = CharacterTemplateDetail(
                character_id=test_character.id,
                detailed_description="详细的角色描述",
                usage_count=0,
                rating=4.5,
                is_popular=True,
                is_new=True
            )
            db.add(detail)
            db.commit()
            print(f"   ✓ 创建模板详情")
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！角色模板功能数据库层面工作正常。")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("角色模板API功能测试")
    success = test_character_templates_query()
    
    if success:
        print("\n✓ 测试完成！现在应该可以正常访问角色模板API了。")
        print("可以尝试重新访问: http://192.168.16.108:5173/api/v1/character-templates/")
    else:
        print("\n✗ 测试失败！请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()