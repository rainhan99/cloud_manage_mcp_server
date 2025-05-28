#!/usr/bin/env python3
"""
Vultr 提供商模块
支持查询、开关机、重启操作，带三次确认机制
"""

import os
import requests
from typing import Dict, Optional
from utils.security import SecurityConfirmation, require_triple_confirmation

class VultrProvider:
    """Vultr 提供商类"""
    
    def __init__(self):
        self.api_key = os.getenv('VULTR_API_KEY')
        self.base_url = 'https://api.vultr.com/v2'
        
        if self.api_key:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            self.available = True
        else:
            self.available = False
            self.error = "VULTR_API_KEY环境变量未配置"
    
    def get_instance_by_ip(self, ip_address: str) -> Dict:
        """
        根据公网IP地址查找Vultr实例
        
        Args:
            ip_address (str): 公网IP地址
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'Vultr服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'vultr'
            }
        
        try:
            # 获取所有实例
            response = requests.get(f'{self.base_url}/instances', headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'error': f'Vultr API调用失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            data = response.json()
            instances = data.get('instances', [])
            
            # 查找匹配的IP地址
            for instance in instances:
                if instance.get('main_ip') == ip_address:
                    instance_info = self._format_instance_info(instance)
                    return {
                        'provider': 'vultr',
                        'found': True,
                        'instance_info': instance_info
                    }
            
            return {
                'provider': 'vultr',
                'found': False,
                'message': f'未找到使用IP地址 {ip_address} 的Vultr实例',
                'total_instances_checked': len(instances)
            }
            
        except requests.RequestException as e:
            return {
                'error': f'网络请求失败: {str(e)}',
                'provider': 'vultr'
            }
        except Exception as e:
            return {
                'error': f'查询Vultr实例时发生错误: {str(e)}',
                'provider': 'vultr'
            }
    
    def get_instance_by_id(self, instance_id: str) -> Dict:
        """
        根据实例ID查找Vultr实例
        
        Args:
            instance_id (str): Vultr实例ID
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'Vultr服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'vultr'
            }
        
        try:
            response = requests.get(f'{self.base_url}/instances/{instance_id}', headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return {
                    'provider': 'vultr',
                    'found': False,
                    'message': f'未找到ID为 {instance_id} 的Vultr实例'
                }
            
            if response.status_code != 200:
                return {
                    'error': f'Vultr API调用失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            data = response.json()
            instance = data.get('instance', {})
            instance_info = self._format_instance_info(instance)
            
            return {
                'provider': 'vultr',
                'found': True,
                'instance_info': instance_info
            }
            
        except requests.RequestException as e:
            return {
                'error': f'网络请求失败: {str(e)}',
                'provider': 'vultr'
            }
        except Exception as e:
            return {
                'error': f'查询Vultr实例时发生错误: {str(e)}',
                'provider': 'vultr'
            }
    
    def list_instances(self) -> Dict:
        """
        列出所有Vultr实例
        
        Returns:
            Dict: 实例列表或错误信息
        """
        if not self.available:
            return {
                'error': f'Vultr服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'vultr'
            }
        
        try:
            response = requests.get(f'{self.base_url}/instances', headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'error': f'Vultr API调用失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            data = response.json()
            instances = data.get('instances', [])
            
            instance_list = []
            for instance in instances:
                instance_info = self._format_instance_summary(instance)
                instance_list.append(instance_info)
            
            return {
                'provider': 'vultr',
                'total_instances': len(instance_list),
                'instances': instance_list
            }
            
        except requests.RequestException as e:
            return {
                'error': f'网络请求失败: {str(e)}',
                'provider': 'vultr'
            }
        except Exception as e:
            return {
                'error': f'列出Vultr实例时发生错误: {str(e)}',
                'provider': 'vultr'
            }
    
    def power_on_instance(
        self, 
        instance_id: str, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        开启Vultr实例（需要三次确认）
        """
        return self._execute_power_operation(
            instance_id, 'start', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def power_off_instance(
        self, 
        instance_id: str, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        强制关闭Vultr实例（需要三次确认）
        """
        return self._execute_power_operation(
            instance_id, 'halt', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def reboot_instance(
        self, 
        instance_id: str, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        重启Vultr实例（需要三次确认）
        """
        return self._execute_power_operation(
            instance_id, 'reboot', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def _execute_power_operation(
        self, 
        instance_id: str, 
        operation: str, 
        ip_confirmation: str, 
        name_confirmation: str, 
        operation_confirmation: str
    ) -> Dict:
        """
        执行电源操作的通用函数
        """
        if not self.available:
            return {
                'error': f'Vultr服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'vultr'
            }
        
        # 首先获取实例信息
        try:
            response = requests.get(f'{self.base_url}/instances/{instance_id}', headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return {
                    'error': f'未找到ID为 {instance_id} 的Vultr实例',
                    'provider': 'vultr'
                }
            
            if response.status_code != 200:
                return {
                    'error': f'获取实例信息失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            data = response.json()
            instance = data.get('instance', {})
            
            # 格式化实例信息用于确认
            instance_info = self._format_instance_for_confirmation(instance)
            
        except Exception as e:
            return {
                'error': f'获取Vultr实例信息时发生错误: {str(e)}',
                'provider': 'vultr'
            }
        
        # 检查是否提供了确认信息
        if not ip_confirmation or not name_confirmation or not operation_confirmation:
            # 转换操作名称
            operation_mapping = {
                'start': 'power_on',
                'halt': 'power_off', 
                'reboot': 'reboot'
            }
            mapped_operation = operation_mapping.get(operation, operation)
            return require_triple_confirmation(instance_info, mapped_operation)
        
        # 验证确认信息
        security = SecurityConfirmation()
        operation_mapping = {
            'start': 'power_on',
            'halt': 'power_off',
            'reboot': 'reboot'
        }
        mapped_operation = operation_mapping.get(operation, operation)
        
        is_valid, error_message = security.validate_power_operation(
            instance_info, mapped_operation, ip_confirmation, name_confirmation, operation_confirmation
        )
        
        if not is_valid:
            return {
                'error': f'确认验证失败: {error_message}',
                'provider': 'vultr',
                'requires_confirmation': True
            }
        
        # 执行实际操作
        try:
            operation_data = {'action': operation}
            response = requests.post(
                f'{self.base_url}/instances/{instance_id}/actions',
                headers=self.headers,
                json=operation_data,
                timeout=10
            )
            
            if response.status_code not in [200, 202, 204]:
                return {
                    'error': f'执行 {operation} 操作失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            return {
                'provider': 'vultr',
                'instance_id': instance_id,
                'operation_success': True,
                'operation': operation,
                'message': f'已成功提交 {operation} 操作',
                'confirmation_validated': True
            }
            
        except Exception as e:
            return {
                'error': f'执行 {operation} 操作时发生错误: {str(e)}',
                'provider': 'vultr'
            }
    
    def get_instance_bandwidth(self, instance_id: str) -> Dict:
        """
        获取实例的带宽使用情况
        
        Args:
            instance_id (str): Vultr实例ID
            
        Returns:
            Dict: 带宽信息或错误信息
        """
        if not self.available:
            return {
                'error': f'Vultr服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'vultr'
            }
        
        try:
            response = requests.get(f'{self.base_url}/instances/{instance_id}/bandwidth', headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'error': f'获取带宽信息失败: {response.status_code} - {response.text}',
                    'provider': 'vultr'
                }
            
            data = response.json()
            
            return {
                'provider': 'vultr',
                'instance_id': instance_id,
                'bandwidth_data': data.get('bandwidth', {})
            }
            
        except Exception as e:
            return {
                'error': f'获取带宽信息时发生错误: {str(e)}',
                'provider': 'vultr'
            }
    
    def _format_instance_info(self, instance: Dict) -> Dict:
        """格式化实例详细信息"""
        return {
            'id': instance.get('id'),
            'label': instance.get('label', '未命名'),
            'hostname': instance.get('hostname'),
            'status': instance.get('status'),
            'power_status': instance.get('power_status'),
            'server_status': instance.get('server_status'),
            'allowed_bandwidth': instance.get('allowed_bandwidth'),
            'netmask_v4': instance.get('netmask_v4'),
            'gateway_v4': instance.get('gateway_v4'),
            'main_ip': instance.get('main_ip'),
            'v6_main_ip': instance.get('v6_main_ip'),
            'ram': instance.get('ram'),
            'disk': instance.get('disk'),
            'vcpu_count': instance.get('vcpu_count'),
            'region': instance.get('region'),
            'plan': instance.get('plan'),
            'os': instance.get('os'),
            'os_id': instance.get('os_id'),
            'app_id': instance.get('app_id'),
            'firewall_group_id': instance.get('firewall_group_id'),
            'features': instance.get('features', []),
            'tags': instance.get('tags', []),
            'internal_ip': instance.get('internal_ip'),
            'kvm': instance.get('kvm'),
            'date_created': instance.get('date_created')
        }
    
    def _format_instance_summary(self, instance: Dict) -> Dict:
        """格式化实例摘要信息"""
        return {
            'id': instance.get('id'),
            'label': instance.get('label', '未命名'),
            'hostname': instance.get('hostname'),
            'status': instance.get('status'),
            'power_status': instance.get('power_status'),
            'main_ip': instance.get('main_ip'),
            'ram': instance.get('ram'),
            'vcpu_count': instance.get('vcpu_count'),
            'region': instance.get('region'),
            'plan': instance.get('plan'),
            'os': instance.get('os'),
            'date_created': instance.get('date_created')
        }
    
    def _format_instance_for_confirmation(self, instance: Dict) -> Dict:
        """格式化实例信息用于确认流程"""
        return {
            'public_ip': instance.get('main_ip', '未知'),
            'name': instance.get('label', instance.get('hostname', '未知')),
            'status': instance.get('status'),
            'instance_id': instance.get('id'),
            'instance_type': instance.get('plan'),
            'tags': instance.get('tags', [])
        }

# 全局实例
vultr_provider = VultrProvider() 