# Multi-Cloud Manager MCP Service

## 📋 服务概述

**服务名称**: `multi-cloud-manager`  
**版本**: `2.0.0`  
**协议**: MCP (Model Context Protocol)  
**描述**: 基于 MCP 的智能多云服务器管理系统，支持 AWS、DigitalOcean、Vultr、阿里云四大主流云服务平台的统一管理

## 🌐 支持的云平台

| 平台         | 功能权限      | 支持操作                         |
| ------------ | ------------- | -------------------------------- |
| AWS EC2      | 只读查询      | 实例查询、存储信息、监控数据     |
| DigitalOcean | 查询+电源管理 | 实例查询、开关机、重启、监控     |
| Vultr        | 查询+电源管理 | 实例查询、开关机、重启、带宽监控 |
| 阿里云 ECS   | 查询+电源管理 | 实例查询、开关机、重启、监控     |

## 🛠️ 可用工具 (Tools)

### 通用工具

#### `get_instance_info`

**描述**: 根据 IP 地址自动检测云服务提供商并获取实例信息  
**参数**:

- `ip_address` (string): 公网 IP 地址

**返回**: 实例详细信息，包含提供商信息和实例配置

#### `get_supported_providers`

**描述**: 获取支持的云服务提供商列表  
**参数**: 无  
**返回**: 支持的云服务提供商信息和状态

#### `get_system_status`

**描述**: 获取整个系统的状态概览  
**参数**: 无  
**返回**: 系统状态、可用提供商数量、安全特性等

#### `check_provider_availability`

**描述**: 检查特定云服务提供商的可用性  
**参数**:

- `provider_name` (string): 提供商名称 ('aws', 'digitalocean', 'vultr', 'alibaba')

**返回**: 提供商可用性状态和环境变量检查结果

### AWS EC2 工具

#### `get_aws_instance_info`

**描述**: 获取 AWS EC2 实例信息（只读）  
**参数**:

- `ip_address_or_id` (string): 公网 IP 地址或实例 ID

#### `get_aws_instance_storage_info`

**描述**: 获取 AWS EC2 实例的存储详细信息  
**参数**:

- `instance_id` (string): EC2 实例 ID

**返回**: 存储信息，包括磁盘类型、IOPS、吞吐量等

#### `get_aws_instance_monitoring`

**描述**: 获取 AWS EC2 实例的监控数据  
**参数**:

- `instance_id` (string): EC2 实例 ID
- `hours` (integer, optional): 获取过去多少小时的数据，默认 1 小时

#### `list_aws_instances`

**描述**: 列出所有 AWS EC2 实例  
**参数**: 无

### DigitalOcean 工具

#### `get_digitalocean_droplet_info`

**描述**: 获取 DigitalOcean Droplet 信息  
**参数**:

- `ip_address_or_id` (string): 公网 IP 地址或 Droplet ID

#### `power_on_digitalocean_droplet`

**描述**: 开启 DigitalOcean Droplet（需要三次确认）  
**参数**:

- `droplet_id` (integer): Droplet ID
- `ip_confirmation` (string): 确认 IP 地址
- `name_confirmation` (string): 确认 Droplet 名称
- `operation_confirmation` (string): 确认操作类型

#### `power_off_digitalocean_droplet`

**描述**: 强制关闭 DigitalOcean Droplet（需要三次确认）  
**参数**: 同 `power_on_digitalocean_droplet`

#### `shutdown_digitalocean_droplet`

**描述**: 优雅关闭 DigitalOcean Droplet（需要三次确认）  
**参数**: 同 `power_on_digitalocean_droplet`

#### `reboot_digitalocean_droplet`

**描述**: 重启 DigitalOcean Droplet（需要三次确认）  
**参数**: 同 `power_on_digitalocean_droplet`

#### `list_digitalocean_droplets`

**描述**: 列出所有 DigitalOcean Droplets  
**参数**: 无

#### `get_digitalocean_droplet_monitoring`

**描述**: 获取 DigitalOcean Droplet 监控信息  
**参数**:

- `droplet_id` (integer): Droplet ID

#### `get_digitalocean_droplet_actions`

**描述**: 获取 DigitalOcean Droplet 操作历史  
**参数**:

- `droplet_id` (integer): Droplet ID

### Vultr 工具

#### `get_vultr_instance_info`

**描述**: 获取 Vultr 实例信息  
**参数**:

- `ip_address_or_id` (string): 公网 IP 地址或实例 ID

#### `power_on_vultr_instance`

**描述**: 开启 Vultr 实例（需要三次确认）  
**参数**:

- `instance_id` (string): Vultr 实例 ID
- `ip_confirmation` (string): 确认 IP 地址
- `name_confirmation` (string): 确认实例名称
- `operation_confirmation` (string): 确认操作类型

#### `power_off_vultr_instance`

**描述**: 强制关闭 Vultr 实例（需要三次确认）  
**参数**: 同 `power_on_vultr_instance`

#### `reboot_vultr_instance`

**描述**: 重启 Vultr 实例（需要三次确认）  
**参数**: 同 `power_on_vultr_instance`

#### `list_vultr_instances`

**描述**: 列出所有 Vultr 实例  
**参数**: 无

#### `get_vultr_instance_bandwidth`

**描述**: 获取 Vultr 实例带宽使用情况  
**参数**:

- `instance_id` (string): Vultr 实例 ID

### 阿里云 ECS 工具

#### `get_alibaba_instance_info`

