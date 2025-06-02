#!/usr/bin/env python3
"""
首页API测试脚本
验证新开发的首页相关接口是否正常工作
Author: AI Writer Team
Created: 2025-06-01
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001/api/v1"

def test_system_status():
    """测试系统状态接口"""
    print("🧪 测试系统状态接口...")
    try:
        response = requests.get(f"{BASE_URL}/generation/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 系统状态接口正常: {data['message']}")
            print(f"   AI服务状态: {data['data']['ai_service']}")
            print(f"   数据库状态: {data['data']['database']}")
            return True
        else:
            print(f"❌ 系统状态接口错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 系统状态接口异常: {str(e)}")
        return False

def test_health_check():
    """测试健康检查接口"""
    print("\n🧪 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查接口正常: {data['message']}")
            return True
        else:
            print(f"❌ 健康检查接口错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查接口异常: {str(e)}")
        return False

def test_with_auth(token):
    """测试需要认证的接口"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 测试用户信息接口...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 用户信息接口正常: {data['message']}")
            return True
        else:
            print(f"❌ 用户信息接口错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 用户信息接口异常: {str(e)}")
        return False

def test_stats_overview(token):
    """测试统计概览接口"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 测试统计概览接口...")
    try:
        response = requests.get(f"{BASE_URL}/novels/stats/overview", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计概览接口正常: {data['message']}")
            print(f"   总小说数: {data['data']['total_novels']}")
            print(f"   总章节数: {data['data']['total_chapters']}")
            return True
        else:
            print(f"❌ 统计概览接口错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计概览接口异常: {str(e)}")
        return False

def test_recent_novels(token):
    """测试最近小说接口"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 测试最近小说接口...")
    try:
        response = requests.get(f"{BASE_URL}/novels/recent?limit=3", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 最近小说接口正常: {data['message']}")
            print(f"   返回小说数: {data['data']['total']}")
            return True
        else:
            print(f"❌ 最近小说接口错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 最近小说接口异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始首页API测试...")
    print("=" * 50)
    
    # 测试无需认证的接口
    success_count = 0
    total_tests = 0
    
    total_tests += 1
    if test_health_check():
        success_count += 1
        
    total_tests += 1
    if test_system_status():
        success_count += 1
    
    # 如果提供了认证token，测试需要认证的接口
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"\n🔑 使用提供的认证token进行测试...")
        
        total_tests += 1
        if test_with_auth(token):
            success_count += 1
            
        total_tests += 1
        if test_stats_overview(token):
            success_count += 1
            
        total_tests += 1
        if test_recent_novels(token):
            success_count += 1
    else:
        print("\n💡 提示: 传入认证token作为参数可测试需要登录的接口")
        print("   用法: python test_homepage_apis.py <your_token>")
    
    # 总结
    print("\n" + "=" * 50)
    print(f"📊 测试总结: {success_count}/{total_tests} 个接口测试通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！首页接口开发完成。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查接口实现。")
        return 1

if __name__ == "__main__":
    exit(main())