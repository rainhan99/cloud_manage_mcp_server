# 多云服务器管理系统 (Multi-Cloud Server Manager)

基于 MCP (Model Context Protocol) 的智能多云服务器管理系统，支持 AWS、DigitalOcean、Vultr、阿里云四大主流云服务平台的统一管理。

## 📚 文档导航

- 🔥 **[MCP 服务完整规范](MCP_SERVICE_SPECIFICATION.md)** - 标准化 MCP 服务文档，包含所有工具详情
- ⚡ **[MCP 快速参考](MCP_QUICK_REFERENCE.md)** - 常用工具和配置的速查表
- 📖 **本文档** - 项目概述、安装部署和基础使用
- 🎯 **[使用示例](USAGE_EXAMPLES.md)** - 详细的使用示例和最佳实践指南

## 🌟 核心特性

### 🎯 智能路由

- **自动 IP 检测**: 根据 IP 地址自动识别云服务提供商
- **统一接口**: 一个函数查询所有云平台的服务器信息
- **智能分发**: 自动路由到对应的云平台 API

### 🛡️ 多重安全保护

- **三次确认机制**: 电源操作需要确认 IP、名称、操作类型
- **AWS 只读权限**: AWS 平台仅提供查询功能，确保安全
- **删除操作禁用**: 所有平台完全禁用删除操作
- **智能安全检查**: 自动识别生产环境标签和大型实例

### 🌐 多云平台支持

- **AWS EC2**: 只读查询，包括存储详情、监控数据
- **DigitalOcean**: 查询 + 电源管理（开关机、重启）
- **Vultr**: 查询 + 电源管理 + 带宽监控
- **阿里云 ECS**: 查询 + 电源管理 + 监控数据

## 📋 系统要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) 包管理器
- 对应云平台的 API 访问权限

## 🚀 快速开始

### 方式一：一键设置（推荐）

```bash
# 克隆项目
git clone https://github.com/rainhan99/cloud_manage_mcp_server.git
cd cloud_manage_mcp_server

# 运行一键设置脚本
./setup.sh
```

这个脚本会自动：

- 检查 Python 版本（需要 3.10+）
- 安装 uv 包管理器（如果未安装）
- 安装所有项目依赖
- 检查环境变量配置
- 运行系统状态检查

### 方式二：手动设置

### 1. 安装 uv 包管理器

如果您还没有安装 uv，可以通过以下方式安装：

```bash
# macOS 和 Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip 安装
pip install uv
```

### 2. 克隆项目并安装依赖

```bash
# 克隆项目
git clone https://github.com/rainhan99/cloud_manage_mcp_server.git
cd cloud_manage_mcp_server

# 使用 uv 安装依赖
uv sync

# 如果需要开发依赖
uv sync --extra dev

# 如果需要性能优化依赖
uv sync --extra performance

# 安装所有依赖（包括可选依赖）
uv sync --extra full
```

### 3. 配置环境变量

复制配置示例文件并填入您的 API 凭证：

```bash
cp config.env.example .env
# 编辑 .env 文件，填入您的API密钥
```

### 4. 启动系统

```bash
# 使用 uv 运行
uv run python main.py

# 或者使用 Makefile（推荐）
make run

# 或者激活虚拟环境后运行
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
python main.py
```

## ⚙️ 环境变量配置

### IP 检测服务（可选）

```bash
IPINFO_API_TOKEN=your_ipinfo_token_here
```

### AWS 配置

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### DigitalOcean 配置

```bash
DIGITALOCEAN_TOKEN=your_digitalocean_token
```

### Vultr 配置

```bash
VULTR_API_KEY=your_vultr_api_key
```

### 阿里云配置

```bash
ALIBABA_CLOUD_ACCESS_KEY_ID=your_alibaba_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_alibaba_access_key_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

## 🔧 主要功能

### 智能实例查询

```python
# 方式1：自动检测并查询任意云平台的实例（传统方式）
get_instance_info("1.2.3.4")  # 根据IP自动识别云平台

# 方式2：明确指定云平台（推荐，更快速）
get_instance_info("1.2.3.4", provider="aws")        # 直接指定AWS
get_instance_info("104.248.1.100", provider="digitalocean")  # 直接指定DigitalOcean

