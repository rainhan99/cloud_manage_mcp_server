# Cloud Manage MCP Server

这是一个基于 MCP (Model Context Protocol) 的云管理服务器，支持通过公网 IP 地址获取云服务器信息。

## 功能特性

- 支持通过公网 IP 地址识别云服务提供商
- 使用 pydo SDK 获取 DigitalOcean droplet 详细信息
- **Droplet 电源管理**: 开机、关机、重启、优雅关机
- **状态监控**: 获取 droplet 当前状态和资源使用情况
- **操作历史**: 查看 droplet 操作历史记录
- **批量管理**: 列出所有 droplets，按名称查找
- **监控数据**: 获取 CPU、内存、磁盘、网络使用率（需启用监控）
- **删除保护**: 多重安全机制防止意外删除重要服务器
- 支持 AWS（待实现）

## 安全特性

### 🛡️ 删除保护机制

为了防止意外删除重要的 droplet，本系统实现了严格的五层安全保护：

#### 保护层级

1. **全局开关保护**: 默认禁用所有删除操作
2. **确认码保护**: 需要特定确认码才能尝试删除
3. **状态检查保护**: 禁止删除运行中的 droplet
4. **标签保护**: 自动识别并保护重要 droplet
5. **最终安全检查**: 即使通过前面检查，实际删除仍被禁用

#### 保护标签

系统会自动保护带有以下标签的 droplet：

- `production` / `prod`
- `important`
- `critical`
- `backup`

#### 配置方法

```bash
# 默认情况下，删除功能完全禁用
# 如需启用（强烈不推荐），设置环境变量：
export ALLOW_DROPLET_DELETION=true
```

**⚠️ 重要提醒**: 即使启用删除功能，所有实际删除操作仍会被最终安全检查阻止。建议始终通过 DigitalOcean 控制面板手动删除 droplet。

## 可用的 MCP 工具函数

### 基础查询功能

#### `get_dg_info(ipv4_address: str)`

根据公网 IP 地址获取对应的 DigitalOcean droplet 信息。

**参数:**

- `ipv4_address` (str): 要查询的公网 IP 地址

#### `list_droplets()`

列出账户下所有的 DigitalOcean droplets。

#### `find_droplet_by_name(name: str)`

根据名称查找 DigitalOcean droplet（支持模糊匹配）。

**参数:**

- `name` (str): droplet 名称或部分名称

#### `get_droplet_status(droplet_id: int)`

获取指定 droplet 的当前状态和详细信息。

**参数:**

- `droplet_id` (int): droplet ID

### 电源管理功能

#### `power_on_droplet(droplet_id: int)`

开启指定的 droplet。

#### `power_off_droplet(droplet_id: int)`

强制关闭指定的 droplet（类似拔电源）。

#### `shutdown_droplet(droplet_id: int)`

优雅关闭指定的 droplet（类似系统关机命令）。

#### `reboot_droplet(droplet_id: int)`

重启指定的 droplet。

**参数:**

- `droplet_id` (int): 要操作的 droplet ID

### 监控和历史功能

#### `get_droplet_monitoring(droplet_id: int)`

获取 droplet 的监控数据，包括 CPU、内存、磁盘、网络使用率。

**注意**: 需要在 droplet 上启用监控功能。

#### `get_droplet_actions(droplet_id: int)`

获取指定 droplet 的操作历史记录。

#### `get_action_status(action_id: int)`

查询特定操作的状态（在执行电源操作后可用于跟踪进度）。

**参数:**

- `droplet_id` (int): droplet ID
- `action_id` (int): 操作 ID

### 删除保护功能

#### `delete_droplet_with_protection(droplet_id: int, confirmation_code: str = "")`

删除 DigitalOcean droplet（带严格安全保护）。

**注意**: 此功能具有多重安全限制，实际上被设计为阻止删除操作。

**参数:**

- `droplet_id` (int): 要删除的 droplet ID
- `confirmation_code` (str): 确认码（必须为 "CONFIRM_DELETE_DROPLET"）

#### `get_droplet_deletion_policy()`

获取当前的删除策略和安全配置信息。

#### `check_droplet_deletion_safety(droplet_id: int)`

检查指定 droplet 的删除安全性（不实际删除）。

**参数:**

- `droplet_id` (int): 要检查的 droplet ID

## 使用示例

### 基本操作示例

```python
# 列出所有 droplets
result = list_droplets()
print(f"总共有 {result['total_droplets']} 个 droplets")

# 查找特定名称的 droplet
result = find_droplet_by_name("web-server")
if result['found']:
    droplet = result['droplets'][0]
    droplet_id = droplet['id']

    # 获取详细状态
    status = get_droplet_status(droplet_id)
    print(f"Droplet 状态: {status['status']}")

    # 重启 droplet
    if status['status'] == 'active':
        action_result = reboot_droplet(droplet_id)
        action_id = action_result['action']['id']

        # 检查操作状态
        action_status = get_action_status(action_id)
        print(f"重启操作状态: {action_status['action']['status']}")
```

