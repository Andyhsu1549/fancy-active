import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, date

# ------------------ 基本設定 ------------------
st.set_page_config(
    page_title="🌟 Streamlit 商業應用展示工具 🌟",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 更新為更亮的顏色主題
PRIMARY = "#6366F1"  # Indigo-500 (比 600 更亮)
ACCENT = "#22D3EE"   # Cyan-400 (更亮)
LIGHT = "#F0F9FF"
DARK = "#0F172A"

CUSTOM_CSS = f"""
<style>
    .big-title {{
        font-size: 2.4rem; font-weight: 900; margin-bottom: .4rem; color: {PRIMARY}; text-align:center;
    }}
    .sub-title {{
        font-size: 1.1rem; color: {ACCENT}; margin-bottom: 1.5rem; text-align:center;
    }}
    .pill {{
        display:inline-block; padding:.15rem .6rem; border-radius:9999px; background:{PRIMARY}; color:white; font-size:.8rem; margin-right:.4rem;
    }}
    .card {{
        background: white; border:1px solid #e5e7eb; border-radius: 16px; padding: 16px; box-shadow: 0 4px 16px rgba(2,6,23,.05);
    }}
    .mute {{ color:#64748B; }}
    .kpi {{ font-size: 1.6rem; font-weight: 700; color: {PRIMARY}; }}
    .footer {{ color:#94A3B8; font-size:.9rem; margin-top:.5rem; text-align:center; }}
    .btn-primary button {{ background:{PRIMARY} !important; border-color:{PRIMARY} !important; }}
    .btn-accent button {{ background:{ACCENT} !important; border-color:{ACCENT} !important; }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------ 頁面標題 ------------------
st.markdown("<div class='big-title'>🌟 Streamlit 商業應用展示工具 🌟</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>讓資料、流程與決策更簡單 · 更快速 · 更美觀</div>", unsafe_allow_html=True)

# ------------------ 側邊導航 ------------------
with st.sidebar:
    st.image("https://static.streamlit.io/examples/dice.jpg", caption="快速將想法變成 App", use_container_width=True)
    st.markdown("### 導航")
    page = st.radio(
        "選擇頁面",
        [
            "總覽",
            "商業情境",
            "即時展示",
            "ROI 試算",
            "元件展覽",
            "資料 App 範本",
            "FAQ / 交付與維運",
        ],
        index=0,
    )

    st.divider()
    st.markdown("#### 快速操作")
    if st.button("重新載入資料樣本", use_container_width=True):
        st.cache_data.clear()
        st.success("已清除快取，資料將於下一次載入！")

    st.markdown("#### 選項")
    dark = st.toggle("深色風格（僅部分）")

# ------------------ 實用輔助 ------------------
@st.cache_data(show_spinner=False)
def load_demo_data(rows: int = 200):
    np.random.seed(42)
    df = pd.DataFrame({
        "日期": pd.date_range(date.today().replace(day=1), periods=rows, freq="D"),
        "通路": np.random.choice(["官網", "門市", "經銷", "B2B"], size=rows),
        "品類": np.random.choice(["A 系列", "B 系列", "C 系列"], size=rows),
        "成本": np.random.randint(50, 200, size=rows),
        "售價": np.random.randint(120, 380, size=rows),
        "數量": np.random.randint(1, 12, size=rows),
    })
    df["營收"] = df["售價"] * df["數量"]
    df["毛利"] = df["營收"] - (df["成本"] * df["數量"])
    return df


def kpi_card(label: str, value: str, help_text: str = ""):
    with st.container(border=True):
        st.markdown(f"<div class='mute'>{label}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi'>{value}</div>", unsafe_allow_html=True)
        if help_text:
            st.caption(help_text)


# ------------------ 各頁面 ------------------
if page == "總覽":

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("開發速度", "x10", "以 Python 直寫，免前端框架。")
    with c2:
        kpi_card("上線時間", "數小時", "Prototype 到 PoC 速度快。")
    with c3:
        kpi_card("維護成本", "低", "單一語言、少依賴。")
    with c4:
        kpi_card("商務價值", "可量化", "決策更快、報表更活。")

    st.divider()

    l, r = st.columns([1.2, 1])
    with l:
        st.subheader("什麼是 Streamlit？")
        st.write(
            """
            - 開源、雲端友善：以 **Python** 為主，資料團隊即可開發。
            - 元件齊全：表格、圖表、上傳、下載、表單、狀態管理。
            - 擴充彈性：可嵌入 LLM、API、資料庫，支援單點登入（企業版）。
            - 交付快速：從 Jupyter/Spyder 原型，**一鍵轉為互動式 App**。
            """
        )
        with st.expander("我們提供的服務內容"):
            st.markdown("""
            1) 需求釐清與資訊架構設計  
            2) UI/UX 雛形與資料流程設計  
            3) 開發與串接（資料庫/Excel/API/LLM）  
            4) 部署（雲端/內網）與權限管理  
            5) 交付文件、教育訓練與維運支援
            """)
    with r:
        with st.container(border=True):
            st.markdown("**快速示例：上傳 Excel → KPI 卡片**")
            up = st.file_uploader("上傳 Excel/CSV", type=["xlsx", "csv"])
            if up:
                df = pd.read_excel(up) if up.name.endswith("xlsx") else pd.read_csv(up)
            else:
                df = load_demo_data(60)
            st.dataframe(df.head(10), use_container_width=True)
            st.caption("*示例資料會自動產生，亦可上傳真實檔案*")

elif page == "商業情境":
    st.subheader("常見商業情境與價值")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 1) 內部儀表板 / 營運看板")
            st.write("多資料源彙整、權限控管、即時 KPI")
            st.markdown("- 例：銷售、庫存、客服、財務指標")
            if st.button("🔎 範例 KPI", key="biz_kpi", use_container_width=True):
                df = load_demo_data(120)
                m1, m2, m3 = st.columns(3)
                kpi_card("月營收", f"{int(df['營收'].sum()):,}")
                kpi_card("毛利率", f"{df['毛利'].sum() / df['營收'].sum():.1%}")
                kpi_card("單筆客單價", f"{int(df['營收'].mean()):,}")

        with st.container(border=True):
            st.markdown("### 2) 客製報價 / 專案估算")
            st.write("將 Excel 報價單流程化、集中化，降低錯誤")
            with st.form("quote_form", clear_on_submit=False):
                qty = st.number_input("數量", 1, 1000, 10)
                unit = st.number_input("單價", 0, 100000, 380)
                disc = st.slider("折扣(%)", 0, 50, 10)
                tax = st.toggle("含稅 5%")
                ok = st.form_submit_button("計算")
                if ok:
                    subtotal = qty * unit
                    total = subtotal * (1 - disc/100) * (1.05 if tax else 1)
                    st.success(f"報價總計：{total:,.0f}")

    with col2:
        with st.container(border=True):
            st.markdown("### 3) 流程自動化 / 文件產製")
            st.write("將 PDF/Word/Excel的重複任務按鈕化，一鍵生成")
            st.markdown("- 例：對帳、合約套版、型錄生成、稽核紀錄")
            if st.button("⚙️ 觸發自動化範例", use_container_width=True):
                with st.spinner("處理中..."):
                    time.sleep(1.2)
                st.success("流程完成（示例）！輸出檔案已保存至 /tmp/demo.xlsx")

        with st.container(border=True):
            st.markdown("### 4) 客戶入口 / 自助查詢")
            st.write("對外提供查詢、試算、工單提交，並可串客服機器人")
            with st.expander("API/SSO/權限示意"):
                st.code(
                    """
                    # 假設以 JWT/SSO 保護端點
                    def verify_user(token: str) -> bool:
                        # decode + verify ...
                        return True
                    """,
                    language="python",
                )

elif page == "即時展示":
    st.subheader("互動式元件與狀態管理示範")

    with st.container(border=True):
        st.markdown("**篩選條件**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            rng = st.slider("日期範圍 (天)", 7, 120, 30)
        with c2:
            channel = st.multiselect("通路", ["官網", "門市", "經銷", "B2B"], default=["官網", "門市"]) 
        with c3:
            cate = st.selectbox("品類", ["全部", "A 系列", "B 系列", "C 系列"], index=0)
        with c4:
            show_margin = st.toggle("顯示毛利")

        df = load_demo_data(200)
        df = df.sort_values("日期").tail(rng)
        if channel: df = df[df["通路"].isin(channel)]
        if cate != "全部": df = df[df["品類"] == cate]

        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("**KPI 概覽**")
        c1, c2, c3 = st.columns(3)
        kpi_card("營收", f"{int(df['營收'].sum()):,}")
        if show_margin:
            kpi_card("毛利率", f"{df['毛利'].sum() / max(df['營收'].sum(),1):.1%}")
        kpi_card("平均單價", f"{int((df['營收'].sum()/max(df['數量'].sum(),1))):,}")

    with right:
        st.markdown("**下載/上傳**")
        st.download_button("下載目前篩選資料 (CSV)", df.to_csv(index=False).encode("utf-8-sig"), file_name="filtered.csv")
        st.file_uploader("上傳以覆蓋目前資料 (示例)", type=["csv", "xlsx"])

elif page == "ROI 試算":
    st.subheader("投資報酬率（ROI）與成本效益")
    st.write("以流程自動化/儀表板為例，估算時間與人力節省")

    with st.form("roi_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ppl = st.number_input("參與人數", 1, 200, 5)
            wage = st.number_input("平均時薪 (NT$)", 150, 3000, 350)
        with col2:
            minutes = st.number_input("每次作業耗時 (分鐘)", 1, 600, 60)
            times = st.number_input("每月作業頻率 (次)", 1, 200, 20)
        with col3:
            auto_rate = st.slider("自動化比例 %", 10, 100, 70)
            proj_cost = st.number_input("專案成本 (NT$)", 10000, 2000000, 300000)

        submit = st.form_submit_button("計算")

    if submit:
        monthly_hours = ppl * (minutes / 60) * times
        monthly_saved = monthly_hours * (auto_rate/100)
        monthly_value = monthly_saved * wage
        months_to_roi = proj_cost / max(monthly_value, 1)

        c1, c2, c3, c4 = st.columns(4)
        kpi_card("每月節省(小時)", f"{monthly_saved:.1f}h")
        kpi_card("每月效益(NT$)", f"{int(monthly_value):,}")
        kpi_card("回本期(月)", f"{months_to_roi:.1f}")
        kpi_card("年化效益(NT$)", f"{int(monthly_value*12):,}")

        with st.expander("計算公式與假設"):
            st.markdown("""
            - 月工時 = 參與人數 × 每次作業耗時(小時) × 每月頻率  
            - 節省工時 = 月工時 × 自動化比例  
            - 月效益 = 節省工時 × 平均時薪  
            - 回本期 = 專案成本 ÷ 月效益
            """)

elif page == "元件展覽":
    st.subheader("常用元件一次看")

    tab1, tab2, tab3, tab4 = st.tabs(["按鈕/選單", "表單與輸入", "表格/圖表", "狀態/提示"])
    with tab1:
        st.markdown("#### 按鈕與選單")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("主要動作", key="b1")
            st.link_button("外部連結", "https://streamlit.io")
        with c2:
            st.selectbox("單選下拉", ["A", "B", "C"])
            st.multiselect("多選", ["紅", "綠", "藍"], default=["紅"]) 
        with c3:
            st.slider("數值範圍", 0, 100, 40)
            st.toggle("開關")
    with tab2:
        st.markdown("#### 表單與輸入")
        with st.form("form_demo"):
            st.text_input("姓名")
            st.date_input("日期", value=date.today())
            st.text_area("備註")
            ok = st.form_submit_button("送出")
            if ok:
                st.success("已提交（示例）")
    with tab3:
        st.markdown("#### 表格與簡易圖表")
        df = load_demo_data(40)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.line_chart(df.groupby("日期")["營收"].sum())
    with tab4:
        st.markdown("#### 狀態與提示")
        with st.status("正在處理任務...", expanded=False) as status:
            time.sleep(.6)
            st.write("讀取資料…")
            time.sleep(.4)
            st.write("計算指標…")
            time.sleep(.4)
            status.update(label="完成！", state="complete")

elif page == "資料 App 範本":
    st.subheader("範本：從檔案到洞察")
    st.caption("這是一個可直接複製的資料應用骨架：上傳 → 清理 → 視覺化 → 匯出")

    step = st.segmented_control("流程", ["上傳", "清理", "視覺化", "匯出"], default="上傳")
    st.divider()

    if "_tpl_df" not in st.session_state:
        st.session_state["_tpl_df"] = None

    if step == "上傳":
        up = st.file_uploader("上傳 CSV/Excel", type=["csv", "xlsx"], key="tpl_up")
        if up:
            df = pd.read_excel(up) if up.name.endswith("xlsx") else pd.read_csv(up)
            st.session_state["_tpl_df"] = df
            st.success(f"讀入 {df.shape[0]} 列 × {df.shape[1]} 欄")
    elif step == "清理":
        df = st.session_state.get("_tpl_df")
        if df is None:
            st.info("請先於『上傳』步驟匯入資料。")
        else:
            st.markdown("**缺失值處理**")
            method = st.radio("策略", ["刪除含 NA 列", "以 0 填補"], horizontal=True)
            if st.button("套用"):
                if method == "刪除含 NA 列":
                    df = df.dropna()
                else:
                    df = df.fillna(0)
                st.session_state["_tpl_df"] = df
                st.success("完成清理！")
            st.dataframe(df.head(20), use_container_width=True)
    elif step == "視覺化":
        df = st.session_state.get("_tpl_df")
        if df is None:
            st.info("請先於『上傳』步驟匯入資料。")
        else:
            col = st.selectbox("選擇數值欄位繪圖", options=[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
            st.line_chart(df[col])
    else:  # 匯出
        df = st.session_state.get("_tpl_df")
        if df is None:
            st.info("請先於『上傳』步驟匯入資料。")
        else:
            st.download_button("下載清理後資料 (CSV)", df.to_csv(index=False).encode("utf-8-sig"), file_name="cleaned.csv")

elif page == "FAQ / 交付與維運":
    st.subheader("FAQ / 專案交付與維運")

    with st.expander("Q1. 如何部署？"):
        st.write("Docker/雲端（Streamlit Community Cloud、Cloud Run、EC2、Azure App Services）或內網伺服器皆可。")
    with st.expander("Q2. 權限與安全"):
        st.write("可串 SSO / JWT，網段白名單，API 金鑰保護，稽核日誌。")
    with st.expander("Q3. 與資料庫/Excel 串接？"):
        st.write("可連接 MySQL/Postgres/BigQuery；也可直接讀寫 Excel、CSV、Google Sheets。")
    with st.expander("Q4. LLM 與自動化"):
        st.write("可接 OpenAI/本地模型，建立問答、摘要、文件產製流程。")
    with st.expander("Q5. 交付內容"):
        st.write("原始碼、README、需求/測試文件、部署腳本、使用手冊與教育訓練。")

# 頁尾
st.markdown("<div class='footer'>© {} Streamlit 商業應用展示工具 · 以範例呈現企業導入可能性</div>".format(datetime.now().year), unsafe_allow_html=True)