# 方式3：直接通过云平台查询（最高效）
get_instance_by_provider("aws", "i-1234567890abcdef0")       # AWS实例ID
get_instance_by_provider("digitalocean", "123456")           # DigitalOcean Droplet ID
get_instance_by_provider("vultr", "uuid-string")             # Vultr实例ID
get_instance_by_provider("alibaba", "i-bp1234567890")        # 阿里云实例ID
```

### 通用电源管理（新增）

```python
# 通用电源管理函数，支持所有云平台（AWS除外）
manage_instance_power(
    provider="digitalocean",
    instance_id="123456",
    action="reboot",
    ip_confirmation="1.2.3.4",
    name_confirmation="web-server",
    operation_confirmation="重启"
)

# 支持的操作类型：
# - power_on: 开机
# - power_off: 强制关机
# - reboot: 重启
# - shutdown: 优雅关机（部分平台支持）

# Vultr示例
manage_instance_power(
    provider="vultr",
    instance_id="uuid-string",
    action="power_on",
    ip_confirmation="5.6.7.8",
    name_confirmation="test-server",
    operation_confirmation="开机"
)

# 阿里云示例
manage_instance_power(
    provider="alibaba",
    instance_id="i-bp1234567890",
    action="power_off",
    ip_confirmation="47.96.1.100",
    name_confirmation="prod-server",
    operation_confirmation="关机"
)
```

### AWS 专属功能（只读）

```python
# 获取EC2实例信息
get_aws_instance_info("i-1234567890abcdef0")

# 获取存储详细信息（磁盘类型、IOPS、吞吐量）
get_aws_instance_storage_info("i-1234567890abcdef0")

# 获取监控数据
get_aws_instance_monitoring("i-1234567890abcdef0", hours=24)
```

### DigitalOcean 功能

```python
# 查询Droplet信息
get_digitalocean_droplet_info("droplet_id_or_ip")

# 电源管理（需要三次确认）
power_on_digitalocean_droplet(
    droplet_id=12345,
    ip_confirmation="1.2.3.4",
    name_confirmation="web-server",
    operation_confirmation="开机"
)
```

### Vultr 功能

```python
# 查询实例信息
get_vultr_instance_info("instance_id_or_ip")

# 电源管理
power_on_vultr_instance(instance_id, ip_confirm, name_confirm, op_confirm)

# 带宽监控
get_vultr_instance_bandwidth("instance_id")
```

### 阿里云功能

```python
# 查询ECS实例
get_alibaba_instance_info("i-bp1234567890")

# 电源管理
power_on_alibaba_instance(instance_id, ip_confirm, name_confirm, op_confirm)

# 监控数据
get_alibaba_instance_monitoring("i-bp1234567890")
```

### 系统管理

```python
# 检查系统状态
get_system_status()

# 查看支持的云平台
get_supported_providers()

# 检查特定平台可用性
check_provider_availability("aws")
```

## 🛡️ 安全机制详解

### 三次确认流程

所有电源操作都需要通过三次确认：

1. **IP 地址确认**: 必须输入目标服务器的准确 IP 地址
2. **名称确认**: 必须输入服务器的准确名称
3. **操作确认**: 必须输入准确的操作类型

```python
# 示例：重启服务器
reboot_digitalocean_droplet(
    droplet_id=12345,
    ip_confirmation="192.168.1.100",     # 第一次确认：IP
    name_confirmation="web-server-01",    # 第二次确认：名称
    operation_confirmation="重启"         # 第三次确认：操作
)
```

### 安全检查项目

系统会自动执行以下安全检查：

- ✅ 实例状态检查（避免对已关机实例执行关机操作）
- ✅ 生产环境标签检测（protection、prod、critical 等）
- ✅ 大型实例警告（避免误操作高配置实例）
- ✅ 确认信息验证（防止误操作）

## 📊 项目结构

```
cloud_manage_mcp_server/
├── main.py                    # 主入口文件和MCP工具函数
├── providers/                 # 云服务提供商模块
│   ├── aws_provider.py       # AWS EC2提供商
│   ├── digitalocean_provider.py  # DigitalOcean提供商
│   ├── vultr_provider.py     # Vultr提供商
│   └── alibaba_provider.py   # 阿里云提供商
├── utils/                     # 工具模块
│   ├── ip_detection.py       # IP地址检测和路由
│   └── security.py           # 安全确认机制
├── pyproject.toml             # uv项目配置和依赖管理
├── .python-version           # Python版本指定
├── config.env.example        # 环境变量配置示例
├── README_NEW.md             # 项目文档
└── test_dg_info.py          # 测试脚本（旧版）
```

## 🎮 使用示例

### 场景 1：根据 IP 查找服务器

```python
# 用户只知道IP地址，系统自动识别云平台并查询
result = get_instance_info("104.248.1.100")

