import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# --- 基本設定 ---
st.set_page_config(page_title="Fancy Active 後台系統", page_icon="🧘", layout="wide")

# 品牌配色
BG_GRADIENT = "linear-gradient(135deg, #f3efe6, #e8e3d4)"
TEXT_COLOR = "#3d4732"      # 深橄欖綠
ACCENT_COLOR = "#7a846b"    # 柔和橄欖綠
CARD_BG = "rgba(255,255,255,0.85)"  # 半透明白色卡片

# --- 自訂 CSS ---
st.markdown(f"""
    <style>
        body {{
            background: {BG_GRADIENT};
            font-family: 'sans-serif';
        }}
        .nav-link {{
            font-weight: bold !important;
        }}
        .stButton button {{
            background-color: {ACCENT_COLOR};
            color: white;
            border-radius: 8px;
            padding: 0.3em 0.8em;
            font-weight: bold;
        }}
    </style>
""", unsafe_allow_html=True)

# --- 載入假數據 ---
df = pd.read_csv("yoga_sales_data.csv", parse_dates=["日期"])

# --- 側邊欄 ---
with st.sidebar:
    st.markdown("## 📂 Fancy Active")
    menu = option_menu(
        menu_title=None,
        options=[
            "🏠 首頁",
            "📊 銷售概覽",
            "📦 訂單管理",
            "🛍 產品管理",
            "📸 模特兒拍攝",
            "💡 促銷建議",
            "📤 匯出報表"
        ],
        icons=[
            "house-fill",
            "bar-chart-fill",
            "box-seam",
            "cart-fill",
            "camera-fill",
            "lightbulb-fill",
            "cloud-download-fill"
        ],
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#f7f7f4"},
            "icon": {"color": TEXT_COLOR, "font-size": "20px"},
            "nav-link": {
                "color": TEXT_COLOR,
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e0ded5",
            },
            "nav-link-selected": {
                "background-color": ACCENT_COLOR,
                "color": "white",
            },
        }
    )

# 🏠 首頁
if menu == "🏠 首頁":
    st.markdown("""
        <style>
            .main {
                background: linear-gradient(135deg, #f3efe6, #e8e3d4);
            }
            .banner {
                background-color: #7a846b;
                padding: 50px 20px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 30px;
            }
            .banner h1 {
                color: white;
                font-size: 40px;
                margin: 0;
            }
            .banner h3 {
                color: white;
                font-weight: normal;
                margin-top: 10px;
                font-size: 22px;
            }
            .card-home {
                background-color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                text-align: center;
            }
            .card-home p {
                margin: 0;
                color: #7a846b;
            }
            .big-number-home {
                font-size: 28px;
                font-weight: bold;
                margin-top: 5px;
                color: #3d4732;
            }
        </style>
    """, unsafe_allow_html=True)

    # Banner
    st.markdown("""
        <div class="banner">
            <h1>Fancy Active 後台系統</h1>
            <h3>對肌膚溫柔，對內心堅定</h3>
        </div>
    """, unsafe_allow_html=True)

    # 浮動卡片
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="card-home"><p>本月銷售額</p><div class="big-number-home">{df["銷售額"].sum():,} 元</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card-home"><p>熱銷商品</p><div class="big-number-home">{df["熱賣商品"].mode()[0]}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card-home"><p>庫存警示數量</p><div class="big-number-home">{(df["庫存"] < 10).sum()}</div></div>', unsafe_allow_html=True)


elif menu == "📊 銷售概覽":
    st.header("📊 銷售數據概覽")
    st.line_chart(df.set_index("日期")["銷售額"])
    st.subheader("🔥 熱銷商品排行榜")
    st.bar_chart(df["熱賣商品"].value_counts())

elif menu == "📦 訂單管理":
    st.header("📦 訂單管理")

    orders = pd.DataFrame({
        "訂單編號": ["A001", "A002", "A003", "A004"],
        "客戶": ["王小姐", "李先生", "張小姐", "陳先生"],
        "商品": ["高腰瑜珈褲A", "運動內衣C", "喇叭瑜珈褲D", "運動外套E"],
        "數量": [2, 1, 3, 1],
        "狀態": ["已出貨", "處理中", "已完成", "處理中"]
    })

    # 篩選器
    status_filter = st.selectbox(
        "選擇訂單狀態",
        options=["全部", "處理中", "已出貨", "已完成"],
        index=0
    )

    # 根據篩選條件過濾
    if status_filter != "全部":
        orders = orders[orders["狀態"] == status_filter]

    st.table(orders)

elif menu == "🛍 產品管理":
    st.header("🛍 商品上傳與 AI 文案生成")
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_img = st.file_uploader("上傳商品圖片", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            st.image(uploaded_img, caption="商品圖片預覽", use_column_width=True)
    with col2:
        product_name = st.text_input("商品名稱")
        product_features = st.text_area("商品特色（用逗號分隔）", "高腰設計, 彈性布料, 透氣無痕")
        if st.button("生成 Fancy Active 風格文案"):
            if product_name:
                features_list = [f.strip() for f in product_features.split(",")]
                description = f"{product_name} — 以對肌膚溫柔、對內心堅定的理念設計，採用{features_list[1]}，在運動與日常中提供{features_list[0]}的同時，保持{features_list[2]}，讓你自由自在地展現自我。"
                st.markdown(f'<div class="card"><p>{description}</p></div>', unsafe_allow_html=True)
            else:
                st.warning("請先輸入商品名稱")

elif menu == "📸 模特兒拍攝":
    st.subheader("📸 模特兒拍攝管理")
    sub_choice = option_menu(
        None,
        ["📅 拍攝計畫表", "👤 模特兒名單", "🖼 圖片庫"],
        icons=["calendar-event", "person-badge", "image-fill"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )
    if sub_choice == "📅 拍攝計畫表":
        st.table(pd.DataFrame({
            "拍攝日": ["2025-08-20", "2025-09-05"],
            "模特兒": ["Anna", "Lisa"],
            "產品": ["高腰瑜珈褲A", "運動內衣C"],
            "場地": ["台北攝影棚", "淡水海邊"],
            "報價": ["$5,000", "$7,200"]
        }))
    elif sub_choice == "👤 模特兒名單":
        st.table(pd.DataFrame({
            "姓名": ["Anna", "Lisa", "Mia"],
            "身高(cm)": [170, 165, 172],
            "風格": ["運動健康", "甜美活潑", "成熟幹練"],
            "合作產品": ["高腰瑜珈褲A", "運動內衣C", "喇叭瑜珈褲D"]
        }))
    elif sub_choice == "🖼 圖片庫":
        img_cols = st.columns(3)
        for i in range(6):
            img_cols[i % 3].image("https://via.placeholder.com/300x200.png?text=Photo+Sample", use_column_width=True)

elif menu == "💡 促銷建議":
    st.header("💡 AI 促銷建議（假資料示範）")
    suggestions = [
        "🎁 高腰瑜珈褲A + 運動內衣C 組合優惠",
        "🏷 附口袋瑜珈褲F 夏季限定 85 折",
        "🎀 購買滿 2000 元送瑜珈毛巾"
    ]
    for s in suggestions:
        st.markdown(f'''
            <div style="
                background-color: {ACCENT_COLOR};
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                margin: 10px 0;
                color: white;
                font-size: 18px;
            ">{s}</div>
        ''', unsafe_allow_html=True)

elif menu == "📤 匯出報表":
    st.header("📤 匯出銷售報表")
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("下載 CSV", csv, "fancy_active_sales.csv", "text/csv")
