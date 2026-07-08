import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import os
import json

# 画面をワイドモードに設定
st.set_page_config(layout="wide", page_title="金銭消費貸借 充当計算総合ダッシュボード")

st.title("📊 金銭消費貸借契約 充当計算＆多角分析ダッシュボード")
st.caption("【計算ルール】遅延損害金: 年 21.9%（うるう年366日） / 充当順位: 遅延損害金 ➔ 滞納元本（法定充当） / 端数処理: 区間ごと切り捨て")

# --- 1. 固定データ（返済予定表）の定義 ---
schedule_data = [
    (datetime.date(2024, 6, 30), 1000000), (datetime.date(2024, 7, 31), 400000),
    (datetime.date(2024, 8, 31), 400000),  (datetime.date(2024, 9, 30), 400000),
    (datetime.date(2024, 10, 31), 400000), (datetime.date(2024, 11, 30), 400000),
    (datetime.date(2024, 12, 31), 1500000),(datetime.date(2025, 1, 31), 400000),
    (datetime.date(2025, 2, 28), 400000),  (datetime.date(2025, 3, 31), 400000),
    (datetime.date(2025, 4, 30), 400000),  (datetime.date(2025, 5, 31), 400000),
    (datetime.date(2025, 6, 30), 1500000),(datetime.date(2025, 7, 31), 400000),
    (datetime.date(2025, 8, 31), 400000),  (datetime.date(2025, 9, 30), 400000),
    (datetime.date(2025, 10, 31), 400000), (datetime.date(2025, 11, 30), 400000),
    (datetime.date(2025, 12, 31), 1500000)
]
schedule_dict = {dt + datetime.timedelta(days=1): amt for dt, amt in schedule_data}
month_ends = [dt for dt, amt in schedule_data]
initial_principal = sum(amt for dt, amt in schedule_data)

# --- 2. 保存用ファイルのパス設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "payments.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# 初回起動時（CSVがない場合）の初期入金データ
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

# CSVファイルが存在しない場合は初期データで作成
if not os.path.exists(CSV_FILE):
    pd.DataFrame(default_payments).to_csv(CSV_FILE, index=False, encoding="utf-8_sig")

# CSVファイルからデータを読み込み
df_base = pd.read_csv(CSV_FILE, encoding="utf-8_sig")
df_base["入金日"] = pd.to_datetime(df_base["入金日"]).dt.date

# 【機能追加】保存された計算基準日を読み込む（なければ「本日」をデフォルトに）
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            default_end_date = datetime.datetime.strptime(config_data.get("end_date"), "%Y-%m-%d").date()
    except:
        default_end_date = datetime.date.today()
else:
    default_end_date = datetime.date.today()

# --- 3. サイドバー・条件設定 ---
st.sidebar.header("⚙️ 計算条件・返済実績の追加")

# 計算基準日を入力（デフォルトは保存データ、または当日日付）
end_date = st.sidebar.date_input("計算基準日（一括精算日）", default_end_date)

st.sidebar.subheader("📝 入金履歴の編集/追加")
st.sidebar.write("データ変更や基準日を変更した後は、必ず下の保存ボタンを押してください。")

# データエディタを表示
df_payments_input = st.sidebar.data_editor(
    df_base,
    num_rows="dynamic",
    column_config={
        "入金日": st.column_config.DateColumn("入金日", required=True),
        "入金額(円)": st.column_config.NumberColumn("入金額(円)", min_value=0, required=True, format="%d")
    },
    key="payment_editor"
)

# 💾 【機能改良】保存ボタンを押すと、入金履歴と計算基準日を同時にMacへ保存
if st.sidebar.button("💾 編集内容と基準日をファイルに保存する", type="primary"):
    # 1. 入金履歴をCSVに保存
    df_to_save = df_payments_input.copy()
    df_to_save["入金日"] = df_to_save["入金日"].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x)
    df_to_save.to_csv(CSV_FILE, index=False, encoding="utf-8_sig")
    
    # 2. 計算基準日をJSONに保存
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"end_date": end_date.strftime('%Y-%m-%d')}, f, ensure_ascii=False, indent=4)
        
    st.sidebar.success("入金履歴と計算基準日をデスクトップに保存しました！")
    st.rerun()

# 入金データを計算用辞書に変換
payments_dict = pd.Series(df_payments_input['入金額(円)'].values, index=df_payments_input['入金日']).to_dict()

# --- 4. コア計算ロジック（日割りシミュレーション） ---
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
            
        is_leap = (current_date.year % 4 == 0 and (current_date.year % 100 != 0 or current_date.year % 400 == 0))
        days_in_year = 366 if is_leap else 365
        daily_damage = current_principal * rate / days_in_year
        untruncated_damage += daily_damage
        
        is_pay_day = current_date in pmts
        is_month_end = current_date in month_ends
        is_final_day = (current_date == target_end_date)
        
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
                
            log_entry = {
                "日付": current_date.strftime('%Y/%m/%d'),
                "期間": f"{current_period_start.strftime('%m/%d')}～{current_date.strftime('%m/%d')}",
                "対象元本(円)": current_principal + allocated_principal_today,
                "発生遅延金(円)": damage_added_today,
                "入金額(円)": payment_today,
                "遅延金充当(円)": allocated_damage_today,
                "元本充当(円)": allocated_principal_today,
                "未払い元本残高(円)": current_principal,
                "未払い遅延金残高(円)": accumulated_damage,
                "イベント": "入金" if is_pay_day else ("月末確定" if is_month_end else "最終日")
            }
            history_logs.append(log_entry)
            current_period_start = current_date + datetime.timedelta(days=1)
            
        daily_records.append({
            "date": current_date,
            "予定累積元本": running_planned_principal,
            "実績累積入金": running_actual_payment,
            "未払い元本": current_principal,
            "未払い遅延金": accumulated_damage + untruncated_damage,
            "発生遅延金": daily_damage,
            "入金額": payment_today if is_pay_day else 0
        })
        
        current_date += datetime.timedelta(days=1)
        
    return (current_principal, accumulated_damage, total_payments_received, 
            total_damage_generated, total_damage_paid, total_principal_paid,
            pd.DataFrame(history_logs), pd.DataFrame(daily_records))

