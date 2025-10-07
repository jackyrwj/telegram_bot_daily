# Telegram 每日古诗推送机器人

这是一个使用 GitHub Actions 每天自动推送古诗词到 Telegram 群组或频道的机器人。

## 功能特点

- 每天自动推送精选古诗词
- 包含诗词解析和作者信息
- 使用 GitHub Actions 实现自动化
- 支持手动触发推送

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

## 文件说明

- `push.py` - 主推送脚本
- `get_chat_id.py` - 获取 Chat ID 的辅助脚本
- `requirements.txt` - Python 依赖包
- `.github/workflows/daily-push.yml` - GitHub Actions 工作流配置

## 自定义古诗内容

你可以在 `push.py` 中的 `get_daily_poem()` 函数中：

1. 添加更多古诗到 `poems` 列表
2. 或者调用外部 API 获取古诗数据
3. 或者从文件中读取古诗数据

## 故障排除

1. **推送失败**：检查 Bot Token 和 Chat ID 是否正确
2. **权限错误**：确保机器人已被添加到目标群组并有发送消息权限
3. **时区问题**：GitHub Actions 使用 UTC 时间，需要换算到你的本地时间

## 注意事项

- GitHub Actions 免费账户每月有使用限制
- 建议不要设置过于频繁的推送时间
- 定期检查 Actions 运行状态