### 删除安全性检查示例

```python
# 检查删除策略
policy = get_droplet_deletion_policy()
print(f"删除功能状态: {policy['deletion_policy']['current_status']}")

# 检查特定 droplet 的删除安全性
safety_check = check_droplet_deletion_safety(droplet_id)
print(f"安全等级: {safety_check['safety_level']}")

# 查看安全检查详情
for check in safety_check['safety_checks']:
    print(f"{check['check']}: {check['status']} - {check['message']}")

# 尝试删除（会被安全机制阻止）
deletion_result = delete_droplet_with_protection(droplet_id, "CONFIRM_DELETE_DROPLET")
if deletion_result.get('error'):
    print(f"删除被阻止: {deletion_result['error']}")
```

### 监控数据获取示例

```python
# 获取监控数据
monitoring_result = get_droplet_monitoring(droplet_id)
if monitoring_result['monitoring_enabled']:
    metrics = monitoring_result['metrics']

    for metric_type, data in metrics.items():
        if data['available']:
            print(f"{metric_type} 监控数据可用")
        else:
            print(f"{metric_type} 暂无数据")
else:
    print("请先在 DigitalOcean 控制面板中启用监控功能")
```

## 返回值说明

### 成功响应示例

#### 删除安全性检查

```python
{
    "cloud_provider": "digitalocean",
    "droplet_id": 123456789,
    "droplet_name": "web-server-01",
    "overall_safety": "BLOCKED",
    "safety_level": "删除被阻止",
    "safety_checks": [
        {
            "check": "全局删除策略",
            "status": "BLOCKED",
            "message": "删除功能已被全局禁用"
        },
        {
            "check": "droplet状态",
            "status": "WARNING",
            "message": "droplet正在运行 (active)，建议先关机"
        },
        {
            "check": "保护标签",
            "status": "BLOCKED",
            "message": "发现保护标签: production"
        }
    ],
    "warnings": [
        "此droplet带有保护标签，表明它可能是重要服务器"
    ],
    "summary": {
        "total_checks": 5,
        "blocked": 2,
        "warnings": 1,
        "passed": 2
    }
}
```

#### 删除策略信息

```python
{
    "cloud_provider": "digitalocean",
    "deletion_policy": {
        "enabled": false,
        "protection_level": "MAXIMUM",
        "current_status": "所有删除操作被禁用",
        "safety_checks": [
            "环境变量 ALLOW_DROPLET_DELETION 必须设置为 true",
            "必须提供正确的确认码 'CONFIRM_DELETE_DROPLET'",
            "droplet 必须处于关机状态",
            "droplet 不能带有保护标签",
            "多重确认机制"
        ],
        "protected_tags": ["production", "prod", "important", "critical", "backup"]
    },
    "security_info": {
        "philosophy": "安全第一，防止意外删除重要服务器",
        "recommendation": "强烈建议通过DigitalOcean控制面板手动删除droplet"
    }
}
```

#### droplet 操作成功

```python
{
    "cloud_provider": "digitalocean",
    "droplet_id": 123456789,
    "action": {
        "id": 987654321,
        "status": "in-progress",
        "type": "reboot",
        "started_at": "2024-01-01T12:00:00Z",
        "completed_at": null,
        "resource_id": 123456789,
        "resource_type": "droplet",
        "region": "New York 3"
    },
    "message": "已成功提交 reboot 操作，操作ID: 987654321"
}
```

#### droplet 状态查询

```python
{
    "cloud_provider": "digitalocean",
    "droplet_id": 123456789,
    "status": "active",
    "name": "web-server-01",
    "locked": false,
    "size_slug": "s-1vcpu-1gb",
    "memory": 1024,
    "vcpus": 1,
    "disk": 25,
    "region": {
        "name": "New York 3",
        "slug": "nyc3"
    },
    "image": {
        "name": "Ubuntu 20.04 x64",
        "distribution": "Ubuntu"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "features": ["monitoring", "ipv6"],
    "tags": ["web", "production"]
}
```

#### 监控数据响应

```python
{
    "cloud_provider": "digitalocean",
    "droplet_id": 123456789,
    "monitoring_enabled": true,
    "metrics": {
        "cpu": {
            "available": true,
            "data": [...]
        },
        "memory": {
            "available": true,
            "data": [...]
        },
        "disk": {
            "available": false,
            "data": []
        },
        "network": {
            "available": true,
            "data": [...]
        }
    },
    "note": "监控数据可能需要几分钟才能在新启用监控的droplet上显示。"
}
```

### 错误响应示例

#### 删除操作被阻止

```python
{
    "cloud_provider": "digitalocean",
    "error": "删除操作已被禁用。出于安全考虑，所有droplet删除操作被限制。",
    "security_info": {
        "protection_level": "MAXIMUM",
        "reason": "防止意外删除重要服务器",
        "how_to_enable": "设置环境变量 ALLOW_DROPLET_DELETION=true (不推荐)"
    }
}
```

#### 一般错误

