import datetime
import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="貸付モニタ | 充当計算ダッシュボード",
    page_icon="💠",
    initial_sidebar_state="collapsed",
)

C_TEAL = "#0f766e"
C_NAVY = "#0f172a"
C_SLATE = "#64748b"
C_ORANGE = "#ea580c"
C_GREEN = "#15803d"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans JP, -apple-system, sans-serif", color=C_NAVY, size=13),
    margin=dict(l=8, r=8, t=8, b=48),
    hovermode="x unified",
    showlegend=True,
    title=dict(text=""),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.22,
        xanchor="left",
        x=0,
        font=dict(size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    height=310,
)


def inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap');

:root {
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
  --safe-right: env(safe-area-inset-right, 0px);
}

html, body, [class*="css"] {
  font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Hiragino Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}
.stApp {
  background:
    radial-gradient(ellipse 70% 45% at 10% -10%, rgba(15,118,110,0.10) 0%, transparent 55%),
    linear-gradient(180deg, #e2e8f0 0%, #eef2f6 140px, #eef2f6 100%) !important;
}
#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }

.block-container {
  padding-top: calc(0.7rem + var(--safe-top)) !important;
  padding-bottom: calc(2.4rem + var(--safe-bottom)) !important;
  padding-left: calc(0.85rem + var(--safe-left)) !important;
  padding-right: calc(0.85rem + var(--safe-right)) !important;
  max-width: 720px !important;
}

/* サイドバー：タッチしやすいボタン */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f172a 0%, #134e4a 100%);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stButton > button {
  background: #14b8a6 !important;
  color: #042f2e !important;
  border: none !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  min-height: 48px !important;
  font-size: 1rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaption"] { color: #94a3b8 !important; font-size: 0.9rem !important; }
[data-testid="stSidebar"] label { font-size: 0.95rem !important; }

/* Streamlit既定のh1/h2巨大化を抑制 */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
  font-size: inherit !important;
  font-weight: inherit !important;
  margin: 0 !important;
  line-height: inherit !important;
}

.hero {
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 55%, #0f766e 100%);
  color: #fff;
  border-radius: 14px;
  padding: 0.85rem 0.9rem 0.8rem;
  margin-bottom: 0.7rem;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
}
.hero-kicker {
  font-size: 0.65rem !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #99f6e4 !important;
  font-weight: 600 !important;
  margin: 0 0 0.2rem 0 !important;
}
.hero-title {
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  margin: 0 0 0.25rem 0 !important;
  letter-spacing: -0.01em;
  line-height: 1.4 !important;
  color: #fff !important;
}
.hero-sub {
  color: #cbd5e1 !important;
  font-size: 0.78rem !important;
  margin: 0 !important;
  line-height: 1.45 !important;
  font-weight: 400 !important;
}

