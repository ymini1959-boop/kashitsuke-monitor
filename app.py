import datetime
import json
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="貸付モニタ | 充当計算ダッシュボード",
    page_icon="💠",
    initial_sidebar_state="expanded",
)

# ── カラー / チャート共通設定 ──
C_TEAL = "#0f766e"
C_TEAL_SOFT = "#99f6e4"
C_NAVY = "#0f172a"
C_SLATE = "#64748b"
C_ORANGE = "#ea580c"
C_RED = "#be123c"
C_GREEN = "#15803d"
C_BG = "#eef2f6"
C_CARD = "#ffffff"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans JP, sans-serif", color=C_NAVY, size=13),
    margin=dict(l=20, r=20, t=48, b=20),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)


def inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background:
    radial-gradient(ellipse 70% 45% at 10% -10%, rgba(15,118,110,0.12) 0%, transparent 55%),
    radial-gradient(ellipse 50% 35% at 100% 0%, rgba(15,23,42,0.06) 0%, transparent 50%),
    linear-gradient(180deg, #e2e8f0 0%, #eef2f6 140px, #eef2f6 100%) !important;
}

#MainMenu, footer { visibility: hidden !important; }

.block-container {
  padding-top: 1.1rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1180px !important;
}

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
}
[data-testid="stSidebar"] [data-testid="stCaption"] { color: #94a3b8 !important; }

div[data-testid="stMetric"] {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.06);
  border-radius: 16px;
  padding: 0.95rem 0.95rem 0.8rem;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
  min-height: 104px;
}
div[data-testid="stMetric"] label {
  color: #64748b !important;
  font-weight: 500 !important;
  white-space: normal !important;
  overflow: visible !important;
  line-height: 1.35 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  font-size: 1.35rem !important;
  white-space: nowrap !important;
  overflow: visible !important;
  line-height: 1.25 !important;
}

.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 55%, #0f766e 100%);
  color: #fff;
  border-radius: 22px;
  padding: 1.45rem 1.4rem 1.35rem;
  margin-bottom: 1.15rem;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.22);
}
.hero::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -8%;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgba(45,212,191,0.35) 0%, transparent 65%);
  pointer-events: none;
}
.hero-kicker {
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #99f6e4;
  font-weight: 600;
  margin-bottom: 0.35rem;
}
.hero-title {
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 0.35rem 0;
  line-height: 1.3;
}
.hero-sub {
  color: #cbd5e1;
  font-size: 0.92rem;
  margin: 0 0 1rem 0;
  line-height: 1.55;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 0.75rem;
}
@media (max-width: 780px) {
  .hero-grid { grid-template-columns: 1fr; }
  .hero-title { font-size: 1.28rem; }
}
.hero-pill {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  backdrop-filter: blur(8px);
}
.hero-pill.primary {
  background: rgba(45,212,191,0.16);
  border-color: rgba(45,212,191,0.35);
}
.hero-pill-label {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 0.2rem;
}
.hero-pill.primary .hero-pill-label { color: #99f6e4; }
.hero-pill-value {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.hero-pill.primary .hero-pill-value { font-size: 1.55rem; color: #ecfdf5; }

.rules {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.25rem 0 1.1rem;
}
.rule-chip {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.08);
  color: #334155;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.4rem 0.7rem;
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.04);
}
.rule-chip strong { color: #0f766e; font-weight: 700; }

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0.4rem 0 0.75rem;
}
.section-head h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}
.section-head span {
  color: #64748b;
  font-size: 0.82rem;
}

.panel {
  background: #fff;
  border: 1px solid rgba(15,23,42,0.06);
  border-radius: 18px;
  padding: 0.85rem 1rem 0.4rem;
  box-shadow: 0 8px 24px rgba(15,23,42,0.05);
  margin-bottom: 0.85rem;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.35rem;
  background: transparent;
}
.stTabs [data-baseweb="tab"] {
  background: #fff;
  border-radius: 999px !important;
  padding: 0.45rem 0.95rem;
  border: 1px solid rgba(15,23,42,0.08);
  color: #475569;
  font-weight: 600;
}
.stTabs [aria-selected="true"] {
  background: #0f766e !important;
  color: #fff !important;
  border-color: #0f766e !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def yen(n) -> str:
    return f"{int(round(n)):,} 円"


def apply_chart_theme(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=15, color=C_NAVY)) if title else None)
    fig.update_xaxes(gridcolor="rgba(15,23,42,0.06)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(15,23,42,0.06)", zeroline=False, tickformat=",")
    return fig


inject_styles()

# --- 1. 固定データ（返済予定表） ---
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

# --- 2. 保存ファイル ---
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

# --- 3. サイドバー ---
st.sidebar.markdown("### 計算条件")
st.sidebar.caption("基準日と入金履歴を更新すると、残高が一括で再計算されます。")
end_date = st.sidebar.date_input("計算基準日（一括精算日）", default_end_date)

st.sidebar.markdown("#### 入金履歴")
st.sidebar.caption("行追加・編集のあと、必ず保存してください。")
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
    df_to_save["入金日"] = df_to_save["入金日"].apply(lambda x: x.strftime("%Y-%m-%d") if hasattr(x, "strftime") else x)
    df_to_save.to_csv(CSV_FILE, index=False, encoding="utf-8_sig")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"end_date": end_date.strftime("%Y-%m-%d")}, f, ensure_ascii=False, indent=4)
    st.sidebar.success("保存しました")
    st.rerun()

payments_dict = pd.Series(df_payments_input["入金額(円)"].values, index=df_payments_input["入金日"]).to_dict()


