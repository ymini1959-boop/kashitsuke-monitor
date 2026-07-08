#!/usr/bin/env bash
# GitHub push + Streamlit Community Cloud デプロイ手順
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

GH="${GH_BIN:-gh}"
if ! command -v "$GH" >/dev/null 2>&1; then
  if [[ -x /tmp/gh_2.74.1_macOS_amd64/bin/gh ]]; then
    GH=/tmp/gh_2.74.1_macOS_amd64/bin/gh
  elif [[ -x /tmp/gh_2.93.0_macOS_arm64/bin/gh ]]; then
    GH=/tmp/gh_2.93.0_macOS_arm64/bin/gh
  else
    echo "GitHub CLI (gh) が見つかりません。"
    echo "  https://cli.github.com/ からインストールするか、GH_BIN=/path/to/gh を指定してください。"
    exit 1
  fi
fi

if ! "$GH" auth status >/dev/null 2>&1; then
  echo "GitHub にログインします（ブラウザが開きます）..."
  "$GH" auth login -h github.com -p https -w
fi

REPO_NAME="${1:-kashitsuke-monitor}"
VISIBILITY="${2:-private}"

if git remote get-url origin >/dev/null 2>&1; then
  echo "既存の origin へ push します..."
  git push -u origin main
else
  echo "GitHub リポジトリ ${REPO_NAME}（${VISIBILITY}）を作成して push します..."
  "$GH" repo create "$REPO_NAME" --"${VISIBILITY}" --source=. --remote=origin --push
fi

REMOTE_URL="$("$GH" repo view --json url -q .url)"
OWNER_REPO="$("$GH" repo view --json nameWithOwner -q .nameWithOwner)"
echo ""
echo "=========================================="
echo " GitHub push 完了: ${REMOTE_URL}"
echo "=========================================="
echo ""
echo "次に Streamlit Community Cloud でデプロイ:"
echo "  1. https://share.streamlit.io を開く"
echo "  2. New app → Repository: ${OWNER_REPO}"
echo "  3. Branch: main / Main file: app.py"
echo "  4. Deploy をクリック"
echo ""
echo "完了後の URL 例: https://<app-name>.streamlit.app"
echo "iPhone ではその URL を Safari で開けば、別ネットワークでも閲覧できます。"
echo ""
