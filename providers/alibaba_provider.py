#!/usr/bin/env python3
"""
阿里云ECS 提供商模块
支持查询、开关机、重启操作，带三次确认机制
"""

import os
import json
from typing import Dict, Optional
from utils.security import SecurityConfirmation, require_triple_confirmation

# 阿里云SDK导入
try:
    from alibabacloud_ecs20140526.client import Client as EcsClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ecs20140526 import models as ecs_models
    from alibabacloud_tea_util.client import Client as UtilClient
    ALIBABA_AVAILABLE = True
except ImportError:
    ALIBABA_AVAILABLE = False
    EcsClient = None
    open_api_models = None
    ecs_models = None
    UtilClient = None

class AlibabaProvider:
    """阿里云ECS 提供商类"""
    
    def __init__(self):
        self.access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        self.region_id = os.getenv('ALIBABA_CLOUD_REGION_ID', 'cn-hangzhou')
        
        if ALIBABA_AVAILABLE and self.access_key_id and self.access_key_secret:
            try:
                config = open_api_models.Config(
                    access_key_id=self.access_key_id,
                    access_key_secret=self.access_key_secret,
                    region_id=self.region_id,
                    endpoint=f'ecs.{self.region_id}.aliyuncs.com'
                )
                self.client = EcsClient(config)
                self.available = True
            except Exception as e:
                self.available = False
                self.error = str(e)
        else:
            self.available = False
            self.error = "阿里云SDK未安装或凭证未配置"
    
    def get_instance_by_ip(self, ip_address: str) -> Dict:
        """
        根据公网IP地址查找ECS实例
        
        Args:
            ip_address (str): 公网IP地址
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'阿里云服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'alibaba'
            }
        
        try:
            # 查询所有ECS实例
            request = ecs_models.DescribeInstancesRequest(
                region_id=self.region_id,
                page_size=100
            )
            
            response = self.client.describe_instances(request)
            
            if not response.body.instances:
                return {
                    'provider': 'alibaba',
                    'found': False,
                    'message': f'未找到使用IP地址 {ip_address} 的ECS实例',
                    'searched_region': self.region_id
                }
            
            # 查找匹配的IP地址
            for instance in response.body.instances.instance:
                # 检查公网IP
                public_ips = []
                if hasattr(instance, 'public_ip_address') and instance.public_ip_address:
                    public_ips.extend(instance.public_ip_address.ip_address)
                
                # 检查弹性公网IP
                if hasattr(instance, 'eip_address') and instance.eip_address.ip_address:
                    public_ips.append(instance.eip_address.ip_address)
                
                if ip_address in public_ips:
                    instance_info = self._format_instance_info(instance)
                    return {
                        'provider': 'alibaba',
                        'found': True,
                        'instance_info': instance_info
                    }
            
            return {
                'provider': 'alibaba',
                'found': False,
                'message': f'未找到使用IP地址 {ip_address} 的ECS实例',
                'total_instances_checked': len(response.body.instances.instance)
            }
            
        except Exception as e:
            return {
                'error': f'查询ECS实例时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
    
    def get_instance_by_id(self, instance_id: str) -> Dict:
        """
        根据实例ID查找ECS实例
        
        Args:
            instance_id (str): ECS实例ID
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'阿里云服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'alibaba'
            }
        
        try:
            request = ecs_models.DescribeInstancesRequest(
                region_id=self.region_id,
                instance_ids=json.dumps([instance_id])
            )
            
            response = self.client.describe_instances(request)
            
            if not response.body.instances or not response.body.instances.instance:
                return {
                    'provider': 'alibaba',
                    'found': False,
                    'message': f'未找到ID为 {instance_id} 的ECS实例'
                }
            
            instance = response.body.instances.instance[0]
            instance_info = self._format_instance_info(instance)
            
            return {
                'provider': 'alibaba',
                'found': True,
                'instance_info': instance_info
            }
            
        except Exception as e:
            return {
                'error': f'查询ECS实例时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
    
    def list_instances(self) -> Dict:
        """
        列出所有ECS实例
        
        Returns:
            Dict: 实例列表或错误信息
        """
        if not self.available:
            return {
                'error': f'阿里云服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'alibaba'
            }
        
        try:
            request = ecs_models.DescribeInstancesRequest(
                region_id=self.region_id,
                page_size=100
            )
            
            response = self.client.describe_instances(request)
            
            instance_list = []
            if response.body.instances and response.body.instances.instance:
                for instance in response.body.instances.instance:
                    instance_info = self._format_instance_summary(instance)
                    instance_list.append(instance_info)
            
            return {
                'provider': 'alibaba',
                'region_id': self.region_id,
                'total_instances': len(instance_list),
                'instances': instance_list
            }
            
        except Exception as e:
            return {
                'error': f'列出ECS实例时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
    
    def power_on_instance(
        self, 
        instance_id: str, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        启动ECS实例（需要三次确认）
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
        强制停止ECS实例（需要三次确认）
        """
        return self._execute_power_operation(
            instance_id, 'stop', ip_confirmation, name_confirmation, operation_confirmation
        )
    
    def reboot_instance(
        self, 
        instance_id: str, 
        ip_confirmation: str = "", 
        name_confirmation: str = "", 
        operation_confirmation: str = ""
    ) -> Dict:
        """
        重启ECS实例（需要三次确认）
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
                'error': f'阿里云服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'alibaba'
            }
        
        # 首先获取实例信息
        try:
            request = ecs_models.DescribeInstancesRequest(
                region_id=self.region_id,
                instance_ids=json.dumps([instance_id])
            )
            
            response = self.client.describe_instances(request)
            
            if not response.body.instances or not response.body.instances.instance:
                return {
                    'error': f'未找到ID为 {instance_id} 的ECS实例',
                    'provider': 'alibaba'
                }
            
            instance = response.body.instances.instance[0]
            
            # 格式化实例信息用于确认
            instance_info = self._format_instance_for_confirmation(instance)
            
        except Exception as e:
            return {
                'error': f'获取ECS实例信息时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
        
        # 检查是否提供了确认信息
        if not ip_confirmation or not name_confirmation or not operation_confirmation:
            # 转换操作名称
            operation_mapping = {
                'start': 'power_on',
                'stop': 'power_off',
                'reboot': 'reboot'
            }
            mapped_operation = operation_mapping.get(operation, operation)
            return require_triple_confirmation(instance_info, mapped_operation)
        
        # 验证确认信息
        security = SecurityConfirmation()
        operation_mapping = {
            'start': 'power_on',
            'stop': 'power_off',
            'reboot': 'reboot'
        }
        mapped_operation = operation_mapping.get(operation, operation)
        
        is_valid, error_message = security.validate_power_operation(
            instance_info, mapped_operation, ip_confirmation, name_confirmation, operation_confirmation
        )
        
        if not is_valid:
            return {
                'error': f'确认验证失败: {error_message}',
                'provider': 'alibaba',
                'requires_confirmation': True
            }
        
        # 执行实际操作
        try:
            if operation == 'start':
                request = ecs_models.StartInstanceRequest(
                    instance_id=instance_id
                )
                response = self.client.start_instance(request)
            elif operation == 'stop':
                request = ecs_models.StopInstanceRequest(
                    instance_id=instance_id,
                    force_stop=True
                )
                response = self.client.stop_instance(request)
            elif operation == 'reboot':
                request = ecs_models.RebootInstanceRequest(
                    instance_id=instance_id,
                    force_stop=True
                )
                response = self.client.reboot_instance(request)
            else:
                return {
                    'error': f'不支持的操作类型: {operation}',
                    'provider': 'alibaba'
                }
            
            return {
                'provider': 'alibaba',
                'instance_id': instance_id,
                'operation_success': True,
                'operation': operation,
                'request_id': response.body.request_id,
                'message': f'已成功提交 {operation} 操作',
                'confirmation_validated': True
            }
            
        except Exception as e:
            return {
                'error': f'执行 {operation} 操作时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
    
    def get_instance_monitoring(self, instance_id: str) -> Dict:
        """
        获取ECS实例的监控信息
        
        Args:
            instance_id (str): ECS实例ID
            
        Returns:
            Dict: 监控信息或错误信息
        """
        if not self.available:
            return {
                'error': f'阿里云服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'alibaba'
            }
        
        try:
            # 这里简化实现，实际需要调用云监控API
            request = ecs_models.DescribeInstancesRequest(
                region_id=self.region_id,
                instance_ids=json.dumps([instance_id])
            )
            
            response = self.client.describe_instances(request)
            
            if not response.body.instances or not response.body.instances.instance:
                return {
                    'error': f'未找到ID为 {instance_id} 的ECS实例',
                    'provider': 'alibaba'
                }
            
            return {
                'provider': 'alibaba',
                'instance_id': instance_id,
                'monitoring_available': True,
                'message': '监控功能可用，具体数据需要通过云监控API获取'
            }
            
        except Exception as e:
            return {
                'error': f'获取监控信息时发生错误: {str(e)}',
                'provider': 'alibaba'
            }
    
    def _format_instance_info(self, instance) -> Dict:
        """格式化实例详细信息"""
        # 获取公网IP
        public_ips = []
        if hasattr(instance, 'public_ip_address') and instance.public_ip_address:
            public_ips.extend(instance.public_ip_address.ip_address)
        
        # 获取弹性公网IP
        eip_address = None
        if hasattr(instance, 'eip_address') and instance.eip_address.ip_address:
            eip_address = instance.eip_address.ip_address
            public_ips.append(eip_address)
        
        # 获取私网IP
        private_ips = []
        if hasattr(instance, 'vpc_attributes') and instance.vpc_attributes.private_ip_address:
            private_ips.extend(instance.vpc_attributes.private_ip_address.ip_address)
        elif hasattr(instance, 'inner_ip_address') and instance.inner_ip_address:
            private_ips.extend(instance.inner_ip_address.ip_address)
        
        # 获取标签
        tags = {}
        if hasattr(instance, 'tags') and instance.tags.tag:
            for tag in instance.tags.tag:
                tags[tag.tag_key] = tag.tag_value
        
        # 获取安全组
        security_groups = []
        if hasattr(instance, 'security_group_ids') and instance.security_group_ids.security_group_id:
            security_groups = instance.security_group_ids.security_group_id
        
        return {
            'instance_id': instance.instance_id,
            'name': instance.instance_name,
            'hostname': getattr(instance, 'hostname', ''),
            'status': instance.status,
            'instance_type': instance.instance_type,
            'image_id': instance.image_id,
            'region_id': instance.region_id,
            'zone_id': instance.zone_id,
            'cpu': instance.cpu,
            'memory': instance.memory,
            'public_ips': public_ips,
            'private_ips': private_ips,
            'eip_address': eip_address,
            'creation_time': instance.creation_time,
            'start_time': getattr(instance, 'start_time', ''),
            'expired_time': getattr(instance, 'expired_time', ''),
            'os_name': getattr(instance, 'osname', ''),
            'os_type': getattr(instance, 'ostype', ''),
            'instance_charge_type': instance.instance_charge_type,
            'internet_charge_type': getattr(instance, 'internet_charge_type', ''),
            'internet_max_bandwidth_in': getattr(instance, 'internet_max_bandwidth_in', 0),
            'internet_max_bandwidth_out': getattr(instance, 'internet_max_bandwidth_out', 0),
            'vpc_id': getattr(instance, 'vpc_id', ''),
            'vswitch_id': getattr(instance, 'vswitch_id', ''),
            'security_group_ids': security_groups,
            'tags': tags
        }
    
    def _format_instance_summary(self, instance) -> Dict:
        """格式化实例摘要信息"""
        # 获取主要公网IP
        primary_public_ip = None
        if hasattr(instance, 'eip_address') and instance.eip_address.ip_address:
            primary_public_ip = instance.eip_address.ip_address
        elif hasattr(instance, 'public_ip_address') and instance.public_ip_address:
            if instance.public_ip_address.ip_address:
                primary_public_ip = instance.public_ip_address.ip_address[0]
        
        # 获取主要私网IP
        primary_private_ip = None
        if hasattr(instance, 'vpc_attributes') and instance.vpc_attributes.private_ip_address:
            if instance.vpc_attributes.private_ip_address.ip_address:
                primary_private_ip = instance.vpc_attributes.private_ip_address.ip_address[0]
        elif hasattr(instance, 'inner_ip_address') and instance.inner_ip_address:
            if instance.inner_ip_address.ip_address:
                primary_private_ip = instance.inner_ip_address.ip_address[0]
        
        return {
            'instance_id': instance.instance_id,
            'name': instance.instance_name,
            'status': instance.status,
            'instance_type': instance.instance_type,
            'region_id': instance.region_id,
            'zone_id': instance.zone_id,
            'cpu': instance.cpu,
            'memory': instance.memory,
            'public_ip': primary_public_ip,
            'private_ip': primary_private_ip,
            'creation_time': instance.creation_time,
            'os_name': getattr(instance, 'osname', ''),
            'instance_charge_type': instance.instance_charge_type
        }
    
    def _format_instance_for_confirmation(self, instance) -> Dict:
        """格式化实例信息用于确认流程"""
        # 获取主要公网IP
        primary_public_ip = None
        if hasattr(instance, 'eip_address') and instance.eip_address.ip_address:
            primary_public_ip = instance.eip_address.ip_address
        elif hasattr(instance, 'public_ip_address') and instance.public_ip_address:
            if instance.public_ip_address.ip_address:
                primary_public_ip = instance.public_ip_address.ip_address[0]
        
        # 获取标签
        tags = []
        if hasattr(instance, 'tags') and instance.tags.tag:
            for tag in instance.tags.tag:
                tags.append(f"{tag.tag_key}:{tag.tag_value}")
        
        return {
            'public_ip': primary_public_ip or '未知',
            'name': instance.instance_name or '未知',
            'status': instance.status,
            'instance_id': instance.instance_id,
            'instance_type': instance.instance_type,
            'tags': tags
        }

# 全局实例
alibaba_provider = AlibabaProvider() 