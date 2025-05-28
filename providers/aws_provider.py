#!/usr/bin/env python3
"""
AWS EC2 提供商模块
只提供查询功能，不允许进行任何操作
"""

import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta

# AWS SDK导入
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception

class AWSProvider:
    """AWS EC2 提供商类"""
    
    def __init__(self):
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.session_token = os.getenv('AWS_SESSION_TOKEN')
        
        if AWS_AVAILABLE and self.access_key and self.secret_key:
            try:
                session_kwargs = {
                    'aws_access_key_id': self.access_key,
                    'aws_secret_access_key': self.secret_key,
                    'region_name': self.region
                }
                if self.session_token:
                    session_kwargs['aws_session_token'] = self.session_token
                
                self.session = boto3.Session(**session_kwargs)
                self.ec2 = self.session.client('ec2')
                self.cloudwatch = self.session.client('cloudwatch')
                self.available = True
            except Exception as e:
                self.available = False
                self.error = str(e)
        else:
            self.available = False
            self.error = "AWS SDK未安装或凭证未配置"
    
    def get_instance_by_ip(self, ip_address: str) -> Dict:
        """
        根据公网IP地址查找EC2实例
        
        Args:
            ip_address (str): 公网IP地址
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'AWS服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'aws'
            }
        
        try:
            # 查找具有指定公网IP的实例
            response = self.ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'ip-address',
                        'Values': [ip_address]
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': ['pending', 'running', 'shutting-down', 'terminated', 'stopping', 'stopped']
                    }
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(instance)
            
            if not instances:
                return {
                    'provider': 'aws',
                    'found': False,
                    'message': f'未找到使用IP地址 {ip_address} 的EC2实例',
                    'searched_region': self.region
                }
            
            # 获取第一个匹配的实例的详细信息
            instance = instances[0]
            instance_info = self._format_instance_info(instance)
            
            return {
                'provider': 'aws',
                'found': True,
                'instance_info': instance_info
            }
            
        except ClientError as e:
            return {
                'error': f'AWS API调用失败: {str(e)}',
                'provider': 'aws'
            }
        except Exception as e:
            return {
                'error': f'查询EC2实例时发生错误: {str(e)}',
                'provider': 'aws'
            }
    
    def get_instance_by_id(self, instance_id: str) -> Dict:
        """
        根据实例ID查找EC2实例
        
        Args:
            instance_id (str): EC2实例ID
            
        Returns:
            Dict: 实例信息或错误信息
        """
        if not self.available:
            return {
                'error': f'AWS服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'aws'
            }
        
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            
            if not response['Reservations']:
                return {
                    'provider': 'aws',
                    'found': False,
                    'message': f'未找到ID为 {instance_id} 的EC2实例'
                }
            
            instance = response['Reservations'][0]['Instances'][0]
            instance_info = self._format_instance_info(instance)
            
            return {
                'provider': 'aws',
                'found': True,
                'instance_info': instance_info
            }
            
        except ClientError as e:
            return {
                'error': f'AWS API调用失败: {str(e)}',
                'provider': 'aws'
            }
        except Exception as e:
            return {
                'error': f'查询EC2实例时发生错误: {str(e)}',
                'provider': 'aws'
            }
    
    def list_instances(self) -> Dict:
        """
        列出所有EC2实例
        
        Returns:
            Dict: 实例列表或错误信息
        """
        if not self.available:
            return {
                'error': f'AWS服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'aws'
            }
        
        try:
            response = self.ec2.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = self._format_instance_summary(instance)
                    instances.append(instance_info)
            
            return {
                'provider': 'aws',
                'region': self.region,
                'total_instances': len(instances),
                'instances': instances
            }
            
        except ClientError as e:
            return {
                'error': f'AWS API调用失败: {str(e)}',
                'provider': 'aws'
            }
        except Exception as e:
            return {
                'error': f'列出EC2实例时发生错误: {str(e)}',
                'provider': 'aws'
            }
    
    def get_instance_storage_info(self, instance_id: str) -> Dict:
        """
        获取实例的存储详细信息
        
        Args:
            instance_id (str): EC2实例ID
            
        Returns:
            Dict: 存储信息或错误信息
        """
        if not self.available:
            return {
                'error': f'AWS服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'aws'
            }
        
        try:
            # 获取实例信息
            instance_response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if not instance_response['Reservations']:
                return {
                    'error': f'未找到ID为 {instance_id} 的EC2实例',
                    'provider': 'aws'
                }
            
            instance = instance_response['Reservations'][0]['Instances'][0]
            
            # 获取卷信息
            storage_info = []
            
            for block_device in instance.get('BlockDeviceMappings', []):
                volume_id = block_device.get('Ebs', {}).get('VolumeId')
                if volume_id:
                    volume_response = self.ec2.describe_volumes(VolumeIds=[volume_id])
                    if volume_response['Volumes']:
                        volume = volume_response['Volumes'][0]
                        
                        # 获取IOPS和吞吐量信息
                        iops = volume.get('Iops', 'N/A')
                        throughput = volume.get('Throughput', 'N/A')
                        
                        storage_info.append({
                            'device_name': block_device.get('DeviceName'),
                            'volume_id': volume_id,
                            'volume_type': volume.get('VolumeType'),
                            'size': volume.get('Size'),
                            'iops': iops,
                            'throughput': throughput,
                            'encrypted': volume.get('Encrypted', False),
                            'state': volume.get('State'),
                            'created_time': volume.get('CreateTime').isoformat() if volume.get('CreateTime') else None
                        })
            
            return {
                'provider': 'aws',
                'instance_id': instance_id,
                'storage_devices': storage_info,
                'total_devices': len(storage_info)
            }
            
        except ClientError as e:
            return {
                'error': f'AWS API调用失败: {str(e)}',
                'provider': 'aws'
            }
        except Exception as e:
            return {
                'error': f'获取存储信息时发生错误: {str(e)}',
                'provider': 'aws'
            }
    
    def get_instance_monitoring_data(self, instance_id: str, hours: int = 1) -> Dict:
        """
        获取实例的监控数据
        
        Args:
            instance_id (str): EC2实例ID
            hours (int): 获取过去多少小时的数据
            
        Returns:
            Dict: 监控数据或错误信息
        """
        if not self.available:
            return {
                'error': f'AWS服务不可用: {getattr(self, "error", "未知错误")}',
                'provider': 'aws'
            }
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            metrics = ['CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadOps', 'DiskWriteOps']
            monitoring_data = {}
            
            for metric in metrics:
                try:
                    response = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName=metric,
                        Dimensions=[
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            }
                        ],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=300,  # 5分钟
                        Statistics=['Average', 'Maximum']
                    )
                    
                    monitoring_data[metric] = {
                        'datapoints': len(response['Datapoints']),
                        'data': response['Datapoints']
                    }
                except Exception as e:
                    monitoring_data[metric] = {
                        'error': str(e),
                        'datapoints': 0
                    }
            
            return {
                'provider': 'aws',
                'instance_id': instance_id,
                'time_range': f'{hours}小时',
                'metrics': monitoring_data
            }
            
        except ClientError as e:
            return {
                'error': f'AWS API调用失败: {str(e)}',
                'provider': 'aws'
            }
        except Exception as e:
            return {
                'error': f'获取监控数据时发生错误: {str(e)}',
                'provider': 'aws'
            }
    
    def _format_instance_info(self, instance: Dict) -> Dict:
        """格式化实例详细信息"""
        # 获取名称标签
        name = '未命名'
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
        
        # 格式化网络信息
        public_ip = instance.get('PublicIpAddress')
        private_ip = instance.get('PrivateIpAddress')
        
        # 格式化安全组
        security_groups = [sg['GroupName'] for sg in instance.get('SecurityGroups', [])]
        
        # 格式化标签
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        
        return {
            'instance_id': instance.get('InstanceId'),
            'name': name,
            'instance_type': instance.get('InstanceType'),
            'state': instance.get('State', {}).get('Name'),
            'public_ip': public_ip,
            'private_ip': private_ip,
            'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
            'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
            'platform': instance.get('Platform', 'Linux/UNIX'),
            'architecture': instance.get('Architecture'),
            'virtualization_type': instance.get('VirtualizationType'),
            'root_device_type': instance.get('RootDeviceType'),
            'security_groups': security_groups,
            'subnet_id': instance.get('SubnetId'),
            'vpc_id': instance.get('VpcId'),
            'tags': tags,
            'monitoring_state': instance.get('Monitoring', {}).get('State'),
            'ebs_optimized': instance.get('EbsOptimized', False)
        }
    
    def _format_instance_summary(self, instance: Dict) -> Dict:
        """格式化实例摘要信息"""
        # 获取名称标签
        name = '未命名'
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
        
        return {
            'instance_id': instance.get('InstanceId'),
            'name': name,
            'instance_type': instance.get('InstanceType'),
            'state': instance.get('State', {}).get('Name'),
            'public_ip': instance.get('PublicIpAddress'),
            'private_ip': instance.get('PrivateIpAddress'),
            'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
            'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None
        }

# 全局实例
aws_provider = AWSProvider() 