.case-grid {
  display: grid !important;
  grid-template-columns: 1fr !important;
  gap: 0.65rem;
  margin: 0.65rem 0 0.7rem;
  width: 100%;
}
.case-card {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.07);
  border-radius: 14px;
  padding: 0.85rem 0.9rem 0.8rem;
  box-shadow: 0 6px 18px rgba(15,23,42,0.05);
  min-width: 0;
  overflow: hidden;
}
.case-card.simple { border-top: 3px solid #0f766e; }
.case-card.delay { border-top: 3px solid #ea580c; }
.case-label {
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em;
  margin: 0 0 0.15rem 0 !important;
}
.case-card.simple .case-label { color: #0f766e !important; }
.case-card.delay .case-label { color: #ea580c !important; }
.case-title {
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  margin: 0 0 0.25rem 0 !important;
  line-height: 1.35 !important;
  word-break: keep-all;
  overflow-wrap: anywhere;
}
.case-desc {
  font-size: 0.78rem !important;
  color: #64748b !important;
  margin: 0 0 0.65rem 0 !important;
  line-height: 1.45 !important;
  font-weight: 400 !important;
}
.case-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.45rem 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.88rem !important;
  line-height: 1.35;
}
.case-row:last-child { border-bottom: none; padding-bottom: 0; }
.case-row .k {
  color: #64748b !important;
  flex: 1;
  min-width: 0;
  font-size: 0.84rem !important;
  font-weight: 400 !important;
}
.case-row .k small {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.72rem !important;
  line-height: 1.35 !important;
  color: #94a3b8 !important;
  font-weight: 400 !important;
}
.case-row .v {
  color: #0f172a !important;
  font-weight: 700 !important;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  font-size: 0.92rem !important;
  flex-shrink: 0;
}
.case-row.total {
  margin-top: 0.2rem;
  padding-top: 0.6rem;
  border-top: 1px solid #e2e8f0;
  border-bottom: none;
  align-items: center;
}
.case-row.total .k {
  color: #0f172a !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
}
.case-row.total .v {
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em;
}
.case-card.simple .case-row.total .v { color: #0f766e !important; }
.case-card.delay .case-row.total .v { color: #c2410c !important; }
.diff-note {
  margin-top: 0.1rem;
  margin-bottom: 0.9rem;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #9a3412;
  border-radius: 12px;
  padding: 0.7rem 0.8rem;
  font-size: 0.82rem !important;
  line-height: 1.5 !important;
}
.diff-note strong { font-weight: 700; font-size: 0.92rem !important; }

.rules {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0 0 0.65rem;
}
.rule-chip {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.08);
  color: #334155;
  font-size: 0.72rem !important;
  font-weight: 500;
  padding: 0.32rem 0.55rem;
  border-radius: 999px;
  line-height: 1.3;
}
.rule-chip strong { color: #0f766e; }

.section-head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1rem;
  margin: 0.1rem 0 0.45rem;
}
.section-head h3,
.section-head .section-title {
  margin: 0 !important;
  font-size: 0.98rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  line-height: 1.35 !important;
}
.section-head span { color: #64748b; font-size: 0.78rem !important; }

.panel {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.06);
  border-radius: 14px;
  padding: 0.85rem 0.8rem 0.55rem;
  box-shadow: 0 6px 18px rgba(15,23,42,0.04);
  margin-bottom: 0.65rem;
  overflow: visible;
}
.chart-caption {
  font-size: 0.92rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  margin: 0 0 0.2rem 0 !important;
  line-height: 1.35 !important;
}
.chart-note {
  font-size: 0.76rem !important;
  color: #64748b !important;
  margin: 0 0 0.55rem 0 !important;
  line-height: 1.4 !important;
}

/* タブ：リッチなピル型セグメント */
div[data-testid="stTabs"] {
  margin-top: 0.15rem;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 0.3rem !important;
  flex-wrap: nowrap !important;
  overflow-x: auto !important;
  -webkit-overflow-scrolling: touch;
  background: linear-gradient(180deg, #0f172a 0%, #134e4a 100%) !important;
  border-radius: 16px !important;
  padding: 0.35rem !important;
  margin-bottom: 0.7rem !important;
  scrollbar-width: none;
  border: 1px solid rgba(15,118,110,0.25) !important;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 12px !important;
  padding: 0.65rem 0.9rem !important;
  border: none !important;
  color: #cbd5e1 !important;
  font-weight: 600 !important;
  font-size: 0.84rem !important;
  line-height: 1.25 !important;
  min-height: 44px !important;
  height: auto !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  overflow: visible !important;
}
.stTabs [data-baseweb="tab"] > div,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {
  overflow: visible !important;
  line-height: 1.25 !important;
  margin: 0 !important;
  color: inherit !important;
  font-size: inherit !important;
  font-weight: inherit !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #14b8a6 0%, #0f766e 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(20, 184, 166, 0.45) !important;
  border: none !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-border"] *,
.stTabs hr {
  display: none !important;
  height: 0 !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

/* スマホ（iPhone幅）：縦積み・小さめタイトルを強制 */
@media (max-width: 767px) {
  .block-container {
    padding-left: calc(0.7rem + var(--safe-left)) !important;
    padding-right: calc(0.7rem + var(--safe-right)) !important;
  }
  .hero { padding: 0.75rem 0.8rem 0.7rem; border-radius: 12px; }
  .hero-title { font-size: 1.0rem !important; }
  .hero-sub { font-size: 0.75rem !important; }
  .case-grid { grid-template-columns: 1fr !important; }
  .case-title { font-size: 0.92rem !important; }
  .case-desc { font-size: 0.75rem !important; }
  .case-row .v { font-size: 0.9rem !important; }
  .case-row.total .v { font-size: 1.1rem !important; }
  .js-plotly-plot, .plotly { max-width: 100% !important; }
}

/* 広い画面だけ2カラム */
@media (min-width: 900px) {
  .block-container { max-width: 920px !important; }
  .case-grid { grid-template-columns: 1fr 1fr !important; }
  .hero-title { font-size: 1.15rem !important; }
  .case-title { font-size: 1.0rem !important; }
  .section-head {
    flex-direction: row;
    align-items: baseline;
    justify-content: space-between;
  }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def yen(n) -> str:
    return f"{int(round(n)):,} 円"


def theme_chart(fig: go.Figure) -> go.Figure:
    """凡例は下。Plotlyタイトルは空文字にして undefined / 被りを防ぐ。"""
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(title=dict(text=""))
    fig.update_xaxes(gridcolor="rgba(15,23,42,0.05)", zeroline=False, showgrid=False)
    fig.update_yaxes(gridcolor="rgba(15,23,42,0.07)", zeroline=False, tickformat=",")
    return fig


def chart_panel(title: str, note: str = "") -> None:
    """チャート上の見出し（Plotlyタイトルは使わない）。"""
    note_html = f'<div class="chart-note">{note}</div>' if note else ""
    st.markdown(
        f"""
<div class="panel">
  <div class="chart-caption">{title}</div>
  {note_html}
</div>
        """,
        unsafe_allow_html=True,
    )

def get_edit_password() -> str:
    try:
        return str(st.secrets.get("EDIT_PASSWORD", "2640"))
    except Exception:
        return "2640"


inject_styles()

# --- 固定スケジュール ---
schedule_data = [
    (datetime.date(2024, 6, 30), 1000000), (datetime.date(2024, 7, 31), 400000),
    (datetime.date(2024, 8, 31), 400000),  (datetime.date(2024, 9, 30), 400000),
    (datetime.date(2024, 10, 31), 400000), (datetime.date(2024, 11, 30), 400000),
    (datetime.date(2024, 12, 31), 1500000), (datetime.date(2025, 1, 31), 400000),
    (datetime.date(2025, 2, 28), 400000),  (datetime.date(2025, 3, 31), 400000),
    (datetime.date(2025, 4, 30), 400000),  (datetime.date(2025, 5, 31), 400000),
    (datetime.date(2025, 6, 30), 1500000), (datetime.date(2025, 7, 31), 400000),
    (datetime.date(2025, 8, 31), 400000),  (datetime.date(2025, 9, 30), 400000),
    (datetime.date(2025, 10, 31), 400000), (datetime.date(2025, 11, 30), 400000),
    (datetime.date(2025, 12, 31), 1500000),
]
schedule_dict = {dt + datetime.timedelta(days=1): amt for dt, amt in schedule_data}
month_ends = [dt for dt, amt in schedule_data]
initial_principal = sum(amt for dt, amt in schedule_data)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "payments.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

default_payments = [
    {"入金日": "2024-11-07", "入金額(円)": 800000},
    {"入金日": "2024-11-16", "入金額(円)": 200000},
    {"入金日": "2024-12-12", "入金額(円)": 441491},
    {"入金日": "2025-03-31", "入金額(円)": 1000000},
    {"入金日": "2025-04-10", "入金額(円)": 150000},
    {"入金日": "2025-05-15", "入金額(円)": 300000},
    {"入金日": "2025-06-10", "入金額(円)": 368267},
    {"入金日": "2025-09-24", "入金額(円)": 420000},
    {"入金日": "2025-09-26", "入金額(円)": 1350676},
    {"入金日": "2025-11-11", "入金額(円)": 550000},
    {"入金日": "2025-11-25", "入金額(円)": 140000},
    {"入金日": "2026-02-06", "入金額(円)": 100000},
    {"入金日": "2026-02-27", "入金額(円)": 50000},
    {"入金日": "2026-05-19", "入金額(円)": 100000},
]

if not os.path.exists(CSV_FILE):
    pd.DataFrame(default_payments).to_csv(CSV_FILE, index=False, encoding="utf-8_sig")

df_base = pd.read_csv(CSV_FILE, encoding="utf-8_sig")
df_base["入金日"] = pd.to_datetime(df_base["入金日"]).dt.date

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            default_end_date = datetime.datetime.strptime(config_data.get("end_date"), "%Y-%m-%d").date()
    except Exception:
        default_end_date = datetime.date.today()
else:
    default_end_date = datetime.date.today()

# --- サイドバー（閲覧 / 編集） ---
if "editor_unlocked" not in st.session_state:
    st.session_state.editor_unlocked = False

st.sidebar.markdown("### 計算条件")
end_date = st.sidebar.date_input("計算基準日", default_end_date)

st.sidebar.markdown("#### 入金履歴")
can_edit = st.session_state.editor_unlocked

if not can_edit:
    st.sidebar.caption("閲覧専用です。編集は管理者のみ。")
    view_df = df_base.copy()
    view_df["入金額(円)"] = view_df["入金額(円)"].map(lambda x: f"{int(x):,}")
    st.sidebar.dataframe(view_df, hide_index=True, use_container_width=True, height=280)
    st.sidebar.markdown("---")
    with st.sidebar.expander("管理者ログイン（編集用）"):
        pwd = st.text_input("パスワード", type="password", key="edit_pwd")
        if st.button("編集を解除する", use_container_width=True):
            if pwd == get_edit_password():
                st.session_state.editor_unlocked = True
                st.rerun()
            else:
                st.error("パスワードが違います")
    df_payments_input = df_base.copy()
else:
    st.sidebar.caption("編集モード中。変更後に保存してください。")
    if st.sidebar.button("編集モードを終了", use_container_width=True):
        st.session_state.editor_unlocked = False
        st.rerun()
    df_payments_input = st.sidebar.data_editor(
        df_base,
        num_rows="dynamic",
        column_config={
            "入金日": st.column_config.DateColumn("入金日", required=True),
            "入金額(円)": st.column_config.NumberColumn("入金額(円)", min_value=0, required=True, format="%d"),
        },
        key="payment_editor",
        use_container_width=True,
    )
    if st.sidebar.button("変更を保存する", type="primary", use_container_width=True):
        df_to_save = df_payments_input.copy()
        df_to_save["入金日"] = df_to_save["入金日"].apply(
            lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else x
        )
        df_to_save.to_csv(CSV_FILE, index=False, encoding="utf-8_sig")
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"end_date": end_date.strftime("%Y-%m-%d")}, f, ensure_ascii=False, indent=4)
        st.sidebar.success("保存しました")
        st.rerun()

payments_dict = pd.Series(df_payments_input["入金額(円)"].values, index=df_payments_input["入金日"]).to_dict()


def run_simulation(target_end_date, pmts):
    current_principal = 0
    accumulated_damage = 0
    untruncated_damage = 0
    rate = 0.219

    total_payments_received = 0
    total_damage_generated = 0
    total_damage_paid = 0
    total_principal_paid = 0
    running_planned_principal = 0
    running_actual_payment = 0

    start_date = datetime.date(2024, 7, 1)
    current_date = start_date
    current_period_start = start_date
    history_logs = []
    daily_records = []

    while current_date <= target_end_date:
        if current_date in schedule_dict:
            running_planned_principal += schedule_dict[current_date]
            current_principal += schedule_dict[current_date]

        is_leap = current_date.year % 4 == 0 and (current_date.year % 100 != 0 or current_date.year % 400 == 0)
        days_in_year = 366 if is_leap else 365
        daily_damage = current_principal * rate / days_in_year
        untruncated_damage += daily_damage

        is_pay_day = current_date in pmts
        is_month_end = current_date in month_ends
        is_final_day = current_date == target_end_date

        allocated_damage_today = 0
        allocated_principal_today = 0
        payment_today = 0
        damage_added_today = 0

        if is_pay_day or is_month_end or is_final_day:
            damage_added_today = int(untruncated_damage)
            accumulated_damage += damage_added_today
            total_damage_generated += damage_added_today
            untruncated_damage = 0

            if is_pay_day:
                payment_today = pmts[current_date]
                running_actual_payment += payment_today
                total_payments_received += payment_today

                if payment_today <= accumulated_damage:
                    allocated_damage_today = payment_today
                    accumulated_damage -= payment_today
                else:
                    allocated_damage_today = accumulated_damage
                    allocated_principal_today = payment_today - accumulated_damage
                    current_principal -= allocated_principal_today
                    accumulated_damage = 0

                total_damage_paid += allocated_damage_today
                total_principal_paid += allocated_principal_today

            history_logs.append(
                {
                    "日付": current_date.strftime("%Y/%m/%d"),
                    "対象元本(円)": current_principal + allocated_principal_today,
                    "発生遅延金(円)": damage_added_today,
                    "入金額(円)": payment_today,
                    "遅延金充当(円)": allocated_damage_today,
                    "元本充当(円)": allocated_principal_today,
                    "未払い元本残高(円)": current_principal,
                    "未払い遅延金残高(円)": accumulated_damage,
                    "イベント": "入金" if is_pay_day else ("月末確定" if is_month_end else "最終日"),
                }
            )
            current_period_start = current_date + datetime.timedelta(days=1)

        daily_records.append(
            {
                "date": current_date,
                "予定累積元本": running_planned_principal,
                "実績累積入金": running_actual_payment,
                "未払い元本": current_principal,
                "未払い遅延金": accumulated_damage + untruncated_damage,
                "発生遅延金": daily_damage,
                "入金額": payment_today if is_pay_day else 0,
            }
        )
        current_date += datetime.timedelta(days=1)

    return (
        current_principal,
        accumulated_damage,
        total_payments_received,
        total_damage_generated,
        total_damage_paid,
        total_principal_paid,
        pd.DataFrame(history_logs),
        pd.DataFrame(daily_records),
    )


(
    final_principal,
    final_damage,
    total_pmt,
    total_dmg_gen,
    total_dmg_paid,
    total_prc_paid,
    df_history,
    df_daily,
) = run_simulation(end_date, payments_dict)

simple_remaining = initial_principal - total_pmt
settlement = final_principal + final_damage
case_gap = settlement - simple_remaining

# --- ヘッダー ---
st.markdown(
    f"""
<div class="hero">
  <div class="hero-kicker">Kashitsuke Monitor</div>
  <div class="hero-title">貸付モニタ</div>
  <p class="hero-sub">{end_date.strftime('%Y/%m/%d')}時点｜単純計算と遅延金込みを比較</p>
</div>
<div class="rules">
  <div class="rule-chip">遅延損害金 <strong>年21.9%</strong></div>
  <div class="rule-chip">充当順位 <strong>遅延金 → 元本</strong></div>
  <div class="rule-chip">端数 <strong>区間ごと切捨て</strong></div>
</div>
    """,
    unsafe_allow_html=True,
)

# --- 2ケース比較 ---
st.markdown(
    f"""
<div class="case-grid">
  <div class="case-card simple">
    <div class="case-label">CASE A</div>
    <div class="case-title">単純計算</div>
    <p class="case-desc">元本から支払済みを差し引くだけ（遅延金なし）</p>
    <div class="case-row"><span class="k">① 当初元本</span><span class="v">{yen(initial_principal)}</span></div>
    <div class="case-row"><span class="k">② 単純支払済み費用</span><span class="v">− {yen(total_pmt)}</span></div>
    <div class="case-row total"><span class="k">③ 単純残額（①−②）</span><span class="v">{yen(simple_remaining)}</span></div>
  </div>
  <div class="case-card delay">
    <div class="case-label">CASE B</div>
    <div class="case-title">遅延損害金込み</div>
    <p class="case-desc">遅延金を日割り計上し、遅延金→元本の順に充当</p>
    <div class="case-row"><span class="k">① 当初元本</span><span class="v">{yen(initial_principal)}</span></div>
    <div class="case-row"><span class="k">② 単純支払済み費用</span><span class="v">− {yen(total_pmt)}</span></div>
    <div class="case-row"><span class="k">③ 累計遅延損害金（発生総額）</span><span class="v">{yen(total_dmg_gen)}</span></div>
    <div class="case-row"><span class="k">④ 遅延損害金（残）<br><small>（発生総額 − すでに遅延金へ充当した分）<br>③ {yen(total_dmg_gen)} − {yen(total_dmg_paid)}</small></span><span class="v">{yen(final_damage)}</span></div>
    <div class="case-row"><span class="k">⑤ 未払い元本（残）<br><small>（単純残額 + 遅延金に回った入金）<br>{yen(simple_remaining)} + {yen(total_dmg_paid)}</small></span><span class="v">{yen(final_principal)}</span></div>
    <div class="case-row total"><span class="k">⑥ 一括精算額（④＋⑤）</span><span class="v">{yen(settlement)}</span></div>
  </div>
</div>
<div class="diff-note">
  <strong>⑤が大きく見える理由</strong><br>
  入金は先に遅延金へ回ります。遅延金に充てた {yen(total_dmg_paid)} は元本を減らせないため、<br>
  ⑤ = Case Aの単純残額 {yen(simple_remaining)} ＋ 遅延金に回った分 {yen(total_dmg_paid)} になります。
</div>
    """,
    unsafe_allow_html=True,
)

# --- グラフ・明細 ---
st.markdown(
    """
<div class="section-head">
  <div class="section-title">分析グラフ</div>
  <span>横にスワイプでタブ切替</span>
</div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["精算の比較", "⑤の内訳", "入金の行き先", "月次", "明細"]
)

with tab1:
    chart_panel("いま払うとすればいくらか", "Case A（単純）と Case B（遅延金込み）の比較")
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            name="単純残額（Case A）",
            x=["Case A 単純計算"],
            y=[simple_remaining],
            marker_color=C_TEAL,
            text=[yen(simple_remaining)],
            textposition="outside",
        )
    )
    fig1.add_trace(
        go.Bar(
            name="未払い元本（⑤）",
            x=["Case B 遅延金込み"],
            y=[final_principal],
            marker_color="#0ea5e9",
            text=[yen(final_principal)],
            textposition="inside",
        )
    )
    fig1.add_trace(
        go.Bar(
            name="遅延金残（④）",
            x=["Case B 遅延金込み"],
            y=[final_damage],
            marker_color=C_ORANGE,
            text=[yen(final_damage)],
            textposition="inside",
        )
    )
    theme_chart(fig1)
    fig1.update_layout(
        barmode="stack",
        yaxis_title="円",
        xaxis_title="",
        height=340,
        margin=dict(l=8, r=8, t=8, b=56),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    st.caption(f"Case Bの合計（⑥）= {yen(settlement)}　／　Case Aとの差 = {yen(case_gap)}")

with tab2:
    chart_panel(
        "なぜ⑤は単純残額より大きい？",
        "単純残額に、遅延金へ回った入金を足すと⑤になります",
    )
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=["単純残額\n(Case A)", "＋ 遅延金に\n回った入金", "＝ ⑤未払い\n元本"],
            y=[simple_remaining, total_dmg_paid, final_principal],
            marker_color=[C_TEAL, C_ORANGE, "#0ea5e9"],
            text=[yen(simple_remaining), yen(total_dmg_paid), yen(final_principal)],
            textposition="outside",
        )
    )
    theme_chart(fig2)
    fig2.update_layout(
        showlegend=False,
        yaxis_title="円",
        xaxis_title="",
        height=340,
        margin=dict(l=8, r=8, t=28, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.caption(
        f"{yen(simple_remaining)} + {yen(total_dmg_paid)} = {yen(final_principal)}"
    )

with tab3:
    chart_panel("入金はどこへ行ったか", f"入金総額 {yen(total_pmt)} の内訳")
    fig3 = go.Figure(
        data=[
            go.Pie(
                labels=["元本へ充当", "遅延金へ充当"],
                values=[total_prc_paid, total_dmg_paid],
                hole=0.55,
                marker=dict(colors=[C_TEAL, C_ORANGE]),
                textinfo="label+percent+value",
                texttemplate="%{label}<br>%{value:,.0f}円<br>(%{percent})",
                textfont=dict(size=12),
            )
        ]
    )
    theme_chart(fig3)
    fig3.update_layout(
        showlegend=False,
        margin=dict(l=8, r=8, t=8, b=8),
        height=320,
        title=dict(text=""),
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    col_a, col_b = st.columns(2)
    col_a.metric("元本へ充当", yen(total_prc_paid))
    col_b.metric("遅延金へ充当", yen(total_dmg_paid))

with tab4:
    chart_panel("月次：入金額と発生した遅延金", "青＝入金、オレンジ＝その月に新しく発生した遅延損害金")
    df_plot = df_daily.copy()
    df_plot["年月"] = df_plot["date"].apply(lambda x: x.strftime("%Y/%m"))
    df_monthly = df_plot.groupby("年月")[["発生遅延金", "入金額"]].sum().reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=df_monthly["年月"], y=df_monthly["入金額"], name="入金額", marker_color=C_TEAL))
    fig4.add_trace(
        go.Bar(x=df_monthly["年月"], y=df_monthly["発生遅延金"], name="発生遅延金", marker_color=C_ORANGE)
    )
    theme_chart(fig4)
    fig4.update_layout(barmode="group", yaxis_title="円", xaxis_title="", height=320)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

with tab5:
    st.caption("イベント発生日のみ（入金・月末確定・基準日）")
    st.dataframe(
        df_history[
            [
                "日付",
                "入金額(円)",
                "遅延金充当(円)",
                "元本充当(円)",
                "未払い元本残高(円)",
                "未払い遅延金残高(円)",
                "イベント",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=420,
    )
