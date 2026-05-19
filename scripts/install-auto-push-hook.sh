#!/usr/bin/env bash
# 一键安装 post-commit 自动 push（见 docs/自动同步.md）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$REPO_ROOT/.git/hooks/post-commit"

if [[ ! -d "$REPO_ROOT/.git" ]]; then
  echo "错误：未找到 .git，请在 Jiangziyamemory 仓库根目录运行。" >&2
  exit 1
fi

mkdir -p "$(dirname "$HOOK")"

cat > "$HOOK" << 'EOF'
#!/bin/sh
export GIT_HTTP_VERSION=HTTP/1.1
git push origin main
EOF

chmod +x "$HOOK"
echo "已安装: $HOOK"
echo "此后每次 git commit 成功将自动 git push origin main（须已配置 GitHub 凭据）。"
