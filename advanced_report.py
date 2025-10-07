import asyncio
import os
import requests
import random
import json
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode

# --- 配置 ---
BOT_TOKEN = os.getenv('BOT_TOKEN', "8226079704:AAHuBWHZphave2xwU_A6ELI3M3IsZOfwZQ4")
CHAT_ID = os.getenv('CHAT_ID', "-1002587693096")
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GH_USERNAME = os.getenv('GH_USERNAME', '')

class DailyReportGenerator:
    def __init__(self):
        self.current_time = datetime.now()
        self.start_of_year = datetime(self.current_time.year, 1, 1)
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return {
                "github": {
                    "username": GH_USERNAME
                }
            }
        
    def get_date_info(self):
        """获取日期相关信息：日期、星期、节气、农历"""
        day_of_year = (self.current_time - self.start_of_year).days + 1
        total_days = 366 if self.current_time.year % 4 == 0 else 365
        progress_percent = (day_of_year / total_days) * 100
        
        # 创建进度条 (20个字符)
        filled_blocks = int(progress_percent / 5)
        progress_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
        
        # 中文星期
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        weekday = weekdays[self.current_time.weekday()]
        
        # 获取节气（简化版本）
        solar_term = self.get_solar_term()
        
        # 获取农历（简化版本）
        lunar_info = self.get_lunar_date()
        
        return {
            'date': self.current_time.strftime('%Y年%m月%d日'),
            'weekday': f'星期{weekday}',
            'day_of_year': day_of_year,
            'total_days': total_days,
            'progress_percent': round(progress_percent, 1),
            'progress_bar': progress_bar,
            'solar_term': solar_term,
            'lunar_date': lunar_info
        }
    
    def get_solar_term(self):
        """获取当前节气（简化版本）"""
        # 简化的节气计算，实际应用建议使用专业的农历库
        month = self.current_time.month
        day = self.current_time.day
        
        solar_terms = {
            (1, 5, 6): "小寒", (1, 20, 21): "大寒",
            (2, 3, 5): "立春", (2, 18, 20): "雨水",
            (3, 5, 6): "惊蛰", (3, 20, 21): "春分",
            (4, 4, 6): "清明", (4, 19, 21): "谷雨",
            (5, 5, 6): "立夏", (5, 20, 22): "小满",
            (6, 5, 7): "芒种", (6, 21, 22): "夏至",
            (7, 6, 8): "小暑", (7, 22, 24): "大暑",
            (8, 7, 9): "立秋", (8, 22, 24): "处暑",
            (9, 7, 9): "白露", (9, 22, 24): "秋分",
            (10, 8, 9): "寒露", (10, 23, 24): "霜降",
            (11, 7, 8): "立冬", (11, 22, 23): "小雪",
            (12, 6, 8): "大雪", (12, 21, 23): "冬至"
        }
        
        for (m, start, end), term in solar_terms.items():
            if month == m and start <= day <= end:
                return term
        return ""
    
    def get_lunar_date(self):
        """获取农历日期（简化版本）"""
        try:
            # 这里使用一个简化的农历API或者库
            # 实际应用中建议使用专业的农历转换库如 lunardate
            response = requests.get(
                f"https://api.xiaobaibk.com/api/lunar/?date={self.current_time.strftime('%Y-%m-%d')}",
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    lunar_data = data.get('data', {})
                    return f"{lunar_data.get('lunar_year', '')} {lunar_data.get('lunar_month', '')}{lunar_data.get('lunar_day', '')}"
        except:
            pass
        
        # 如果API失败，返回简化的农历信息
        lunar_months = ['正月', '二月', '三月', '四月', '五月', '六月', 
                       '七月', '八月', '九月', '十月', '冬月', '腊月']
        lunar_days = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                     '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                     '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        
        # 简单估算（不准确，仅为示例）
        month_approx = ((self.current_time.month - 1) % 12)
        day_approx = min(self.current_time.day - 1, 29)
        
        return f"{lunar_months[month_approx]}{lunar_days[day_approx]}"
    
    async def get_github_activity(self, days_back=1):
        """获取 GitHub 活动信息
        
        Args:
            days_back (int): 获取几天前的活动，默认1（昨天）
                           0 = 今天, 1 = 昨天, 2 = 前天
        """
        username = GH_USERNAME or self.config.get('github', {}).get('username', '')
        
        if not username:
            return {"prs": [], "issues": [], "commits": [], "stars": 0}
            
        try:
            headers = {'User-Agent': 'Daily-Report-Bot'}
            if GITHUB_TOKEN:
                headers['Authorization'] = f'token {GITHUB_TOKEN}'
            
            # 获取用户事件
            events_url = f"https://api.github.com/users/{username}/events"
            response = requests.get(events_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"GitHub API 返回状态码: {response.status_code}")
                return {"prs": [], "issues": [], "commits": [], "error": True}
            
            events = response.json()
            target_date = self.current_time - timedelta(days=days_back)
            
            github_activity = {"prs": [], "issues": [], "commits": [], "date": target_date.strftime('%Y-%m-%d')}
            
            for event in events[:30]:  # 检查最近30个事件
                event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                
                # 检查是否是目标日期的活动
                if event_date.date() == target_date.date():
                    if event['type'] == 'PullRequestEvent' and event['payload']['action'] in ['opened', 'closed']:
                        pr_info = {
                            'action': '创建了' if event['payload']['action'] == 'opened' else '合并了',
                            'title': event['payload']['pull_request']['title'],
                            'repo': event['repo']['name'],
                            'url': event['payload']['pull_request']['html_url']
                        }
                        github_activity['prs'].append(pr_info)
                        
                    elif event['type'] == 'IssuesEvent' and event['payload']['action'] == 'opened':
                        issue_info = {
                            'action': '创建了',
                            'title': event['payload']['issue']['title'],
                            'repo': event['repo']['name'],
                            'url': event['payload']['issue']['html_url']
                        }
                        github_activity['issues'].append(issue_info)
                        
                    elif event['type'] == 'PushEvent':
                        commits = event['payload']['commits']
                        for commit in commits[:2]:  # 最多2个提交
                            commit_info = {
                                'message': commit['message'].split('\n')[0][:60],  # 只取第一行，限制长度
                                'repo': event['repo']['name']
                            }
                            github_activity['commits'].append(commit_info)
            
            return github_activity
            
        except Exception as e:
            print(f"获取 GitHub 活动失败: {e}")
            return {"prs": [], "issues": [], "commits": [], "error": True}
    

    
    def get_daily_poem(self):
        """获取每日诗词"""
        poems = [
            {"content": "携壶酌流霞，搴菊泛寒荣。", "author": "李白", "title": "九日龙山饮"},
            {"content": "山重水复疑无路，柳暗花明又一村。", "author": "陆游", "title": "游山西村"},
            {"content": "海内存知己，天涯若比邻。", "author": "王勃", "title": "送杜少府之任蜀州"},
            {"content": "落红不是无情物，化作春泥更护花。", "author": "龚自珍", "title": "己亥杂诗"},
            {"content": "会当凌绝顶，一览众山小。", "author": "杜甫", "title": "望岳"},
            {"content": "长风破浪会有时，直挂云帆济沧海。", "author": "李白", "title": "行路难"},
            {"content": "问君能有几多愁，恰似一江春水向东流。", "author": "李煜", "title": "虞美人"},
            {"content": "春花秋月何时了，往事知多少。", "author": "李煜", "title": "虞美人"},
            {"content": "但愿人长久，千里共婵娟。", "author": "苏轼", "title": "水调歌头"},
            {"content": "人生如梦，一尊还酹江月。", "author": "苏轼", "title": "念奴娇·赤壁怀古"},
            {"content": "采菊东篱下，悠然见南山。", "author": "陶渊明", "title": "饮酒"},
            {"content": "不畏浮云遮望眼，自缘身在最高层。", "author": "王安石", "title": "登飞来峰"},
            {"content": "千里莺啼绿映红，水村山郭酒旗风。", "author": "杜牧", "title": "江南春"},
            {"content": "停车坐爱枫林晚，霜叶红于二月花。", "author": "杜牧", "title": "山行"},
        ]
        return random.choice(poems)
    
    async def generate_report(self, github_days_back=1):
        """生成简洁日报"""
        date_info = self.get_date_info()
        github_activity = await self.get_github_activity(github_days_back)
        poem = self.get_daily_poem()

        # 构建报告文本
        report = f"<b>📅 每日报告</b>\n\n"
        report += f"📆 <b>{date_info['date']} {date_info['weekday']}</b>\n"
        if date_info['solar_term']:
            report += f"🌸 节气：{date_info['solar_term']}\n"
        report += f"🏮 农历：{date_info['lunar_date']}\n\n"
        report += f"今天是今年的第 <b>{date_info['day_of_year']}</b> 天\n"
        report += f"<code>{date_info['progress_bar']}</code> {date_info['progress_percent']}% ({date_info['day_of_year']}/{date_info['total_days']})\n\n"

        # GitHub 活动
        if github_days_back == 0:
            date_text = "今天"
        elif github_days_back == 1:
            date_text = "昨天"
        else:
            date_text = f"{github_days_back}天前"
        report += f"<b>💻 GitHub ({date_text})：</b>\n"
        has_activity = False
        for pr in github_activity.get('prs', []):
            report += f"• {pr['action']} PR: {pr['title']} ({pr['repo']})\n"
            has_activity = True
        for issue in github_activity.get('issues', []):
            report += f"• {issue['action']} Issue: {issue['title']} ({issue['repo']})\n"
            has_activity = True
        for commit in github_activity.get('commits', []):
            report += f"• 提交了: {commit['message']} ({commit['repo']})\n"
            has_activity = True
        if not has_activity:
            if github_activity.get('error'):
                report += "• GitHub 数据获取失败\n"
            else:
                report += f"• {date_text}没有 GitHub 活动\n"
        report += "\n"

        # 每日诗词
        report += "<b>📜 今天的一句诗:</b>\n"
        report += f"<i>{poem['content']}</i>\n"
        if poem.get('author') and poem.get('title'):
            report += f"—— {poem['author']}《{poem['title']}》\n"

        return report

async def send_daily_report(github_days_back=1):
    """发送日报
    
    Args:
        github_days_back (int): 获取几天前的 GitHub 活动，默认1（昨天）
    """
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # 生成日报
        generator = DailyReportGenerator()
        report = await generator.generate_report(github_days_back)
        
        # 发送消息
        await bot.send_message(
            chat_id=CHAT_ID,
            text=report,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        print("✅ 日报发送成功！")
        
    except Exception as e:
        print(f"❌ 日报发送失败: {e}")
        # 发送简化的错误通知
        try:
            error_msg = f"⚠️ 日报生成失败\n\n错误: {str(e)[:100]}"
            await bot.send_message(chat_id=CHAT_ID, text=error_msg)
        except:
            print("连错误通知都发送失败了")

# 兼容性：保持原有的简单推送功能
async def push_poem():
    """推送简单的古诗（向后兼容）"""
    await send_daily_report()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'simple':
            # python advanced_report.py simple - 发送简单版本
            asyncio.run(push_poem())
        elif sys.argv[1] == 'today':
            # python advanced_report.py today - 显示今天的 GitHub 活动
            asyncio.run(send_daily_report(github_days_back=0))
        elif sys.argv[1] == 'yesterday':
            # python advanced_report.py yesterday - 显示昨天的 GitHub 活动
            asyncio.run(send_daily_report(github_days_back=1))
        elif sys.argv[1].isdigit():
            # python advanced_report.py 2 - 显示2天前的 GitHub 活动
            days = int(sys.argv[1])
            asyncio.run(send_daily_report(github_days_back=days))
        else:
            print("❌ 无效参数")
            print("用法:")
            print("  python advanced_report.py        - 默认日报（显示昨天活动）")
            print("  python advanced_report.py simple - 简单版本")
            print("  python advanced_report.py today  - 显示今天的活动")
            print("  python advanced_report.py yesterday - 显示昨天的活动")
            print("  python advanced_report.py 2     - 显示2天前的活动")
    else:
        # python advanced_report.py - 发送完整日报（默认显示昨天活动）
        asyncio.run(send_daily_report())
