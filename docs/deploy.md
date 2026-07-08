# Streamlit Community Cloud デプロイ手順

card-compare と同じ構成（GitHub + Streamlit Community Cloud）です。

## 前提

- GitHub アカウント
- [GitHub CLI](https://cli.github.com/)（`gh`）推奨

## クイックデプロイ（推奨）

```bash
cd ~/Desktop/貸付モニ
./scripts/deploy.sh
```

初回はブラウザで GitHub ログイン（デバイス認証）が求められます。  
push 完了後、表示される手順に従い [share.streamlit.io](https://share.streamlit.io) でアプリを作成してください。
誰でも URL だけで閲覧できる public アプリになります（財務データ公開に注意）。

リポジトリ名を変える場合:

```bash
./scripts/deploy.sh kashitsuke-monitor
```

private にしたい場合:

```bash
./scripts/deploy.sh kashitsuke-monitor private
```

## 手動デプロイ

### 1. GitHub へ push

```bash
cd ~/Desktop/貸付モニ
git remote add origin https://github.com/<your-username>/kashitsuke-monitor.git
git push -u origin main
```

### 2. Streamlit Community Cloud でデプロイ

1. [share.streamlit.io](https://share.streamlit.io) にアクセス
2. GitHub アカウントでログイン
3. **Create app** をクリック
4. 設定:
   - **Repository**: `<your-username>/kashitsuke-monitor`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. **Deploy** をクリック

数分後、`https://<app-name>-<hash>.streamlit.app` で公開されます。  
iPhone からはこの URL を Safari で開けば、別 Wi‑Fi / モバイル回線でも閲覧できます。

### 3. 再デプロイ

`main` ブランチへの push で自動的に再デプロイされます。

## ローカル確認

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 注意事項

- 入金 CSV / 計算基準日を含みます。リンク共有範囲に注意
- Streamlit Cloud 上の「保存」はコンテナ再起動で消える可能性があります。恒久反映は `payments.csv` / `config.json` を更新して push してください
- `requirements.txt` に全依存関係を記載する
- Python 3.10 以上を推奨

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| デプロイ失敗 | Cloud のログで `requirements.txt` のエラーを確認 |
| private リポジトリが選べない | Streamlit Cloud で GitHub 連携を再認証（repo 権限） |
| 共有URLが localhost | 本番では `*.streamlit.app` の HTTPS URL を使う |
