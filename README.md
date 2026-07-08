# 金銭消費貸借 充当計算ダッシュボード

金銭消費貸借契約の返済予定と入金実績から、遅延損害金の日割り計算・法定充当・一括精算額を可視化する Streamlit アプリです。

## ローカル実行

```bash
cd 貸付モニ
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## デプロイ

Streamlit Community Cloud へのデプロイ手順は [docs/deploy.md](docs/deploy.md) を参照してください。

```bash
./scripts/deploy.sh
```

## 計算ルール（要約）

- 遅延損害金: 年 21.9%（うるう年は 366 日）
- 充当順位: 遅延損害金 → 滞納元本（法定充当）
- 端数処理: 区間ごと切り捨て

## 注意

入金履歴・残高など財務データを含みます。公開範囲に注意してください（既定のデプロイは private リポジトリ）。
