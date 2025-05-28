#!/usr/bin/env python3
"""
安全确认工具模块
实现多重确认机制，确保敏感操作的安全性
"""

from typing import Dict, Optional, Tuple

class SecurityConfirmation:
    """安全确认类，用于敏感操作的多重确认"""
    
    @staticmethod
    def validate_power_operation(
        instance_info: Dict,
        operation: str,
        ip_confirmation: str,
        name_confirmation: str,
        operation_confirmation: str
    ) -> Tuple[bool, str]:
        """
        验证电源操作的三次确认
        
        Args:
            instance_info (dict): 实例信息
            operation (str): 操作类型 ('shutdown', 'reboot', 'power_off', 'power_on')
            ip_confirmation (str): 用户确认的IP地址
            name_confirmation (str): 用户确认的实例名称
            operation_confirmation (str): 用户确认的操作类型
            
        Returns:
            Tuple[bool, str]: (是否通过验证, 错误信息)
        """
        errors = []
        
        # 获取实例的实际信息
        actual_ip = instance_info.get('public_ip', instance_info.get('public_ipv4', '未知'))
        actual_name = instance_info.get('name', instance_info.get('instance_name', '未知'))
        
        # 第一次确认：IP地址
        if ip_confirmation.strip() != actual_ip:
            errors.append(f"IP地址确认失败: 期望 '{actual_ip}', 但收到 '{ip_confirmation}'")
        
        # 第二次确认：实例名称
        if name_confirmation.strip() != actual_name:
            errors.append(f"实例名称确认失败: 期望 '{actual_name}', 但收到 '{name_confirmation}'")
        
        # 第三次确认：操作类型
        valid_operations = {
            'shutdown': ['shutdown', '关机', '优雅关机'],
            'power_off': ['power_off', '强制关机', '强制断电'],
            'reboot': ['reboot', '重启', '重新启动'],
            'power_on': ['power_on', '开机', '启动']
        }
        
        operation_confirmed = False
        for op, variations in valid_operations.items():
            if op == operation and operation_confirmation.strip().lower() in [v.lower() for v in variations]:
                operation_confirmed = True
                break
        
        if not operation_confirmed:
            expected_ops = valid_operations.get(operation, [operation])
            errors.append(f"操作确认失败: 期望 '{expected_ops[0]}', 但收到 '{operation_confirmation}'")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, "所有确认项目验证通过"
    
    @staticmethod
    def create_confirmation_prompt(instance_info: Dict, operation: str) -> Dict[str, str]:
        """
        创建确认提示信息
        
        Args:
            instance_info (dict): 实例信息
            operation (str): 操作类型
            
        Returns:
            Dict[str, str]: 确认提示信息
        """
        actual_ip = instance_info.get('public_ip', instance_info.get('public_ipv4', '未知'))
        actual_name = instance_info.get('name', instance_info.get('instance_name', '未知'))
        
        operation_names = {
            'shutdown': '优雅关机',
            'power_off': '强制关机',
            'reboot': '重启',
            'power_on': '开机'
        }
        
        operation_name = operation_names.get(operation, operation)
        
        return {
            'target_ip': actual_ip,
            'target_name': actual_name,
            'operation_name': operation_name,
            'warning': f"您即将对实例 '{actual_name}' ({actual_ip}) 执行 '{operation_name}' 操作",
            'confirmation_requirements': [
                f"请确认目标IP地址: {actual_ip}",
                f"请确认实例名称: {actual_name}",
                f"请确认操作类型: {operation_name}"
            ]
        }
    
    @staticmethod
    def check_operation_safety(instance_info: Dict, operation: str) -> Tuple[bool, str, list]:
        """
        检查操作的安全性
        
        Args:
            instance_info (dict): 实例信息
            operation (str): 操作类型
            
        Returns:
            Tuple[bool, str, list]: (是否安全, 安全级别, 警告信息列表)
        """
        warnings = []
        status = instance_info.get('status', instance_info.get('state', 'unknown')).lower()
        
        # 检查当前状态与操作的兼容性
        if operation == 'power_on' and status in ['running', 'active']:
            warnings.append("实例已经处于运行状态，开机操作可能无效")
        
        if operation in ['shutdown', 'power_off'] and status in ['stopped', 'off', 'halted']:
            warnings.append("实例已经处于关闭状态，关机操作可能无效")
        
        if operation == 'reboot' and status not in ['running', 'active']:
            warnings.append("实例未处于运行状态，重启操作可能失败")
        
        # 检查实例标签和特殊属性
        tags = instance_info.get('tags', [])
        if isinstance(tags, list):
            production_tags = ['production', 'prod', 'critical', 'important']
            for tag in tags:
                tag_str = str(tag).lower()
                if any(ptag in tag_str for ptag in production_tags):
                    warnings.append(f"检测到生产环境标签: {tag}")
        
        # 检查实例大小/类型
        instance_type = instance_info.get('instance_type', instance_info.get('size_slug', ''))
        if instance_type and any(keyword in instance_type.lower() for keyword in ['large', 'xlarge', '2xlarge']):
            warnings.append(f"这是一个大型实例 ({instance_type})，请谨慎操作")
        
        # 确定安全级别
        if len(warnings) == 0:
            safety_level = "安全"
            is_safe = True
        elif len(warnings) <= 2:
            safety_level = "需要注意"
            is_safe = True
        else:
            safety_level = "高风险"
            is_safe = False
        
        return is_safe, safety_level, warnings

def require_triple_confirmation(instance_info: Dict, operation: str) -> Dict[str, any]:
    """
    生成三重确认要求的完整信息
    
    Args:
        instance_info (dict): 实例信息
        operation (str): 操作类型
        
    Returns:
        Dict[str, any]: 确认要求信息
    """
    security = SecurityConfirmation()
    
    # 获取确认提示
    prompt = security.create_confirmation_prompt(instance_info, operation)
    
    # 检查操作安全性
    is_safe, safety_level, warnings = security.check_operation_safety(instance_info, operation)
    
    return {
        'requires_confirmation': True,
        'confirmation_prompt': prompt,
        'safety_check': {
            'is_safe': is_safe,
            'safety_level': safety_level,
            'warnings': warnings
        },
        'confirmation_format': {
            'ip_confirmation': f"请输入目标IP地址: {prompt['target_ip']}",
            'name_confirmation': f"请输入实例名称: {prompt['target_name']}", 
            'operation_confirmation': f"请输入操作类型: {prompt['operation_name']}"
        }
    } 