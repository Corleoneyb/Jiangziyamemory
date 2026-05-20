#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP="$HOME/Desktop"
APP="$DESKTOP/封神·说一句话.app"
CMD="$DESKTOP/封神·说一句话.command"

cat > "$CMD" <<EOF
#!/bin/bash
cd "$ROOT"
/usr/bin/python3 scripts/voice_once.py
EOF
chmod +x "$CMD"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>封神·说一句话</string>
<key>CFBundleExecutable</key><string>run</string>
<key>CFBundleIdentifier</key><string>com.fengshen.voice-once</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.2</string>
</dict></plist>
PLIST

cat > "$APP/Contents/MacOS/run" <<EOF
#!/bin/bash
osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script "cd '$ROOT' && /usr/bin/python3 scripts/voice_once.py"
end tell
APPLESCRIPT
EOF
chmod +x "$APP/Contents/MacOS/run"
echo "【完成】v1.2：说完推微信、自动关终端、识别 small"
