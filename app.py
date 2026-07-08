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
    font=dict(family="Noto Sans JP, -apple-system, sans-serif", color=C_NAVY, size=14),
    margin=dict(l=4, r=4, t=40, b=4),
    hovermode="x unified",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
    height=320,
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

.hero {
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 55%, #0f766e 100%);
  color: #fff;
  border-radius: 18px;
  padding: 1.15rem 1.05rem 1.05rem;
  margin-bottom: 0.85rem;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.2);
}
.hero-kicker {
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #99f6e4;
  font-weight: 600;
  margin-bottom: 0.3rem;
}
.hero-title {
  font-size: 1.28rem;
  font-weight: 700;
  margin: 0 0 0.4rem 0;
  letter-spacing: -0.02em;
  line-height: 1.35;
}
.hero-sub {
  color: #cbd5e1;
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.55;
}

.case-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin: 0.75rem 0 0.85rem;
}
.case-card {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.07);
  border-radius: 16px;
  padding: 1rem 1rem 0.95rem;
  box-shadow: 0 8px 22px rgba(15,23,42,0.05);
}
.case-card.simple { border-top: 4px solid #0f766e; }
.case-card.delay { border-top: 4px solid #ea580c; }
.case-label {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 0.25rem;
}
.case-card.simple .case-label { color: #0f766e; }
.case-card.delay .case-label { color: #ea580c; }
.case-title {
  font-size: 1.12rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.4rem 0;
  line-height: 1.35;
}
.case-desc {
  font-size: 0.92rem;
  color: #64748b;
  margin: 0 0 0.85rem 0;
  line-height: 1.5;
}
.case-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.98rem;
  line-height: 1.4;
}
.case-row:last-child { border-bottom: none; padding-bottom: 0; }
.case-row .k { color: #64748b; flex: 1; min-width: 0; }
.case-row .v {
  color: #0f172a;
  font-weight: 700;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  font-size: 1.02rem;
}
.case-row.total {
  margin-top: 0.25rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
  border-bottom: none;
  align-items: center;
}
.case-row.total .k { color: #0f172a; font-weight: 700; font-size: 1rem; }
.case-row.total .v {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.case-card.simple .case-row.total .v { color: #0f766e; }
.case-card.delay .case-row.total .v { color: #c2410c; }
.diff-note {
  margin-top: 0.15rem;
  margin-bottom: 1rem;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #9a3412;
  border-radius: 12px;
  padding: 0.85rem 0.95rem;
  font-size: 0.95rem;
  line-height: 1.55;
}
.diff-note strong { font-weight: 700; font-size: 1.05rem; }

.rules {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0 0 0.75rem;
}
.rule-chip {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.08);
  color: #334155;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 0.42rem 0.7rem;
  border-radius: 999px;
  line-height: 1.3;
}
.rule-chip strong { color: #0f766e; }

.section-head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
  margin: 0.15rem 0 0.55rem;
}
.section-head h3 {
  margin: 0;
  font-size: 1.12rem;
  font-weight: 700;
  color: #0f172a;
}
.section-head span { color: #64748b; font-size: 0.88rem; }

.panel {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.06);
  border-radius: 16px;
  padding: 0.45rem 0.45rem 0.15rem;
  box-shadow: 0 6px 18px rgba(15,23,42,0.04);
  margin-bottom: 0.7rem;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.35rem;
  flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
  background: #fff;
  border-radius: 999px !important;
  padding: 0.55rem 0.95rem !important;
  border: 1px solid rgba(15,23,42,0.08);
  color: #475569;
  font-weight: 600;
  font-size: 0.95rem !important;
  min-height: 44px;
}
.stTabs [aria-selected="true"] {
  background: #0f766e !important;
  color: #fff !important;
  border-color: #0f766e !important;
}

/* スマホ向け：フォントと余白をさらに読みやすく */
@media (max-width: 640px) {
  .hero-title { font-size: 1.35rem; }
  .hero-sub { font-size: 1rem; }
  .case-title { font-size: 1.18rem; }
  .case-desc { font-size: 0.98rem; }
  .case-row { font-size: 1.02rem; padding: 0.62rem 0; }
  .case-row .v { font-size: 1.08rem; }
  .case-row.total .v { font-size: 1.55rem; }
  .diff-note { font-size: 1rem; }
  .rule-chip { font-size: 0.88rem; }
  .section-head h3 { font-size: 1.18rem; }
  .stTabs [data-baseweb="tab"] {
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
  }
}

/* タブレット以上は2カラム */
@media (min-width: 820px) {
  .block-container { max-width: 980px !important; }
  .case-grid { grid-template-columns: 1fr 1fr; }
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


def theme_chart(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=C_NAVY)) if title else None,
    )
    fig.update_xaxes(gridcolor="rgba(15,23,42,0.05)", zeroline=False, showgrid=False)
    fig.update_yaxes(gridcolor="rgba(15,23,42,0.07)", zeroline=False, tickformat=",")
    return fig


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
  <h1 class="hero-title">金銭消費貸借 充当計算ダッシュボード</h1>
  <p class="hero-sub">{end_date.strftime('%Y/%m/%d')} 時点｜単純計算と遅延損害金込みの精算額を並べて確認できます。</p>
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
    <h2 class="case-title">単純計算（遅延金なし）</h2>
    <p class="case-desc">当初元本から、支払済み総額をそのまま差し引きます。</p>
    <div class="case-row"><span class="k">① 当初元本</span><span class="v">{yen(initial_principal)}</span></div>
    <div class="case-row"><span class="k">② 単純支払済み費用</span><span class="v">− {yen(total_pmt)}</span></div>
    <div class="case-row total"><span class="k">③ 単純残額（①−②）</span><span class="v">{yen(simple_remaining)}</span></div>
  </div>
  <div class="case-card delay">
    <div class="case-label">CASE B</div>
    <h2 class="case-title">遅延損害金ケース（法定充当）</h2>
    <p class="case-desc">日割りの遅延損害金を発生させ、入金を遅延金→元本の順に充当します。</p>
    <div class="case-row"><span class="k">未払い元本</span><span class="v">{yen(final_principal)}</span></div>
    <div class="case-row"><span class="k">未払い遅延損害金</span><span class="v">{yen(final_damage)}</span></div>
    <div class="case-row"><span class="k">発生した遅延損害金（累計）</span><span class="v">{yen(total_dmg_gen)}</span></div>
    <div class="case-row total"><span class="k">一括精算額</span><span class="v">{yen(settlement)}</span></div>
  </div>
</div>
<div class="diff-note">
  両ケースの差：<strong>{yen(case_gap)}</strong><br>
  単純残額 {yen(simple_remaining)} に対し、遅延損害金込みだと {yen(settlement)} になります。
  差は「遅延損害金の影響」です。
</div>
    """,
    unsafe_allow_html=True,
)

# --- シンプルなグラフ（2タブ） ---
st.markdown(
    """
<div class="section-head">
  <h3>推移グラフ</h3>
  <span>必要最低限の2つ</span>
</div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["残高の推移", "予定と実績", "計算明細"])

with tab1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["未払い元本"],
            mode="lines",
            name="未払い元本",
            line=dict(color=C_TEAL, width=2.5),
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["未払い遅延金"],
            mode="lines",
            name="未払い遅延金",
            line=dict(color=C_ORANGE, width=2.5),
        )
    )
    theme_chart(fig1, "未払い元本と遅延金")
    fig1.update_layout(yaxis_title="円", xaxis_title="")
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["予定累積元本"],
            mode="lines",
            name="予定累積",
            line=dict(color=C_SLATE, width=2, dash="dot"),
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["実績累積入金"],
            mode="lines",
            name="実績入金",
            line=dict(color=C_GREEN, width=2.5),
        )
    )
    theme_chart(fig2, "予定累積 vs 実績入金")
    fig2.update_layout(yaxis_title="円", xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
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