**描述**: 获取阿里云 ECS 实例信息  
**参数**:

- `ip_address_or_id` (string): 公网 IP 地址或实例 ID

#### `power_on_alibaba_instance`

**描述**: 启动阿里云 ECS 实例（需要三次确认）  
**参数**:

- `instance_id` (string): ECS 实例 ID
- `ip_confirmation` (string): 确认 IP 地址
- `name_confirmation` (string): 确认实例名称
- `operation_confirmation` (string): 确认操作类型

#### `power_off_alibaba_instance`

**描述**: 强制停止阿里云 ECS 实例（需要三次确认）  
**参数**: 同 `power_on_alibaba_instance`

#### `reboot_alibaba_instance`

**描述**: 重启阿里云 ECS 实例（需要三次确认）  
**参数**: 同 `power_on_alibaba_instance`

#### `list_alibaba_instances`

**描述**: 列出所有阿里云 ECS 实例  
**参数**: 无

#### `get_alibaba_instance_monitoring`

**描述**: 获取阿里云 ECS 实例监控信息  
**参数**:

- `instance_id` (string): ECS 实例 ID

## 🔧 环境配置要求

### 必需环境变量

#### AWS 配置

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

#### DigitalOcean 配置

```bash
DIGITALOCEAN_TOKEN=your_digitalocean_token
```

#### Vultr 配置

```bash
VULTR_API_KEY=your_vultr_api_key
```

#### 阿里云配置

```bash
ALIBABA_CLOUD_ACCESS_KEY_ID=your_alibaba_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_alibaba_access_key_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

### 可选环境变量

#### IP 检测服务

```bash
IPINFO_API_TOKEN=your_ipinfo_token
```

## 🛡️ 安全特性

### 三重确认机制

所有电源操作（开关机、重启）都需要三次确认：

1. **IP 地址确认**: 输入目标服务器的准确 IP 地址
2. **名称确认**: 输入服务器的准确名称
3. **操作确认**: 输入准确的操作类型

### 权限限制

- **AWS**: 仅提供只读查询功能，确保安全
- **其他平台**: 支持查询和电源管理，但完全禁用删除操作
- **删除保护**: 所有平台都不允许删除操作

### 智能安全检查

- 实例状态验证
- 生产环境标签检测
- 大型实例操作警告
- 确认信息验证

## 📋 MCP 客户端配置

### Claude Desktop 配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "multi-cloud-manager": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/cloud_manage_mcp_server",
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret",
        "DIGITALOCEAN_TOKEN": "your_token",
        "VULTR_API_KEY": "your_key",
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "your_key",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "your_secret"
      }
    }
  }
}
```

### 通用 MCP 客户端配置

```json
{
  "name": "multi-cloud-manager",
  "command": ["uv", "run", "python", "main.py"],
  "args": [],
  "env": {
    "环境变量": "值"
  }
}
```

## 📝 使用示例

### 基础查询

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_instance_info",
    "arguments": {
      "ip_address": "1.2.3.4"
    }
  }
}
```

### AWS 存储查询

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_aws_instance_storage_info",
    "arguments": {
      "instance_id": "i-1234567890abcdef0"
    }
  }
}
```

### 安全重启操作

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "reboot_digitalocean_droplet",
    "arguments": {
      "droplet_id": 123456,
      "ip_confirmation": "192.168.1.100",
      "name_confirmation": "web-server-01",
      "operation_confirmation": "重启"
    }
  }
}
```

## 🚀 启动和部署

### 本地开发

```bash
# 安装依赖
uv sync

# 配置环境变量
cp config.env.example .env
# 编辑 .env 文件

# 启动服务
uv run python main.py
```

### 生产部署

```bash
# 安装生产依赖
uv sync --no-dev

# 设置环境变量
export AWS_ACCESS_KEY_ID=xxx
export DIGITALOCEAN_TOKEN=xxx

# 启动服务
uv run python main.py
```

## 📊 服务能力

### 支持的功能

- ✅ 多云平台统一管理
- ✅ 智能 IP 检测和路由
- ✅ 三重确认安全机制
- ✅ 实时状态监控
- ✅ 详细配置查询
- ✅ 电源管理操作
- ✅ 历史操作记录

### 限制和约束

- ❌ 不支持实例创建/删除
- ❌ 不支持网络配置修改
- ❌ 不支持安全组管理
- ⚠️ 需要相应的 API 权限
- ⚠️ 电源操作需要三次确认

## 🔍 故障排除

### 常见错误码

- `PROVIDER_NOT_AVAILABLE`: 云服务提供商不可用
- `INVALID_CREDENTIALS`: API 凭证无效
- `CONFIRMATION_FAILED`: 三次确认验证失败
- `RESOURCE_NOT_FOUND`: 资源未找到
- `OPERATION_NOT_SUPPORTED`: 操作不支持

### 诊断命令

```bash
# 检查系统状态
uv run python -c "from main import get_system_status; print(get_system_status())"

# 检查特定提供商
uv run python -c "from main import check_provider_availability; print(check_provider_availability('aws'))"
```

## 📞 支持和贡献

- **GitHub**: https://github.com/rainhan99/cloud_manage_mcp_server
- **Issues**: https://github.com/rainhan99/cloud_manage_mcp_server/issues
- **文档**: README_NEW.md
- **许可证**: MIT

---

**版本**: 2.0.0  
**最后更新**: 2024 年  
**MCP 协议版本**: 2024-11-05