# 返回结果包含：
# - 检测到的云平台
# - 完整的服务器信息
# - 平台能力说明
```

### 场景 2：AWS 服务器存储分析

```python
# 查看AWS实例的详细存储配置
storage_info = get_aws_instance_storage_info("i-1234567890abcdef0")

# 获取信息：
# - 磁盘类型（gp3, io2等）
# - IOPS性能
# - 吞吐量
# - 加密状态
```

### 场景 3：安全的服务器重启

```python
# 第一步：获取服务器信息确认
server_info = get_digitalocean_droplet_info("123456")

# 第二步：执行安全重启（需要三次确认）
result = reboot_digitalocean_droplet(
    droplet_id=123456,
    ip_confirmation="192.168.1.100",
    name_confirmation="web-server-prod",
    operation_confirmation="重启"
)

# 如果确认信息错误，操作会被拒绝
```

## 🔍 故障排除

### 1. 提供商不可用

```bash
# 检查系统状态
uv run python -c "from main import get_system_status; print(get_system_status())"

# 检查特定提供商
uv run python -c "from main import check_provider_availability; print(check_provider_availability('aws'))"
```

### 2. 环境变量问题

- 确保 `.env` 文件存在且格式正确
- 检查 API 密钥是否有正确的权限
- 验证区域配置是否正确

### 3. 网络连接问题

- 确保能访问对应云平台的 API 端点
- 检查防火墙和代理设置
- 验证 DNS 解析是否正常

### 4. uv 相关问题

```bash
# 重新同步依赖
uv sync --refresh

# 检查依赖状态
uv pip list

# 清理并重新安装
rm -rf .venv uv.lock
uv sync
```

## 🎮 开发环境

### 设置开发环境

```bash
# 安装开发依赖
uv sync --extra dev

# 运行代码格式化
uv run black .
uv run isort .

# 运行类型检查
uv run mypy .

# 运行测试
uv run pytest

# 运行代码质量检查
uv run flake8 .
```

### 添加新依赖

```bash
# 添加生产依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 添加可选依赖
uv add --optional performance package-name
```

## 📈 性能优化

### 1. IP 检测缓存

系统支持 IP 检测结果缓存，减少重复查询：

```python
# 配置IPInfo API token以启用智能检测
IPINFO_API_TOKEN=your_token
```

### 2. 并发查询

对于批量操作，建议使用异步方式：

```python
# 并发查询多个实例
import asyncio
results = await asyncio.gather(
    get_aws_instance_info("i-123"),
    get_digitalocean_droplet_info("456"),
    get_vultr_instance_info("789")
)
```

### 3. 使用性能依赖

```bash
# 安装性能优化依赖
uv sync --extra performance

# 这将安装 ujson 和 orjson 以提升JSON处理性能
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 安装开发依赖 (`uv sync --extra dev`)
4. 进行开发并运行测试 (`uv run pytest`)
5. 运行代码质量检查 (`uv run black . && uv run isort . && uv run mypy .`)
6. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
7. 推送到分支 (`git push origin feature/AmazingFeature`)
8. 开启 Pull Request

## 📦 构建和发布

```bash
# 构建项目
uv build

# 发布到 PyPI（需要配置认证）
uv publish

# 本地安装开发版本
uv pip install -e .
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [uv](https://github.com/astral-sh/uv) - 现代化的 Python 包管理器
- [MCP Framework](https://github.com/modelcontextprotocol) - 模型上下文协议框架
- [AWS SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - AWS Python SDK
- [DigitalOcean pydo](https://github.com/digitalocean/pydo) - DigitalOcean 官方 Python 库
- [IPInfo](https://ipinfo.io/) - IP 地址地理位置和 ISP 检测服务

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [常见问题](#故障排除) 部分
2. 搜索 [现有 Issues](https://github.com/rainhan99/cloud_manage_mcp_server/issues)
3. 创建新的 [Issue](https://github.com/rainhan99/cloud_manage_mcp_server/issues/new)

---

**⚠️ 重要提醒**: 本系统优先考虑安全性，所有删除操作已被禁用。建议通过各云平台的官方控制面板进行敏感操作。
