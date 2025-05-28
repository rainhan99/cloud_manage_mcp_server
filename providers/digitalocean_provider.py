#!/usr/bin/env python3
"""
DigitalOcean Droplet 提供商模块
支持查询、开关机、重启操作，带三次确认机制
"""

import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from utils.security import SecurityConfirmation, require_triple_confirmation

# DigitalOcean SDK导入
try:
    from pydo import Client
    DO_AVAILABLE = True
except ImportError:
    DO_AVAILABLE = False
    Client = None

class DigitalOceanProvider:
    """DigitalOcean Droplet 提供商类"""
    
    def __init__(self):
        self.token = os.getenv('DIGITALOCEAN_TOKEN')
        
        if DO_AVAILABLE and self.token:
            try:
                self.client = Client(token=self.token)
                self.available = True
            except Exception as e:
                self.available = False
                self.error = str(e)
        else:
            self.available = False
            self.error = "pydo SDK未安装或DIGITALOCEAN_TOKEN未配置"
    
    def get_droplet_by_ip(self, ip_address: str) -> Dict:
        """
        根据公网IP地址查找Droplet
        
        Args:
            ip_address (str): 公网IP地址
            
        Returns:
            Dict: Droplet信息或错误信息
        """
        if not self.available:
            return {
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        try:
            response = self.client.droplets.list()
            droplets = response.get("droplets", [])
            
            for droplet in droplets:
                networks = droplet.get("networks", {})
                ipv4_networks = networks.get("v4", [])
                
                for network in ipv4_networks:
                    if network.get("type") == "public" and network.get("ip_address") == ip_address:
                        droplet_info = self._format_droplet_info(droplet)
                        return {
                            'provider': 'digitalocean',
                            'found': True,
                            'droplet_info': droplet_info
                        }
            
            return {
                'provider': 'digitalocean',
                'found': False,
                'message': f'未找到使用IP地址 {ip_address} 的Droplet',
                'total_droplets_checked': len(droplets)
            }
            
        except Exception as e:
            return {
                'error': f'查询Droplet时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def get_droplet_by_id(self, droplet_id: int) -> Dict:
        """
        根据Droplet ID查找信息
        
        Args:
            droplet_id (int): Droplet ID
            
        Returns:
            Dict: Droplet信息或错误信息
        """
        if not self.available:
            return {
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        try:
            response = self.client.droplets.get(droplet_id)
            droplet = response.get("droplet", {})
            
            if not droplet:
                return {
                    'provider': 'digitalocean',
                    'found': False,
                    'message': f'未找到ID为 {droplet_id} 的Droplet'
                }
            
            droplet_info = self._format_droplet_info(droplet)
            return {
                'provider': 'digitalocean',
                'found': True,
                'droplet_info': droplet_info
            }
            
        except Exception as e:
            return {
                'error': f'查询Droplet时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def list_droplets(self) -> Dict:
        """
        列出所有Droplets
        
        Returns:
            Dict: Droplets列表或错误信息
        """
        if not self.available:
            return {
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        try:
            response = self.client.droplets.list()
            droplets = response.get("droplets", [])
            
            droplet_list = []
            for droplet in droplets:
                droplet_info = self._format_droplet_summary(droplet)
                droplet_list.append(droplet_info)
            
            return {
                'provider': 'digitalocean',
                'total_droplets': len(droplet_list),
                'droplets': droplet_list
            }
            
        except Exception as e:
            return {
                'error': f'获取Droplets列表时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def get_droplet_monitoring(self, droplet_id: int) -> Dict:
        """
        获取Droplet监控信息
        
        Args:
            droplet_id (int): Droplet ID
            
        Returns:
            Dict: 监控信息或错误信息
        """
        if not self.available:
            return {
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        try:
            # 先检查droplet是否存在和是否启用了监控
            droplet_response = self.client.droplets.get(droplet_id)
            droplet = droplet_response.get("droplet", {})
            
            if not droplet:
                return {
                    'error': f'未找到ID为 {droplet_id} 的Droplet',
                    'provider': 'digitalocean'
                }
            
            features = droplet.get("features", [])
            monitoring_enabled = "monitoring" in features
            
            if not monitoring_enabled:
                return {
                    'provider': 'digitalocean',
                    'droplet_id': droplet_id,
                    'monitoring_enabled': False,
                    'message': '此Droplet未启用监控功能。请在DigitalOcean控制面板中启用监控功能后重试。'
                }
            
            # 获取监控数据（简化版本）
            return {
                'provider': 'digitalocean',
                'droplet_id': droplet_id,
                'monitoring_enabled': True,
                'message': '监控功能已启用，具体数据需要通过DigitalOcean API获取'
            }
            
        except Exception as e:
            return {
                'error': f'获取Droplet监控信息时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def power_on_droplet(
        self, 
        droplet_id: int, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        开启Droplet（需要三次确认）
        
        Args:
            droplet_id (int): Droplet ID
            ip_confirmation (str): IP地址确认
            name_confirmation (str): 名称确认
            operation_confirmation (str): 操作确认
            
        Returns:
            Dict: 操作结果或确认要求
        """
        return self._execute_power_operation(
            droplet_id, 'power_on', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def power_off_droplet(
        self, 
        droplet_id: int, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        强制关闭Droplet（需要三次确认）
        """
        return self._execute_power_operation(
            droplet_id, 'power_off', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def shutdown_droplet(
        self, 
        droplet_id: int, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        优雅关闭Droplet（需要三次确认）
        """
        return self._execute_power_operation(
            droplet_id, 'shutdown', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def reboot_droplet(
        self, 
        droplet_id: int, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        重启Droplet（需要三次确认）
        """
        return self._execute_power_operation(
            droplet_id, 'reboot', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def _execute_power_operation(
        self, 
        droplet_id: int, 
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
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        # 首先获取droplet信息
        try:
            droplet_response = self.client.droplets.get(droplet_id)
            droplet = droplet_response.get("droplet", {})
            
            if not droplet:
                return {
                    'error': f'未找到ID为 {droplet_id} 的Droplet',
                    'provider': 'digitalocean'
                }
            
            # 格式化droplet信息用于确认
            droplet_info = self._format_droplet_for_confirmation(droplet)
            
        except Exception as e:
            return {
                'error': f'获取Droplet信息时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
        
        # 检查是否提供了确认信息
        if not ip_confirmation or not name_confirmation or not operation_confirmation:
            # 返回确认要求
            return require_triple_confirmation(droplet_info, operation)
        
        # 验证确认信息
        security = SecurityConfirmation()
        is_valid, error_message = security.validate_power_operation(
            droplet_info, operation, ip_confirmation, name_confirmation, operation_confirmation
        )
        
        if not is_valid:
            return {
                'error': f'确认验证失败: {error_message}',
                'provider': 'digitalocean',
                'requires_confirmation': True
            }
        
        # 执行实际操作
        try:
            action_data = {"type": operation}
            response = self.client.droplet_actions.post(droplet_id=droplet_id, body=action_data)
            
            action = response.get("action", {})
            
            return {
                'provider': 'digitalocean',
                'droplet_id': droplet_id,
                'operation_success': True,
                'action': {
                    'id': action.get("id"),
                    'status': action.get("status"),
                    'type': action.get("type"),
                    'started_at': action.get("started_at"),
                    'resource_id': action.get("resource_id")
                },
                'message': f'已成功提交 {operation} 操作，操作ID: {action.get("id")}',
                'confirmation_validated': True
            }
            
        except Exception as e:
            return {
                'error': f'执行 {operation} 操作时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def get_droplet_actions(self, droplet_id: int) -> Dict:
        """
        获取Droplet的操作历史
        
        Args:
            droplet_id (int): Droplet ID
            
        Returns:
            Dict: 操作历史或错误信息
        """
        if not self.available:
            return {
                'error': f'DigitalOcean服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'digitalocean'
            }
        
        try:
            response = self.client.droplet_actions.list(droplet_id=droplet_id)
            actions = response.get("actions", [])
            
            action_list = []
            for action in actions:
                action_info = {
                    'id': action.get("id"),
                    'status': action.get("status"),
                    'type': action.get("type"),
                    'started_at': action.get("started_at"),
                    'completed_at': action.get("completed_at"),
                    'resource_id': action.get("resource_id"),
                    'resource_type': action.get("resource_type"),
                    'region': action.get("region", {}).get("name", "未知")
                }
                action_list.append(action_info)
            
            return {
                'provider': 'digitalocean',
                'droplet_id': droplet_id,
                'total_actions': len(action_list),
                'actions': action_list
            }
            
        except Exception as e:
            return {
                'error': f'获取Droplet操作历史时发生错误: {str(e)}',
                'provider': 'digitalocean'
            }
    
    def _format_droplet_info(self, droplet: Dict) -> Dict:
        """格式化Droplet详细信息"""
        networks = droplet.get("networks", {})
        
        # 获取IP地址
        public_ip = None
        private_ip = None
        public_ipv6 = None
        
        for net in networks.get("v4", []):
            if net.get("type") == "public":
                public_ip = net.get("ip_address")
            elif net.get("type") == "private":
                private_ip = net.get("ip_address")
        
        for net in networks.get("v6", []):
            if net.get("type") == "public":
                public_ipv6 = net.get("ip_address")
        
        return {
            'id': droplet.get("id"),
            'name': droplet.get("name"),
            'status': droplet.get("status"),
            'size_slug': droplet.get("size_slug"),
            'memory': droplet.get("memory"),
            'vcpus': droplet.get("vcpus"),
            'disk': droplet.get("disk"),
            'region': droplet.get("region", {}).get("name"),
            'region_slug': droplet.get("region", {}).get("slug"),
            'image': {
                'id': droplet.get("image", {}).get("id"),
                'name': droplet.get("image", {}).get("name"),
                'distribution': droplet.get("image", {}).get("distribution"),
                'slug': droplet.get("image", {}).get("slug")
            },
            'public_ipv4': public_ip,
            'private_ipv4': private_ip,
            'public_ipv6': public_ipv6,
            'features': droplet.get("features", []),
            'tags': droplet.get("tags", []),
            'created_at': droplet.get("created_at"),
            'volume_ids': droplet.get("volume_ids", []),
            'vpc_uuid': droplet.get("vpc_uuid")
        }
    
    def _format_droplet_summary(self, droplet: Dict) -> Dict:
        """格式化Droplet摘要信息"""
        networks = droplet.get("networks", {})
        public_ip = None
        private_ip = None
        
        for net in networks.get("v4", []):
            if net.get("type") == "public":
                public_ip = net.get("ip_address")
            elif net.get("type") == "private":
                private_ip = net.get("ip_address")
        
        return {
            'id': droplet.get("id"),
            'name': droplet.get("name"),
            'status': droplet.get("status"),
            'size_slug': droplet.get("size_slug"),
            'memory': droplet.get("memory"),
            'vcpus': droplet.get("vcpus"),
            'disk': droplet.get("disk"),
            'region': droplet.get("region", {}).get("name"),
            'public_ipv4': public_ip,
            'private_ipv4': private_ip,
            'created_at': droplet.get("created_at"),
            'tags': droplet.get("tags", [])
        }
    
    def _format_droplet_for_confirmation(self, droplet: Dict) -> Dict:
        """格式化Droplet信息用于确认流程"""
        networks = droplet.get("networks", {})
        public_ip = None
        
        for net in networks.get("v4", []):
            if net.get("type") == "public":
                public_ip = net.get("ip_address")
                break
        
        return {
            'public_ip': public_ip or droplet.get('public_ipv4', '未知'),
            'name': droplet.get("name", '未知'),
            'status': droplet.get("status"),
            'instance_id': droplet.get("id"),
            'instance_type': droplet.get("size_slug"),
            'tags': droplet.get("tags", [])
        }

# 全局实例
digitalocean_provider = DigitalOceanProvider() 