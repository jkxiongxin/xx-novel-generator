#!/usr/bin/env python3
"""
AI响应解析测试类
测试AI服务对大模型返回值的处理能力
Author: AI Writer Team
Created: 2025-06-03
"""

import json
import re
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIResponseParser:
    """AI响应解析器 - 从ai_service.py中提取的核心解析逻辑"""
    
    def __init__(self):
        pass
    
    def _clean_json_trailing_commas(self, json_str: str) -> str:
        """清理JSON中的多余逗号"""
        # 移除对象中的尾随逗号 (,})
        json_str = re.sub(r',\s*}', '}', json_str)
        
        # 移除数组中的尾随逗号 (,])
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json_str
    
    def parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析结构化响应 - 参考ai_service.py中的generate_structured_response方法
        
        Args:
            response_text: AI模型返回的原始文本
            
        Returns:
            解析后的字典对象
        """
        try:
            logger.info(f"原始响应文本长度: {len(response_text)}")
            logger.debug(f"原始响应文本前500字符: {response_text[:500]}...")

            # 第一步：过滤掉<think>...</think>内容
            filtered_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL | re.IGNORECASE)
            if filtered_text != response_text:
                logger.info("检测到并移除了<think>标签内容")
            
            # 第二步：提取被```json ... ```包裹的内容（允许多行，使用单行匹配模式 re.DOTALL）
            match = re.search(r"```json\s*(.*?)\s*```", filtered_text, re.DOTALL | re.IGNORECASE)
            if match:
                json_str = match.group(1)
                logger.info("成功提取```json```包裹的内容")
                logger.debug(f"提取的JSON字符串长度: {len(json_str)}")
            else:
                json_str = filtered_text
                logger.warning("未找到```json```标记，使用原始文本进行解析")

            # 第三步：清理JSON中的尾随逗号
            cleaned_json = self._clean_json_trailing_commas(json_str)
            if cleaned_json != json_str:
                logger.info("清理了JSON中的尾随逗号")

            # 第四步：尝试解析JSON
            try:
                parsed_data = json.loads(cleaned_json)
                logger.info("JSON解析成功")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败: {str(e)}")
                logger.warning(f"无法解析为JSON格式，返回原始文本包装")
                return {"content": response_text}

        except Exception as e:
            logger.error(f"解析结构化响应失败: {str(e)}")
            return {"error": f"解析失败: {str(e)}", "content": response_text}


class AIResponseParserTest:
    """AI响应解析测试类"""
    
    def __init__(self):
        self.parser = AIResponseParser()
        self.test_results = []
    
    def load_test_data(self, file_path: str) -> str:
        """加载测试数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"成功加载测试文件: {file_path}")
            return content
        except Exception as e:
            logger.error(f"加载测试文件失败: {str(e)}")
            return ""
    
    def validate_worldview_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证世界观数据结构的完整性"""
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "field_counts": {},
            "structure_analysis": {}
        }
        
        # 检查顶级字段
        expected_top_fields = ["world_base", "geography", "power_system", "history", "factions"]
        for field in expected_top_fields:
            if field not in data:
                validation_result["missing_fields"].append(field)
                validation_result["is_valid"] = False
            else:
                validation_result["field_counts"][field] = "present"
        
        # 详细结构分析
        if "world_base" in data:
            world_base = data["world_base"]
            validation_result["structure_analysis"]["world_base"] = {
                "has_name": "name" in world_base,
                "has_description": "description" in world_base,
                "has_background": "background" in world_base,
                "has_rules": "rules" in world_base,
                "has_characteristics": "characteristics" in world_base,
                "rules_count": len(world_base.get("rules", [])),
                "characteristics_count": len(world_base.get("characteristics", []))
            }
        
        if "geography" in data:
            geography = data["geography"]
            validation_result["structure_analysis"]["geography"] = {
                "has_map_regions": "map_regions" in geography,
                "has_special_locations": "special_locations" in geography,
                "regions_count": len(geography.get("map_regions", [])),
                "locations_count": len(geography.get("special_locations", []))
            }
        
        if "power_system" in data:
            power_system = data["power_system"]
            validation_result["structure_analysis"]["power_system"] = {
                "has_name": "name" in power_system,
                "has_description": "description" in power_system,
                "has_levels": "levels" in power_system,
                "has_unique_features": "unique_features" in power_system,
                "has_cultivation_methods": "cultivation_methods" in power_system,
                "levels_count": len(power_system.get("levels", [])),
                "features_count": len(power_system.get("unique_features", [])),
                "methods_count": len(power_system.get("cultivation_methods", []))
            }
        
        if "history" in data:
            history = data["history"]
            validation_result["structure_analysis"]["history"] = {
                "has_eras": "eras" in history,
                "has_artifacts": "significant_artifacts" in history,
                "eras_count": len(history.get("eras", [])),
                "artifacts_count": len(history.get("significant_artifacts", []))
            }
        
        if "factions" in data:
            factions = data["factions"]
            validation_result["structure_analysis"]["factions"] = {
                "factions_count": len(factions),
                "factions_with_ideology": sum(1 for f in factions if "ideology" in f),
                "factions_with_powers": sum(1 for f in factions if "powers_and_abilities" in f),
                "factions_with_structure": sum(1 for f in factions if "structure" in f)
            }
        
        return validation_result
    
    def run_test_case(self, test_name: str, test_data: str) -> Dict[str, Any]:
        """运行单个测试用例"""
        logger.info(f"=== 开始测试: {test_name} ===")
        
        test_result = {
            "test_name": test_name,
            "success": False,
            "parse_success": False,
            "validation_success": False,
            "data": None,
            "validation_result": None,
            "error": None,
            "execution_time": 0
        }
        
        try:
            import time
            start_time = time.time()
            
            # 解析响应
            parsed_data = self.parser.parse_structured_response(test_data)
            test_result["parse_success"] = True
            test_result["data"] = parsed_data
            
            # 如果解析成功且不是错误响应，进行结构验证
            if "error" not in parsed_data and "content" not in parsed_data:
                validation_result = self.validate_worldview_structure(parsed_data)
                test_result["validation_result"] = validation_result
                test_result["validation_success"] = validation_result["is_valid"]
                test_result["success"] = validation_result["is_valid"]
            elif "content" in parsed_data:
                # 这种情况表示解析失败，但没有抛出异常
                test_result["success"] = False
                test_result["error"] = "Failed to parse as JSON, returned raw content"
            else:
                test_result["success"] = False
                test_result["error"] = parsed_data.get("error", "Unknown error")
            
            test_result["execution_time"] = time.time() - start_time
            
        except Exception as e:
            test_result["error"] = str(e)
            logger.error(f"测试执行失败: {str(e)}")
        
        logger.info(f"=== 测试完成: {test_name}, 成功: {test_result['success']} ===")
        return test_result
    
    def create_test_variations(self, base_content: str) -> Dict[str, str]:
        """创建测试变体"""
        variations = {}
        
        # 原始内容
        variations["original"] = base_content
        
        # 添加<think>标签的变体
        think_content = "<think>这是一个复杂的世界观设计，需要仔细构建...</think>\n" + base_content
        variations["with_think_tags"] = think_content
        
        # 移除```json```标记的变体
        no_markers = base_content.replace("```json", "").replace("```", "")
        variations["without_json_markers"] = no_markers
        
        # 添加尾随逗号的变体
        trailing_comma_content = base_content.replace('"factions": [', '"factions": [,').replace('}', '},')
        variations["with_trailing_commas"] = trailing_comma_content
        
        # 混合所有问题的变体
        problematic = "<think>复杂思考过程...</think>\n" + trailing_comma_content.replace("```json", "").replace("```", "")
        variations["problematic_mixed"] = problematic
        
        return variations
    
    def run_all_tests(self, test_file_path: str):
        """运行所有测试"""
        logger.info("开始AI响应解析测试")
        
        # 加载基础测试数据
        base_content = self.load_test_data(test_file_path)
        if not base_content:
            logger.error("无法加载测试数据，退出测试")
            return
        
        # 创建测试变体
        test_variations = self.create_test_variations(base_content)
        
        # 运行所有测试用例
        for test_name, test_data in test_variations.items():
            result = self.run_test_case(test_name, test_data)
            self.test_results.append(result)
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        logger.info("\n" + "="*60)
        logger.info("AI响应解析测试报告")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        parse_successful = sum(1 for r in self.test_results if r["parse_success"])
        
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"解析成功: {parse_successful}")
        logger.info(f"验证成功: {successful_tests}")
        logger.info(f"成功率: {successful_tests/total_tests*100:.1f}%")
        logger.info("")
        
        # 详细测试结果
        for result in self.test_results:
            status = "✅ 成功" if result["success"] else "❌ 失败"
            parse_status = "✅" if result["parse_success"] else "❌"
            
            logger.info(f"{status} | 解析{parse_status} | {result['test_name']} | 耗时: {result['execution_time']:.3f}s")
            
            if result["error"]:
                logger.info(f"    错误: {result['error']}")
            
            if result["validation_result"]:
                val_result = result["validation_result"]
                if val_result["missing_fields"]:
                    logger.info(f"    缺失字段: {val_result['missing_fields']}")
                
                # 显示结构分析摘要
                if "structure_analysis" in val_result:
                    analysis = val_result["structure_analysis"]
                    for section, details in analysis.items():
                        if isinstance(details, dict):
                            counts = [f"{k}: {v}" for k, v in details.items() if k.endswith("_count")]
                            if counts:
                                logger.info(f"    {section}: {', '.join(counts)}")
            
            logger.info("")
        
        # 性能分析
        avg_time = sum(r["execution_time"] for r in self.test_results) / total_tests
        max_time = max(r["execution_time"] for r in self.test_results)
        min_time = min(r["execution_time"] for r in self.test_results)
        
        logger.info("性能分析:")
        logger.info(f"  平均解析时间: {avg_time:.3f}s")
        logger.info(f"  最长解析时间: {max_time:.3f}s")
        logger.info(f"  最短解析时间: {min_time:.3f}s")
        
        # 推荐和问题分析
        logger.info("\n问题分析:")
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            logger.info("失败的测试用例:")
            for test in failed_tests:
                logger.info(f"  - {test['test_name']}: {test['error']}")
        else:
            logger.info("所有测试用例都通过了！AI响应解析功能运行正常。")


def main():
    """主函数"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    test_file_path = current_dir / "worldview.txt"
    
    # 检查测试文件是否存在
    if not test_file_path.exists():
        logger.error(f"测试文件不存在: {test_file_path}")
        return
    
    # 创建测试实例并运行
    tester = AIResponseParserTest()
    tester.run_all_tests(str(test_file_path))


if __name__ == "__main__":
    main()