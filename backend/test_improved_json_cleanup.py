#!/usr/bin/env python3
"""
改进版JSON清理功能测试
测试增强的逗号处理算法
"""

import json
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedJSONCleaner:
    """改进版JSON清理器"""
    
    @staticmethod
    def original_clean_json_trailing_commas(json_str: str) -> str:
        """原始的逗号清理方法（来自ai_service.py）"""
        # 移除对象中的尾随逗号 (,})
        json_str = re.sub(r',\s*}', '}', json_str)
        # 移除数组中的尾随逗号 (,])
        json_str = re.sub(r',\s*]', ']', json_str)
        return json_str
    
    @staticmethod
    def improved_clean_json_trailing_commas(json_str: str) -> str:
        """改进版JSON逗号清理"""
        # 第一步：移除对象中的尾随逗号 (,})
        json_str = re.sub(r',\s*}', '}', json_str)
        
        # 第二步：移除数组中的尾随逗号 (,])
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # 第三步：移除数组/对象开头的逗号
        json_str = re.sub(r'(\[|\{)\s*,', r'\1', json_str)
        
        # 第四步：移除连续的逗号
        json_str = re.sub(r',\s*,+', ',', json_str)
        
        # 第五步：移除键后面直接跟逗号的情况（没有值）
        json_str = re.sub(r':\s*,', ': null,', json_str)
        
        # 第六步：修复null值后多余逗号的问题
        json_str = re.sub(r'null,\s*([}\]])', r'null\1', json_str)
        
        return json_str
    
    @staticmethod
    def aggressive_json_cleanup(json_str: str) -> str:
        """激进的JSON修复算法"""
        # 使用改进的基础清理
        json_str = ImprovedJSONCleaner.improved_clean_json_trailing_commas(json_str)
        
        # 尝试修复引号问题
        # 确保属性名有双引号
        json_str = re.sub(r'([{\[,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # 修复字符串值的引号
        json_str = re.sub(r':\s*([^",\[\{\}\]]*[^",\[\{\}\]\s])\s*([,\}\]])', r': "\1"\2', json_str)
        
        return json_str


def create_problematic_json_cases():
    """创建各种有问题的JSON测试用例"""
    base_json = {
        "test": "value",
        "array": ["item1", "item2"],
        "nested": {"key": "value"}
    }
    
    cases = {
        # 基础情况
        "valid": json.dumps(base_json, ensure_ascii=False),
        
        # 尾随逗号
        "trailing_object": '{"test": "value", "array": ["item1", "item2"],}',
        "trailing_array": '{"array": ["item1", "item2",]}',
        
        # 开头逗号
        "leading_array": '{"array": [,"item1", "item2"]}',
        "leading_object": '{,"test": "value"}',
        
        # 连续逗号
        "double_comma": '{"test": "value",, "array": ["item1"]}',
        "triple_comma": '{"test": "value",,, "array": ["item1"]}',
        
        # 复杂组合问题
        "complex_trailing": '{"test": "value", "array": ["item1", "item2",], "nested": {"key": "value",},}',
        "mixed_problems": '{,"test": "value",, "array": [,"item1", "item2",]}',
        
        # 来自实际worldview.txt的问题模拟
        "worldview_like": '''{"factions": [,
            {"name": "天医宗", "description": "正道领袖",},
            {"name": "无相殿", "description": "鬼修势力",}
        ],}'''
    }
    
    return cases


def test_json_cleanup_methods():
    """测试不同的JSON清理方法"""
    cases = create_problematic_json_cases()
    cleaner = ImprovedJSONCleaner()
    
    results = {
        "original_method": {},
        "improved_method": {},
        "aggressive_method": {}
    }
    
    for case_name, problematic_json in cases.items():
        logger.info(f"\n=== 测试用例: {case_name} ===")
        logger.info(f"原始JSON: {problematic_json}")
        
        # 测试原始方法
        try:
            cleaned_original = cleaner.original_clean_json_trailing_commas(problematic_json)
            json.loads(cleaned_original)
            results["original_method"][case_name] = "✅ 成功"
            logger.info("原始方法: ✅ 成功")
        except Exception as e:
            results["original_method"][case_name] = f"❌ 失败: {str(e)}"
            logger.info(f"原始方法: ❌ 失败: {str(e)}")
        
        # 测试改进方法
        try:
            cleaned_improved = cleaner.improved_clean_json_trailing_commas(problematic_json)
            json.loads(cleaned_improved)
            results["improved_method"][case_name] = "✅ 成功"
            logger.info("改进方法: ✅ 成功")
        except Exception as e:
            results["improved_method"][case_name] = f"❌ 失败: {str(e)}"
            logger.info(f"改进方法: ❌ 失败: {str(e)}")
        
        # 测试激进方法
        try:
            cleaned_aggressive = cleaner.aggressive_json_cleanup(problematic_json)
            json.loads(cleaned_aggressive)
            results["aggressive_method"][case_name] = "✅ 成功"
            logger.info("激进方法: ✅ 成功")
        except Exception as e:
            results["aggressive_method"][case_name] = f"❌ 失败: {str(e)}"
            logger.info(f"激进方法: ❌ 失败: {str(e)}")
    
    return results


def generate_comparison_report(results):
    """生成对比报告"""
    total_cases = len(results["original_method"])
    
    logger.info("\n" + "="*60)
    logger.info("JSON清理方法对比报告")
    logger.info("="*60)
    
    for method_name, method_results in results.items():
        success_count = sum(1 for result in method_results.values() if result.startswith("✅"))
        success_rate = success_count / total_cases * 100
        
        logger.info(f"\n{method_name}:")
        logger.info(f"  成功率: {success_rate:.1f}% ({success_count}/{total_cases})")
        
        for case_name, result in method_results.items():
            logger.info(f"  {case_name}: {result}")
    
    # 改进效果分析
    original_success = sum(1 for r in results["original_method"].values() if r.startswith("✅"))
    improved_success = sum(1 for r in results["improved_method"].values() if r.startswith("✅"))
    aggressive_success = sum(1 for r in results["aggressive_method"].values() if r.startswith("✅"))
    
    logger.info(f"\n改进效果:")
    logger.info(f"  原始方法 → 改进方法: +{improved_success - original_success} 个成功用例")
    logger.info(f"  改进方法 → 激进方法: +{aggressive_success - improved_success} 个成功用例")
    logger.info(f"  总体改进: +{aggressive_success - original_success} 个成功用例")


def test_worldview_specific_issues():
    """测试worldview.txt中遇到的具体问题"""
    logger.info("\n" + "="*60)
    logger.info("WorldView.txt 特定问题测试")
    logger.info("="*60)
    
    # 模拟测试中失败的具体情况
    problematic_worldview = '''{"world_base": {"name": "test",}, "factions": [,
        {"name": "天医宗", "description": "test",}
    ],}'''
    
    cleaner = ImprovedJSONCleaner()
    
    logger.info("原始有问题的JSON:")
    logger.info(problematic_worldview)
    
    # 逐步清理过程
    step1 = cleaner.original_clean_json_trailing_commas(problematic_worldview)
    logger.info(f"\n步骤1 - 原始清理后: {step1}")
    
    step2 = cleaner.improved_clean_json_trailing_commas(problematic_worldview)
    logger.info(f"\n步骤2 - 改进清理后: {step2}")
    
    step3 = cleaner.aggressive_json_cleanup(problematic_worldview)
    logger.info(f"\n步骤3 - 激进清理后: {step3}")
    
    # 测试解析
    for step_name, cleaned_json in [("原始", step1), ("改进", step2), ("激进", step3)]:
        try:
            parsed = json.loads(cleaned_json)
            logger.info(f"\n{step_name}方法解析: ✅ 成功")
            logger.info(f"解析结果: {json.dumps(parsed, ensure_ascii=False, indent=2)[:200]}...")
        except Exception as e:
            logger.info(f"\n{step_name}方法解析: ❌ 失败: {str(e)}")


def main():
    """主函数"""
    logger.info("开始JSON清理算法改进测试")
    
    # 测试各种清理方法
    results = test_json_cleanup_methods()
    
    # 生成对比报告
    generate_comparison_report(results)
    
    # 测试worldview特定问题
    test_worldview_specific_issues()
    
    logger.info("\n测试完成！")


if __name__ == "__main__":
    main()