# シミュレーション実行
(final_principal, final_damage, total_pmt, total_dmg_gen, 
 total_dmg_paid, total_prc_paid, df_history, df_daily) = run_simulation(end_date, payments_dict)

# --- 5. 画面描画（KPIサマリー表示） ---
st.subheader("📊 契約内容とこれまでの累積実績（トータル）")
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric(label="📄 当初元本（契約総額）", value=f"{initial_principal:,} 円")
with col_stat2:
    st.metric(label="🟢 これまでの支払い実績総額（入金総額）", value=f"{total_pmt:,} 円")
with col_stat3:
    st.metric(label="⚠️ これまでに発生した遅延損害金の総額", value=f"{total_dmg_gen:,} 円")

st.subheader("⏳ 現時点での未払い残高内訳")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🔴 現在の未払い元本残高", value=f"{final_principal:,} 円")
with col2:
    st.metric(label="⏳ 支払いを待っている遅延損害金（残額）", value=f"{final_damage:,} 円")
with col3:
    st.metric(label="💰 現時点の一括精算合計額", value=f"{final_principal + final_damage:,} 円", delta="一括精算請求額")

st.markdown("---")

# --- 6. 多角分析タブの配置 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 残高推移 (元本vs遅延金)", 
    "🍰 充当内訳 & 回収率", 
    "📉 予定vs実績ギャップ", 
    "📅 月次ペナルティ推移", 
    "📋 充当計算明細表"
])

with tab1:
    st.subheader("未払い残高の時系列推移")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["未払い元本"], mode='lines', name='未払い元本残高', line=dict(color='#1f77b4', width=3)))
    fig1.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["未払い遅延金"], mode='lines', name='未払い遅延損害金', line=dict(color='#ff7f0e', width=3)))
    fig1.update_layout(hovermode="x unified", xaxis_title="日付", yaxis_title="金額（円）")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("支払金のゆくえ ＆ 元本回収ステータス")
    col_tab2_left, col_tab2_right = st.columns(2)
    with col_tab2_left:
        fig_pie = go.Figure(data=[go.Pie(labels=['元本返済に充当', '遅延損害金の消化'], values=[total_prc_paid, total_dmg_paid], hole=.4, marker=dict(colors=['#2ca02c', '#d62728']))])
        fig_pie.update_layout(title_text="これまでに入金された総額の使途内訳", legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_tab2_right:
        recovery_rate = (total_prc_paid / initial_principal) * 100
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=recovery_rate, title={'text': "当初元本の回収進捗率 (%)"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1f77b4"}, 'steps': [{'range': [0, 50], 'color': "#ffcccb"}, {'range': [50, 80], 'color': "#fff3cd"}, {'range': [80, 100], 'color': "#d4edda"}],}))
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab3:
    st.subheader("契約上の返済計画と実際の入金累積の乖離（ギャップ）")
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["予定累積元本"], mode='lines', name='契約上の予定累積元本', line=dict(color='#7f7f7f', width=2, dash='dash')))
    fig_gap.add_trace(go.Scatter(x=df_daily["date"], y=df_daily["実績累積入金"], mode='lines', name='実際の累積入金額', fill='tonexty', fillcolor='rgba(214, 39, 40, 0.1)', line=dict(color='#2ca02c', width=3)))
    fig_gap.update_layout(hovermode="x unified", title="網掛けエリアが「返済の遅れ（滞納規模）」を示します", xaxis_title="日付", yaxis_title="金額（円）")
    st.plotly_chart(fig_gap, use_container_width=True)

with tab4:
    st.subheader("月別の実績データ（発生遅延損害金 vs 実際の入金額）")
    df_daily['年月'] = df_daily['date'].apply(lambda x: x.strftime('%Y/%m'))
    df_monthly = df_daily.groupby('年月')[['発生遅延金', '入金額']].sum().reset_index()
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=df_monthly["年月"], y=df_monthly["入金額"], name="当月の入金額", marker_color='#2ca02c'))
    fig_monthly.add_trace(go.Bar(x=df_monthly["年月"], y=df_monthly["発生遅延金"], name="当月の新発生遅延金", marker_color='#ff7f0e'))
    fig_monthly.update_layout(barmode='group', hovermode="x unified", title="後半、入金額が損害金（オレンジ）を下回り、破綻しているのが分かります", xaxis_title="年月", yaxis_title="金額（円）")
    st.plotly_chart(fig_monthly, use_container_width=True)

with tab5:
    st.subheader("日割り充当計算の明細一覧（裁判提出用・エビデンスベース）")
    st.dataframe(df_history[["日付", "対象元本(円)", "発生遅延金(円)", "入金額(円)", "遅延金充当(円)", "元本充当(円)", "未払い元本残高(円)", "未払い遅延金残高(円)", "イベント"]], use_container_width=True, hide_index=True)