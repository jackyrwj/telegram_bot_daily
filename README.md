# Telegram 每日报告机器人

这是一个功能丰富的每日报告机器人，使用 GitHub Actions 自动推送到 Telegram。包含时间统计、GitHub 活动、运动数据和每日诗词。

## 🌟 功能特点

- **📅 时间统计**: 年度进度条和天数统计
- **📊 GitHub 活动**: 自动获取 PR、Issue 和提交记录
- **🏃 运动统计**: 跑步距离和目标跟踪
- **📜 每日诗词**: 精选古诗词推送
- **🤖 自动化**: GitHub Actions 定时执行
- **⚙️ 可配置**: 支持自定义数据和设置

## 设置步骤

### 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 保存获得的 Bot Token

### 2. 获取 Chat ID

有两种方式获取 Chat ID：

**方式一：使用脚本获取**

```bash
python get_chat_id.py
```

**方式二：手动获取**

1. 将机器人添加到目标群组或频道
2. 发送一条消息给机器人
3. 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. 在返回的 JSON 中找到 `chat.id`

### 3. 配置 GitHub Secrets

在你的 GitHub 仓库中设置以下 Secrets：

1. 进入仓库的 `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret` 添加：
   - `BOT_TOKEN`: 你的 Telegram Bot Token
   - `CHAT_ID`: 目标群组或频道的 Chat ID
   - `GITHUB_TOKEN`: 你的 GitHub Personal Access Token (可选，用于获取活动数据)
   - `GH_USERNAME`: 你的 GitHub 用户名

### 4. 自定义推送时间

编辑 `.github/workflows/daily-push.yml` 文件中的 cron 表达式：

```yaml
schedule:
  # 当前设置：每天北京时间上午 9:00 (UTC 01:00)
  - cron: "0 1 * * *"
```

Cron 表达式格式：`分 时 日 月 周`

- `0 1 * * *` - 每天 UTC 01:00 (北京时间 09:00)
- `0 13 * * *` - 每天 UTC 13:00 (北京时间 21:00)
- `0 1 * * 1-5` - 工作日 UTC 01:00

### 5. 测试运行

1. **手动触发测试**：

   - 进入 GitHub 仓库的 `Actions` 页面
   - 选择 "Daily Telegram Bot Push" 工作流
   - 点击 `Run workflow` 手动触发

2. **本地测试**：
   ```bash
   pip install -r requirements.txt
   python push.py
   ```

## 📁 文件说明

- `advanced_report.py` - 🚀 高级日报生成器（主脚本）
- `push.py` - 📜 简单古诗推送脚本（向后兼容）
- `config.json` - ⚙️ 配置文件（运动数据、GitHub 用户名等）
- `update_config.py` - 🔧 配置更新工具
- `get_chat_id.py` - 🔍 获取 Chat ID 的辅助脚本
- `requirements.txt` - 📦 Python 依赖包
- `.github/workflows/daily-push.yml` - 🤖 GitHub Actions 工作流配置

## 🛠️ 使用方法

### 更新运动数据

使用配置管理工具更新跑步数据：

```bash
python update_config.py
```

或者直接编辑 `config.json` 文件：

```json
{
  "running": {
    "month_distance": 53.7,
    "year_distance": 967.81,
    "last_run_date": "2025-10-06"
  }
}
```

### 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 发送完整日报
python advanced_report.py

# 发送简单古诗
python advanced_report.py simple
```

### GitHub Token 设置

要获取 GitHub 活动数据，需要创建 Personal Access Token：

1. 访问 GitHub → Settings → Developer settings → Personal access tokens
2. 创建新的 token，选择 `public_repo` 权限
3. 将 token 添加到 GitHub Secrets 中的 `GITHUB_TOKEN`

## 📊 日报内容示例

```
📅 每日报告

今天的起床时间是--2025-10-07 05:00:43。

起床啦。

今天是今年的第 280 天。

██████████████░░░░░░ 76.7% (280/365)

GitHub：

• 创建了 PR: Add new feature (username/repo)
• 提交了: Fix bug in main.py (username/repo)

Run：

• 昨天没跑
• 本月跑了 53.7 公里
• 今年跑了 967.81 公里

今天的一句诗:

携壶酌流霞，搴菊泛寒荣。
—— 李白《九日龙山饮》
```

## 🎨 自定义功能

### 添加更多诗词

编辑 `advanced_report.py` 中的 `get_daily_poem()` 函数：

```python
poems = [
    {"content": "你的诗句", "author": "作者", "title": "诗名"},
    # 添加更多...
]
```

### 接入运动 API

你可以修改 `get_running_stats()` 函数来接入：

- Strava API
- Nike Run Club API
- 咕咚 API
- 其他运动应用 API

### 自定义 GitHub 活动

修改 `get_github_activity()` 函数来：

- 过滤特定类型的活动
- 添加更多活动类型
- 自定义显示格式

## 🐛 故障排除

1. **推送失败**：检查 Bot Token 和 Chat ID 是否正确
2. **GitHub 数据获取失败**：确认 GITHUB_TOKEN 和 GITHUB_USERNAME 设置正确
3. **配置文件错误**：使用 `update_config.py` 重新生成配置
4. **时区问题**：GitHub Actions 使用 UTC 时间，需要换算

## ⚠️ 注意事项

- GitHub Actions 免费账户每月有 2000 分钟限制
- GitHub API 有速率限制，建议设置 GITHUB_TOKEN
- 定期更新运动数据以保持准确性
- 保护好你的 Bot Token 和其他敏感信息
