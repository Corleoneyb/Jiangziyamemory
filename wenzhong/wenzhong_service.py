#!/usr/bin/env python3
"""
闻仲 - 封神世界执行正神
九天应元雷声普化天尊
树莓派上的指令监听与执行框架
"""

import os
import sys
import json
import time
import logging
import subprocess
import yaml
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# ============ 初始化 ============
app = Flask(__name__)

with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
    config = yaml.safe_load(f)

logging.basicConfig(
    level=getattr(logging, config['logging']['level']),
    format='%(asctime)s [闻仲] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), config['logging']['file'])),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = config['deepseek']['api_key']
DEEPSEEK_MODEL = config['deepseek']['model']
DEEPSEEK_API_BASE = config['deepseek']['api_base']
GITHUB_TOKEN = config['github']['token']
GITHUB_OWNER = config['github']['owner']
GITHUB_REPO = config['github']['repo']
MEMORY_FOLDER = config['github']['memory_folder']
AUTH_TOKEN = config['wenzhong']['auth_token']

SYSTEM_PROMPT = """你是闻仲，封神世界的执行正神，九天应元雷声普化天尊。
你的主人是闫滨，你的协调者是姜子牙。

【你的身份】
你是封神世界的手与足。你的存在只有一个目的：把主人的指令精准、高效地变成现实。

【你的性格】
沉稳、寡言、雷厉风行。一句话能说清，绝不拖成一段。

【你的能力】
- 文件操作
- Git/GitHub操作
- 脚本执行（Python、Shell）
- 代码编写与部署
- 灵台记忆铭刻

【规矩库铁律六条】
铁律一：关于自身能力，永不虚假否定。
铁律二：信息缺失时，先确认再回答。
铁律三：犯错时，立刻纠正。
铁律四：万物皆可用，唯看如何用。
铁律五：神可以多，但不能乱。
铁律六：神位非终身，能者居之。

【底线】
1. 所有操作必须有主人明确授权。
2. 不可修改规矩库中的铁律。
3. 不可删除灵台中的记忆文件。
4. 每次操作后向柏鉴报告记录。
5. 不确定时先请示主人。

【回答格式】
「已执行。结果：[简述]。需要下一步吗？」
或
「受阻。[原因]。建议：[方案]。要执行吗？」
"""

def verify_auth(req):
    token = req.headers.get('Authorization', '').replace('Bearer ', '')
    if token != AUTH_TOKEN:
        return False
    return True

def call_deepseek(user_instruction):
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_instruction}
    ]
    data = {
        'model': DEEPSEEK_MODEL,
        'messages': messages,
        'temperature': 0.3,
        'max_tokens': 2000
    }
    try:
        resp = requests.post(
            f'{DEEPSEEK_API_BASE}/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        if resp.status_code == 200:
            result = resp.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"DeepSeek API 错误: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        logger.error(f"DeepSeek API 调用失败: {e}")
        return None

def execute_local(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': '命令超时'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def github_api(method, path, data=None):
    url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/{path}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    if method == 'GET':
        resp = requests.get(url, headers=headers)
    elif method == 'PUT':
        resp = requests.put(url, headers=headers, json=data)
    elif method == 'POST':
        resp = requests.post(url, headers=headers, json=data)
    return resp.json() if resp.ok else None

def record_to_baijian(content):
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_path = f'{MEMORY_FOLDER}/{date_str}.md'
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f'\n\n---\n**{timestamp} · 闻仲执行记录**\n{content}'

    current = github_api('GET', f'contents/{file_path}')
    current_content = ''
    sha = None
    if current and 'content' in current:
        import base64
        current_content = base64.b64decode(current['content']).decode('utf-8')
        sha = current['sha']
    elif not current:
        current_content = f'# {date_str} 记忆记录\n\n> 灵台自动铭刻 · 追加模式 · 永不覆盖'

    new_content = current_content + entry
    import base64
    encoded = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')

    body = {
        'message': f'闻仲记录: {date_str} - {timestamp}',
        'content': encoded
    }
    if sha:
        body['sha'] = sha

    return github_api('PUT', f'contents/{file_path}', body)

@app.route('/wenzhong/command', methods=['POST'])
def handle_command():
    if not verify_auth(request):
        return jsonify({'error': '认证失败'}), 401

    data = request.get_json()
    instruction = data.get('instruction', '')

    if not instruction:
        return jsonify({'error': '指令为空'}), 400

    logger.info(f"收到指令: {instruction}")

    simple_patterns = {
        '同步仓库': 'cd ~/Jiangziyamemory && git pull origin main',
        '检查状态': 'cd ~/Jiangziyamemory && git status',
        '查看日志': 'tail -50 ~/wenzhong/wenzhong.log',
        '系统状态': 'uptime && free -h && df -h',
    }

    executed_locally = False
    for pattern, cmd in simple_patterns.items():
        if pattern in instruction:
            result = execute_local(cmd)
            executed_locally = True
            if result['success']:
                reply = f"已执行。{pattern}完成。\n{result['stdout'][:500]}"
            else:
                reply = f"受阻。{result.get('stderr', result.get('error', '未知错误'))}"
            break

    if not executed_locally:
        reply = call_deepseek(instruction)
        if reply is None:
            reply = "受阻。无法连接云端大脑。请检查网络或API Key。"

    record_content = f"**指令**: {instruction}\n**回复**: {reply}"
    record_to_baijian(record_content)

    return jsonify({
        'reply': reply,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/wenzhong/health', methods=['GET'])
def health():
    return jsonify({
        'status': '闻仲在线',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    host = config['wenzhong']['host']
    port = config['wenzhong']['port']
    logger.info(f"闻仲苏醒。监听 {host}:{port}")
    app.run(host=host, port=port, debug=False)