```python
{
    "cloud_provider": "digitalocean",
    "error": "未找到ID为 123456789 的droplet"
}
```

## 测试功能

项目包含一个完整的测试脚本 `test_dg_info.py`，可以测试所有功能：

```bash
python test_dg_info.py
```

测试脚本包含以下测试模块：

- **基本功能测试**: 列出 droplets、API 连接测试
- **Droplet 操作测试**: 状态查询、电源管理、操作历史
- **监控功能测试**: 监控数据获取和可用性检查
- **删除保护测试**: 安全策略检查、删除安全性评估
- **IP 查找测试**: 根据 IP 地址查找对应的 droplet

## 注意事项

### 安全相关

1. **删除保护**:

   - 默认禁用所有删除操作以防止意外删除
   - 多重安全检查机制保护重要服务器
   - 即使配置允许删除，实际删除仍被最终安全检查阻止
   - 强烈建议通过 DigitalOcean 控制面板手动删除

2. **API 权限**: 确保您的 DigitalOcean API token 具有适当的权限：

   - 读取 droplets 的权限
   - 执行 droplet 操作的权限（开关机、重启等）
   - 访问监控数据的权限

3. **监控功能限制**:

   - 需要在 droplet 上启用监控功能（在创建时或后续在控制面板中启用）
   - 监控数据可能需要几分钟才能显示
   - 免费 monitoring 功能每 5 分钟收集一次数据点

4. **API 调用限制**:

   - DigitalOcean API 有频率限制（每小时 5,000 次请求）
   - 电源操作是异步的，需要查询操作状态来确认完成

5. **安全考虑**:
   - 请妥善保管您的 API token
   - 建议使用环境变量存储敏感信息
   - 在生产环境中限制 API token 的权限范围
   - 避免在自动化脚本中启用删除功能

## 操作状态说明

droplet 可能的状态包括：

- `new`: 新创建，正在初始化
- `active`: 运行中
- `off`: 已关机
- `archive`: 已归档（长期关闭）

操作状态包括：

- `in-progress`: 执行中
- `completed`: 已完成
- `errored`: 执行失败

删除安全等级：

- `BLOCKED`: 删除被阻止（有严重安全问题）
- `WARNING`: 需要谨慎考虑（有潜在风险）
- `CAUTION`: 可以删除但需确认（仍有限制）

## 最佳实践

1. **安全操作**:

   - 避免启用删除功能，始终通过控制面板手动删除
   - 定期使用 `check_droplet_deletion_safety()` 评估服务器安全性
   - 为重要服务器添加保护标签

2. **批量操作**: 使用 `list_droplets()` 获取所有 droplets，然后根据需要过滤和操作

3. **状态检查**: 在执行电源操作前，先检查 droplet 当前状态

4. **操作跟踪**: 保存操作 ID，用于后续状态查询

5. **错误处理**: 始终检查返回结果中的 `error` 字段

6. **监控启用**: 在创建 droplet 时启用监控功能，以便后续获取使用数据

## 依赖安装

```bash
pip install -r requirements.txt
```

## 环境变量配置

创建 `.env` 文件并设置以下环境变量：

```bash
# DigitalOcean API Token
# 在 https://cloud.digitalocean.com/account/api/tokens 获取
DIGITALOCEAN_TOKEN=your_digitalocean_api_token_here

# IPInfo API Token (可选，用于IP地址查询)
# 在 https://ipinfo.io/account/token 获取
IPINFO_API_TOKEN=your_ipinfo_api_token_here

# 删除功能控制 (强烈不推荐启用)
# ALLOW_DROPLET_DELETION=false  # 默认值，建议保持禁用
```

## 使用方法

### 启动服务器

```bash
python main.py
```

## API 说明

### pydo SDK 集成

本项目使用官方的 [pydo SDK](https://github.com/digitalocean/pydo) 来与 DigitalOcean API 交互：

1. **安装 pydo**: `pip install pydo`
2. **配置 API Token**: 设置 `DIGITALOCEAN_TOKEN` 环境变量
3. **调用 API**: 使用 `client.droplets.list()` 获取所有 droplets

### 工作原理

1. 初始化 pydo 客户端，使用配置的 API token
2. 调用 `client.droplets.list()` 获取账户下所有 droplets
3. 遍历每个 droplet 的网络配置
4. 查找匹配指定公网 IP 地址的 droplet
5. 返回找到的 droplet 的详细信息

## 错误处理

- 自动检测 pydo SDK 是否已安装
- 验证 DIGITALOCEAN_TOKEN 环境变量是否配置
- 捕获 API 调用异常并返回友好的错误信息
- 提供详细的调试信息

## 注意事项

1. 确保您的 DigitalOcean API token 具有读取 droplets 的权限
2. API 有调用频率限制，请合理使用
3. 该功能会列出账户下所有 droplets，请确保 token 的安全性

## 扩展功能

- 支持按标签过滤 droplets
- 支持分页查询大量 droplets
- 缓存查询结果以提高性能
- 支持其他云服务提供商（AWS、GCP 等）
