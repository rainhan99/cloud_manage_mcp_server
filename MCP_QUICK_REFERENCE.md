# Multi-Cloud Manager MCP 快速参考

## 🚀 快速启动

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp config.env.example .env
# 编辑 .env 文件添加API密钥

# 3. 启动服务
uv run python main.py
```

## 🛠️ 核心工具

### 智能查询

```python
get_instance_info(ip_address="1.2.3.4")  # 自动识别云平台
get_system_status()                       # 查看系统状态
get_supported_providers()                 # 查看支持的平台
```

### AWS (只读)

```python
get_aws_instance_info("i-1234567890abcdef0")      # 实例信息
get_aws_instance_storage_info("i-1234567890")     # 存储详情
get_aws_instance_monitoring("i-1234567890", 24)   # 监控数据
list_aws_instances()                               # 所有实例
```

### DigitalOcean

```python
get_digitalocean_droplet_info("123456")           # Droplet信息
list_digitalocean_droplets()                      # 所有Droplets

# 电源操作（需要三次确认）
power_on_digitalocean_droplet(
    droplet_id=123456,
    ip_confirmation="1.2.3.4",
    name_confirmation="server-name",
    operation_confirmation="开机"
)
```

### Vultr

```python
get_vultr_instance_info("uuid-string")            # 实例信息
list_vultr_instances()                             # 所有实例
get_vultr_instance_bandwidth("uuid-string")       # 带宽监控
```

### 阿里云

```python
get_alibaba_instance_info("i-bp1234567890")       # 实例信息
list_alibaba_instances()                           # 所有实例
get_alibaba_instance_monitoring("i-bp1234567890") # 监控数据
```

## 🔧 Claude Desktop 配置

```json
{
  "mcpServers": {
    "multi-cloud-manager": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/cloud_manage_mcp_server",
      "env": {
        "AWS_ACCESS_KEY_ID": "your_key",
        "DIGITALOCEAN_TOKEN": "your_token",
        "VULTR_API_KEY": "your_key",
        "ALIBABA_CLOUD_ACCESS_KEY_ID": "your_key"
      }
    }
  }
}
```

## 🛡️ 安全确认示例

电源操作需要三次确认：

```python
reboot_digitalocean_droplet(
    droplet_id=123456,
    ip_confirmation="192.168.1.100",    # 第1次：IP地址
    name_confirmation="web-server-01",   # 第2次：服务器名称
    operation_confirmation="重启"        # 第3次：操作类型
)
```

## 📋 环境变量

```bash
# AWS (必需)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# DigitalOcean (必需)
DIGITALOCEAN_TOKEN=your_token

# Vultr (必需)
VULTR_API_KEY=your_key

# 阿里云 (必需)
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret

# IP检测 (可选)
IPINFO_API_TOKEN=your_token
```

## 🔍 故障排除

```bash
# 检查系统状态
make status

# 检查特定平台
uv run python -c "from main import check_provider_availability; print(check_provider_availability('aws'))"

# 重新安装依赖
make clean && uv sync
```

## 📊 权限和限制

| 平台         | 查询 | 开关机 | 重启 | 删除 | 特殊功能       |
| ------------ | ---- | ------ | ---- | ---- | -------------- |
| AWS          | ✅   | ❌     | ❌   | ❌   | 存储详情、监控 |
| DigitalOcean | ✅   | ✅\*   | ✅\* | ❌   | 操作历史       |
| Vultr        | ✅   | ✅\*   | ✅\* | ❌   | 带宽监控       |
| 阿里云       | ✅   | ✅\*   | ✅\* | ❌   | 监控数据       |

\*需要三次确认
