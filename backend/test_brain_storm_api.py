"""
脑洞生成器API测试脚本
Author: AI Writer Team
Created: 2025-06-03
"""

import requests
import json
import time
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"


def test_brain_storm_api():
    """测试脑洞生成器API"""
    
    print("开始测试脑洞生成器API...")
    
    # 1. 登录获取token
    print("\n1. 用户登录...")
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("✓ 登录成功")
    
    # 2. 测试获取用户偏好
    print("\n2. 测试获取用户偏好...")
    response = requests.get(f"{BASE_URL}/generation/brain-storm/preferences", headers=headers)
    if response.status_code == 200:
        preferences = response.json()
        print(f"✓ 获取用户偏好成功: {json.dumps(preferences, indent=2, ensure_ascii=False)}")
    else:
        print(f"✗ 获取用户偏好失败: {response.status_code} - {response.text}")
    
    # 3. 测试获取要素建议
    print("\n3. 测试获取要素建议...")
    response = requests.get(f"{BASE_URL}/generation/brain-storm/elements", headers=headers)
    if response.status_code == 200:
        elements = response.json()
        print(f"✓ 获取要素建议成功，共 {len(elements.get('categories', []))} 个分类")
        for category in elements.get('categories', [])[:2]:  # 只显示前2个分类
            print(f"  - {category['display_name']}: {len(category['elements'])} 个要素")
    else:
        print(f"✗ 获取要素建议失败: {response.status_code} - {response.text}")
    
    # 4. 测试获取主题建议
    print("\n4. 测试获取主题建议...")
    response = requests.get(f"{BASE_URL}/generation/brain-storm/topic-suggestions", headers=headers)
    if response.status_code == 200:
        topics = response.json()
        print(f"✓ 获取主题建议成功，共 {len(topics.get('suggestions', []))} 个建议")
        for topic in topics.get('suggestions', [])[:3]:  # 只显示前3个
            print(f"  - {topic['topic']}: {topic['description']}")
    else:
        print(f"✗ 获取主题建议失败: {response.status_code} - {response.text}")
    
    # 5. 测试脑洞生成
    print("\n5. 测试脑洞生成...")
    brain_storm_request = {
        "topic": "穿越到修仙世界的程序员",
        "creativity_level": 8,
        "idea_count": 5,
        "idea_type": ["plot", "character"],
        "elements": ["修仙", "科技", "穿越"],
        "style": "幽默轻松",
        "user_input": "希望结合现代科技和修仙元素，创造有趣的故事"
    }
    
    response = requests.post(
        f"{BASE_URL}/generation/brain-storm",
        json=brain_storm_request,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        generation_id = result.get("generation_id")
        ideas = result.get("ideas", [])
        print(f"✓ 脑洞生成成功，生成ID: {generation_id}")
        print(f"  生成了 {len(ideas)} 个创意:")
        
        for i, idea in enumerate(ideas[:3], 1):  # 只显示前3个创意
            print(f"  {i}. {idea['content'][:100]}...")
            print(f"     类型: {idea['type']}, 创意评分: {idea.get('creativity_score', 'N/A')}")
        
        # 保存generation_id用于后续测试
        global test_generation_id
        test_generation_id = generation_id
        
    else:
        print(f"✗ 脑洞生成失败: {response.status_code} - {response.text}")
        return
    
    # 6. 测试评价生成结果
    print("\n6. 测试评价生成结果...")
    if 'test_generation_id' in globals():
        rating_request = {
            "rating": 4,
            "feedback": "生成的创意很有趣，特别是科技与修仙结合的部分",
            "useful_ideas": [ideas[0]["id"]] if ideas else [],
            "improvement_suggestions": "希望能有更多关于角色背景的描述"
        }
        
        response = requests.post(
            f"{BASE_URL}/generation/brain-storm/{test_generation_id}/rating",
            json=rating_request,
            headers=headers
        )
        
        if response.status_code == 200:
            rating_result = response.json()
            print(f"✓ 评价成功，平均评分: {rating_result.get('average_rating', 'N/A')}")
        else:
            print(f"✗ 评价失败: {response.status_code} - {response.text}")
    
    # 7. 测试获取生成历史
    print("\n7. 测试获取生成历史...")
    response = requests.get(f"{BASE_URL}/generation/brain-storm/history", headers=headers)
    if response.status_code == 200:
        history = response.json()
        print(f"✓ 获取历史成功，共 {history.get('total', 0)} 条记录")
        for record in history.get('history', [])[:2]:  # 只显示前2条
            print(f"  - {record['topic']} (创意程度: {record['creativity_level']}, 生成数: {record['ideas_generated']})")
    else:
        print(f"✗ 获取历史失败: {response.status_code} - {response.text}")
    
    # 8. 测试获取历史详情
    print("\n8. 测试获取历史详情...")
    if response.status_code == 200 and history.get('history'):
        history_id = history['history'][0]['id']
        response = requests.get(
            f"{BASE_URL}/generation/brain-storm/history/{history_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            detail = response.json()
            print(f"✓ 获取历史详情成功")
            print(f"  主题: {detail['history']['topic']}")
            print(f"  创意数量: {len(detail['ideas'])}")
            print(f"  使用统计: {detail['usage_stats']}")
        else:
            print(f"✗ 获取历史详情失败: {response.status_code} - {response.text}")
    
    # 9. 测试保存用户偏好
    print("\n9. 测试保存用户偏好...")
    preferences_request = {
        "default_creativity_level": 8,
        "default_idea_count": 12,
        "preferred_types": ["plot", "character"],
        "favorite_elements": ["修仙", "科技", "穿越", "幽默"],
        "default_style": "轻松幽默",
        "auto_save_history": True,
        "show_creativity_scores": True
    }
    
    response = requests.post(
        f"{BASE_URL}/generation/brain-storm/preferences",
        json=preferences_request,
        headers=headers
    )
    
    if response.status_code == 200:
        saved_prefs = response.json()
        print("✓ 保存用户偏好成功")
        print(f"  默认创意程度: {saved_prefs['preferences']['default_creativity_level']}")
        print(f"  偏好类型: {saved_prefs['preferences']['preferred_types']}")
    else:
        print(f"✗ 保存用户偏好失败: {response.status_code} - {response.text}")
    
    # 10. 测试获取生成统计
    print("\n10. 测试获取生成统计...")
    response = requests.get(f"{BASE_URL}/generation/brain-storm/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("✓ 获取统计信息成功")
        print(f"  总生成次数: {stats.get('total_generations', 0)}")
        print(f"  总创意数: {stats.get('total_ideas', 0)}")
        print(f"  平均每次生成: {stats.get('average_ideas_per_generation', 0)}")
    else:
        print(f"✗ 获取统计信息失败: {response.status_code} - {response.text}")
    
    print("\n脑洞生成器API测试完成!")


def test_system_status():
    """测试系统状态接口"""
    print("\n测试系统状态接口...")
    
    response = requests.get(f"{BASE_URL}/generation/status")
    if response.status_code == 200:
        status = response.json()
        print("✓ 系统状态获取成功")
        print(f"  AI服务状态: {status['data']['ai_service']}")
        print(f"  数据库状态: {status['data']['database']}")
        print(f"  功能开关: {status['data']['feature_flags']}")
    else:
        print(f"✗ 系统状态获取失败: {response.status_code} - {response.text}")


def create_test_user():
    """创建测试用户"""
    print("创建测试用户...")
    
    register_data = {
        "username": TEST_USERNAME,
        "email": "test@example.com",
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print("✓ 测试用户创建成功")
    elif response.status_code == 400 and "already exists" in response.text:
        print("✓ 测试用户已存在")
    else:
        print(f"✗ 创建测试用户失败: {response.status_code} - {response.text}")


def main():
    """主函数"""
    print("=== 脑洞生成器API测试 ===")
    
    # 测试系统状态
    test_system_status()
    
    # 创建测试用户
    create_test_user()
    
    # 等待一秒
    time.sleep(1)
    
    # 测试脑洞生成器API
    test_brain_storm_api()


if __name__ == "__main__":
    main()