# --- 4. コア計算 ---
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
                    "期間": f"{current_period_start.strftime('%m/%d')}～{current_date.strftime('%m/%d')}",
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

settlement = final_principal + final_damage
recovery_rate = (total_prc_paid / initial_principal) * 100 if initial_principal else 0

# --- 5. ヒーロー ---
st.markdown(
    f"""
<div class="hero">
  <div class="hero-kicker">Kashitsuke Monitor</div>
  <h1 class="hero-title">金銭消費貸借 充当計算ダッシュボード</h1>
  <p class="hero-sub">返済予定と入金実績から、遅延損害金・未払い残高・一括精算額を日割りで可視化します。</p>
  <div class="hero-grid">
    <div class="hero-pill primary">
      <div class="hero-pill-label">いま必要な一括精算額（{end_date.strftime('%Y/%m/%d')}時点）</div>
      <div class="hero-pill-value">{yen(settlement)}</div>
    </div>
    <div class="hero-pill">
      <div class="hero-pill-label">未払い元本</div>
      <div class="hero-pill-value">{yen(final_principal)}</div>
    </div>
    <div class="hero-pill">
      <div class="hero-pill-label">未払い遅延損害金</div>
      <div class="hero-pill-value">{yen(final_damage)}</div>
    </div>
  </div>
</div>
<div class="rules">
  <div class="rule-chip">遅延損害金 <strong>年21.9%</strong></div>
  <div class="rule-chip">充当順位 <strong>遅延金 → 元本</strong></div>
  <div class="rule-chip">端数 <strong>区間ごと切捨て</strong></div>
  <div class="rule-chip">うるう年は <strong>366日</strong></div>
</div>
    """,
    unsafe_allow_html=True,
)

# --- 6. KPI ---
st.markdown(
    f"""
<div class="section-head">
  <h3>契約サマリー</h3>
  <span>契約総額とこれまでの累積実績</span>
</div>
    """,
    unsafe_allow_html=True,
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("当初元本", yen(initial_principal))
c2.metric("入金総額", yen(total_pmt))
c3.metric("発生した遅延損害金", yen(total_dmg_gen))
c4.metric("元本回収率", f"{recovery_rate:.1f}%")

# --- 7. タブ分析 ---
st.markdown(
    """
<div class="section-head">
  <h3>詳細分析</h3>
  <span>残高・充当・計画ギャップを確認</span>
</div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["残高推移", "充当内訳", "予定と実績", "月次比較", "計算明細"]
)

with tab1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["未払い元本"],
            mode="lines",
            name="未払い元本",
            line=dict(color=C_TEAL, width=3),
            fill="tozeroy",
            fillcolor="rgba(15,118,110,0.08)",
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["未払い遅延金"],
            mode="lines",
            name="未払い遅延損害金",
            line=dict(color=C_ORANGE, width=3),
        )
    )
    apply_chart_theme(fig1, "未払い残高の時系列推移")
    fig1.update_layout(xaxis_title="", yaxis_title="金額（円）")
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=["元本へ充当", "遅延損害金へ充当"],
                    values=[total_prc_paid, total_dmg_paid],
                    hole=0.58,
                    marker=dict(colors=[C_TEAL, C_ORANGE]),
                    textinfo="label+percent",
                )
            ]
        )
        apply_chart_theme(fig_pie, "入金の使途内訳")
        fig_pie.update_layout(showlegend=False, margin=dict(t=48, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=recovery_rate,
                number={"suffix": "%", "font": {"size": 36}},
                title={"text": "元本回収進捗", "font": {"size": 15}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": C_TEAL},
                    "bgcolor": "#f1f5f9",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50], "color": "#ffe4e6"},
                        {"range": [50, 80], "color": "#ffedd5"},
                        {"range": [80, 100], "color": "#ccfbf1"},
                    ],
                },
            )
        )
        apply_chart_theme(fig_gauge)
        fig_gauge.update_layout(margin=dict(t=40, b=10, l=20, r=20), height=320)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    fig_gap = go.Figure()
    fig_gap.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["予定累積元本"],
            mode="lines",
            name="契約上の予定累積",
            line=dict(color=C_SLATE, width=2, dash="dash"),
        )
    )
    fig_gap.add_trace(
        go.Scatter(
            x=df_daily["date"],
            y=df_daily["実績累積入金"],
            mode="lines",
            name="実際の累積入金",
            fill="tonexty",
            fillcolor="rgba(190,18,60,0.08)",
            line=dict(color=C_GREEN, width=3),
        )
    )
    apply_chart_theme(fig_gap, "予定と実績のギャップ（網掛け＝遅れ）")
    fig_gap.update_layout(xaxis_title="", yaxis_title="金額（円）")
    st.plotly_chart(fig_gap, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    df_plot = df_daily.copy()
    df_plot["年月"] = df_plot["date"].apply(lambda x: x.strftime("%Y/%m"))
    df_monthly = df_plot.groupby("年月")[["発生遅延金", "入金額"]].sum().reset_index()
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=df_monthly["年月"], y=df_monthly["入金額"], name="入金額", marker_color=C_TEAL))
    fig_monthly.add_trace(
        go.Bar(x=df_monthly["年月"], y=df_monthly["発生遅延金"], name="発生遅延金", marker_color=C_ORANGE)
    )
    apply_chart_theme(fig_monthly, "月次：入金 vs 発生遅延金")
    fig_monthly.update_layout(barmode="group", xaxis_title="", yaxis_title="金額（円）")
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.caption("日割り充当計算の明細（イベント発生日のみ）")
    st.dataframe(
        df_history[
            [
                "日付",
                "対象元本(円)",
                "発生遅延金(円)",
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
