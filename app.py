import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import json

# -----------------------------
# Optional: Google Sheets (safe to run offline)
# -----------------------------
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except Exception:
    gspread = None
    Credentials = None
    GSPREAD_AVAILABLE = False

st.set_page_config(page_title="錐光金屬 - 報價系統 MVP", page_icon="🧮", layout="wide")
st.title("🧮 錐光金屬 - 報價系統 MVP")
st.caption("以 Streamlit 製作的最小可行原型：單件/批次估價、(可選) Google Sheets 參數同步、內部管理與 Excel 匯出。未連線時也能正常運作。")

# -----------------------------
# Sidebar: Global Params
# -----------------------------
st.sidebar.header("全域參數 (可依工廠實際調整)")
with st.sidebar:
    st.subheader("Google Sheets 連動（可選）")
    st.caption("上傳 Service Account JSON，並貼上 Google Sheet 連結。需將該 Sheet 分享給此 Service Account email。未設定時將使用內建參數。")

    gs_json_file = st.file_uploader("Service Account JSON", type=["json"], key="gsjson")
    gs_url = st.text_input("Google Sheet 連結 (含 /edit)", value="", key="gs_url")

    use_gs = False
    gs_book = None

    if GSPREAD_AVAILABLE and gs_json_file and gs_url:
        try:
            creds_info = json.load(gs_json_file)
            creds = Credentials.from_service_account_info(
                creds_info,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.readonly",
                ],
            )
            gs_client = gspread.authorize(creds)
            gs_book = gs_client.open_by_url(gs_url)
            use_gs = True
            st.success("已連線 Google Sheets！")
        except Exception as e:
            use_gs = False
            gs_book = None
            st.warning(f"Google Sheets 連線失敗，將改用本機參數：{e}")
    elif not GSPREAD_AVAILABLE:
        st.info("偵測不到 gspread / google-auth 套件，將以離線模式運行。")

    # 供 key 後綴使用，確保不重複
    ctx = "gs" if use_gs else "offline"

    st.subheader("材料與密度/單價")
    default_materials = {
        "SPCC 冷軋鋼": {"density": 7.85, "price_per_kg": 35},
        "SS304 不鏽鋼": {"density": 8.0, "price_per_kg": 90},
        "AL5052 鋁合金": {"density": 2.7, "price_per_kg": 75},
    }

    # Materials
    if use_gs:
        try:
            ws_m = gs_book.worksheet("Materials")
            rows = ws_m.get_all_records()
            from collections import OrderedDict
            mat = OrderedDict()
            for r in rows:
                name = str(r.get("material") or "").strip()
                if not name:
                    continue
                dens = float(r.get("density") or 0)
                price = float(r.get("price_per_kg") or 0)
                mat[name] = {"density": dens, "price_per_kg": price}
        except Exception as e:
            st.warning(f"讀取 Materials 失敗，改用預設：{e}")
            mat = default_materials.copy()
    else:
        mat = default_materials.copy()

    # 可在 UI 臨時覆寫材料參數（每個材料有獨立 key）
    for i, m in enumerate(list(mat.keys())):
        with st.expander(f"{m}", expanded=False):
            mat[m]["density"] = st.number_input(
                f"{m} 密度 (g/cm³)", value=float(mat[m]["density"]), step=0.01, key=f"dens_{i}")
            mat[m]["price_per_kg"] = st.number_input(
                f"{m} 材料單價 (NT$/kg)", value=float(mat[m]["price_per_kg"]), step=1.0, key=f"price_{i}")

    # Rates
    st.subheader("製程費率")
    if use_gs:
        try:
            ws_r = gs_book.worksheet("Rates")
            r = {k: v for k, v in ws_r.get_all_records(head=1)[0].items()}
            laser_rate = st.number_input("雷射/等離子切割單價 (NT$/m)", value=float(r.get("laser_per_m", 25.0)), step=1.0, key=f"laser_rate_{ctx}")
            bend_rate = st.number_input("折彎單價 (NT$/道)", value=float(r.get("bend_per_pass", 12.0)), step=1.0, key=f"bend_rate_{ctx}")
            weld_rate = st.number_input("焊接單價 (NT$/m)", value=float(r.get("weld_per_m", 120.0)), step=1.0, key=f"weld_rate_{ctx}")
            tap_rate = st.number_input("攻牙單價 (NT$/孔)", value=float(r.get("tap_per_hole", 3.0)), step=0.5, key=f"tap_rate_{ctx}")
            punch_rate = st.number_input("沖壓單價 (NT$/孔/次)", value=float(r.get("punch_per_hit", 1.5)), step=0.5, key=f"punch_rate_{ctx}")
            paint_rate = st.number_input("表面處理/噴塗 (NT$/m²)", value=float(r.get("paint_per_m2", 80.0)), step=1.0, key=f"paint_rate_{ctx}")
        except Exception as e:
            st.warning(f"讀取 Rates 失敗，改用預設：{e}")
            laser_rate = st.number_input("雷射/等離子切割單價 (NT$/m)", value=25.0, step=1.0, key=f"laser_rate_{ctx}")
            bend_rate = st.number_input("折彎單價 (NT$/道)", value=12.0, step=1.0, key=f"bend_rate_{ctx}")
            weld_rate = st.number_input("焊接單價 (NT$/m)", value=120.0, step=1.0, key=f"weld_rate_{ctx}")
            tap_rate = st.number_input("攻牙單價 (NT$/孔)", value=3.0, step=0.5, key=f"tap_rate_{ctx}")
            punch_rate = st.number_input("沖壓單價 (NT$/孔/次)", value=1.5, step=0.5, key=f"punch_rate_{ctx}")
            paint_rate = st.number_input("表面處理/噴塗 (NT$/m²)", value=80.0, step=1.0, key=f"paint_rate_{ctx}")
    else:
        laser_rate = st.number_input("雷射/等離子切割單價 (NT$/m)", value=25.0, step=1.0, key=f"laser_rate_{ctx}")
        bend_rate = st.number_input("折彎單價 (NT$/道)", value=12.0, step=1.0, key=f"bend_rate_{ctx}")
        weld_rate = st.number_input("焊接單價 (NT$/m)", value=120.0, step=1.0, key=f"weld_rate_{ctx}")
        tap_rate = st.number_input("攻牙單價 (NT$/孔)", value=3.0, step=0.5, key=f"tap_rate_{ctx}")
        punch_rate = st.number_input("沖壓單價 (NT$/孔/次)", value=1.5, step=0.5, key=f"punch_rate_{ctx}")
        paint_rate = st.number_input("表面處理/噴塗 (NT$/m²)", value=80.0, step=1.0, key=f"paint_rate_{ctx}")

    # Settings
    st.subheader("費率與係數")
    if use_gs:
        try:
            ws_s = gs_book.worksheet("Settings")
            s = {k: v for k, v in ws_s.get_all_records(head=1)[0].items()}
            scrap_rate = st.number_input("材料損耗率", value=float(s.get("scrap_rate", 0.05)), step=0.01, min_value=0.0, key=f"scrap_rate_{ctx}")
            overhead_rate = st.number_input("製造間接費率 (作用於製程費)", value=float(s.get("overhead_rate", 0.15)), step=0.01, min_value=0.0, key=f"overhead_rate_{ctx}")
            setup_cost = st.number_input("每筆訂單固定開機/換線費 (NT$)", value=float(s.get("setup_cost", 150.0)), step=10.0, min_value=0.0, key=f"setup_cost_{ctx}")
            profit_margin = st.number_input("利潤率 (作用於總成本)", value=float(s.get("profit_margin", 0.12)), step=0.01, min_value=0.0, key=f"profit_margin_{ctx}")
        except Exception as e:
            st.warning(f"讀取 Settings 失敗，改用預設：{e}")
            scrap_rate = st.number_input("材料損耗率", value=0.05, step=0.01, min_value=0.0, key=f"scrap_rate_{ctx}")
            overhead_rate = st.number_input("製造間接費率 (作用於製程費)", value=0.15, step=0.01, min_value=0.0, key=f"overhead_rate_{ctx}")
            setup_cost = st.number_input("每筆訂單固定開機/換線費 (NT$)", value=150.0, step=10.0, min_value=0.0, key=f"setup_cost_{ctx}")
            profit_margin = st.number_input("利潤率 (作用於總成本)", value=0.12, step=0.01, min_value=0.0, key=f"profit_margin_{ctx}")
    else:
        scrap_rate = st.number_input("材料損耗率", value=0.05, step=0.01, min_value=0.0, key=f"scrap_rate_{ctx}")
        overhead_rate = st.number_input("製造間接費率 (作用於製程費)", value=0.15, step=0.01, min_value=0.0, key=f"overhead_rate_{ctx}")
        setup_cost = st.number_input("每筆訂單固定開機/換線費 (NT$)", value=150.0, step=10.0, min_value=0.0, key=f"setup_cost_{ctx}")
        profit_margin = st.number_input("利潤率 (作用於總成本)", value=0.12, step=0.01, min_value=0.0, key=f"profit_margin_{ctx}")

# -----------------------------
# Helper: 核心計算
# -----------------------------

def compute_quote_row(row, mat_dict):
    # 期望欄位：length_mm, width_mm, thickness_mm, perimeter_m, bends, weld_len_m,
    #           tap_qty, punch_qty, surface_area_m2, qty, material
    mat_props = mat_dict.get(row.get('material'), {"density": 7.85, "price_per_kg": 35})

    area_m2 = (row.get('length_mm', 0) / 1000) * (row.get('width_mm', 0) / 1000)
    thickness_m = row.get('thickness_mm', 0) / 1000
    volume_m3 = area_m2 * thickness_m
    density_kg_m3 = mat_props['density'] * 1000  # g/cm3 -> kg/m3
    weight_kg = volume_m3 * density_kg_m3

    material_cost = weight_kg * mat_props['price_per_kg'] * (1 + scrap_rate)
    cutting_cost = row.get('perimeter_m', 0) * laser_rate
    bending_cost = row.get('bends', 0) * bend_rate
    welding_cost = row.get('weld_len_m', 0) * weld_rate
    tap_cost = row.get('tap_qty', 0) * tap_rate
    punch_cost = row.get('punch_qty', 0) * punch_rate
    surface_cost = row.get('surface_area_m2', area_m2) * paint_rate

    process_cost = cutting_cost + bending_cost + welding_cost + tap_cost + punch_cost + surface_cost
    overhead_cost = process_cost * overhead_rate

    unit_cost_before_margin = material_cost + process_cost + overhead_cost
    unit_price = np.ceil(unit_cost_before_margin * (1 + profit_margin))  # 無條件進位

    qty = max(int(row.get('qty', 1)), 1)
    total_price = unit_price * qty

    return {
        'material_cost': material_cost,
        'cutting_cost': cutting_cost,
        'bending_cost': bending_cost,
        'welding_cost': welding_cost,
        'tap_cost': tap_cost,
        'punch_cost': punch_cost,
        'surface_cost': surface_cost,
        'overhead_cost': overhead_cost,
        'unit_cost_before_margin': unit_cost_before_margin,
        'unit_price': unit_price,
        'qty': qty,
        'total_price': total_price,
        'area_m2': area_m2,
        'weight_kg': weight_kg,
    }

# -----------------------------
# 單件報價
# -----------------------------
st.header("單件報價")
col1, col2, col3, col4 = st.columns(4)
with col1:
    material = st.selectbox("材料", list(mat.keys()), index=0, key="material_sel")
    length_mm = st.number_input("展開長 (mm)", value=200.0, step=1.0, key="length_mm")
    width_mm = st.number_input("展開寬 (mm)", value=150.0, step=1.0, key="width_mm")
    thickness_mm = st.number_input("厚度 (mm)", value=2.0, step=0.1, key="thickness_mm")
with col2:
    perimeter_m = st.number_input("切割周長 (m)", value=1.2, step=0.1, key="perimeter_m")
    bends = st.number_input("折彎道數 (道)", value=4, step=1, key="bends")
    weld_len_m = st.number_input("焊接長度 (m)", value=0.3, step=0.1, key="weld_len_m")
with col3:
    tap_qty = st.number_input("攻牙孔數 (孔)", value=0, step=1, key="tap_qty")
    punch_qty = st.number_input("沖壓次數/孔數", value=0, step=1, key="punch_qty")
    surface_area_m2 = st.number_input("表面處理面積 (m²)", value=0.1, step=0.01, key="surface_area_m2")
with col4:
    qty = st.number_input("數量 (pcs)", value=10, step=1, min_value=1, key="qty")
    part_no = st.text_input("料號/品名", value="Bracket-001", key="part_no")
    customer = st.text_input("客戶名稱", value="Demo 客戶", key="customer")

single_row = {
    'material': material,
    'length_mm': length_mm,
    'width_mm': width_mm,
    'thickness_mm': thickness_mm,
    'perimeter_m': perimeter_m,
    'bends': bends,
    'weld_len_m': weld_len_m,
    'tap_qty': tap_qty,
    'punch_qty': punch_qty,
    'surface_area_m2': surface_area_m2,
    'qty': qty
}

single_breakdown = compute_quote_row(single_row, mat)

# 可選：寫回 Google Sheets 的 Quotes 表
if use_gs and st.button("寫入此單到 Google Sheets/Quotes", key="write_quote"):
    try:
        try:
            ws_q = gs_book.worksheet("Quotes")
        except Exception:
            ws_q = gs_book.add_worksheet(title="Quotes", rows=2000, cols=30)
            ws_q.append_row(["timestamp","customer","part_no","material","length_mm","width_mm","thickness_mm","perimeter_m","bends","weld_len_m","tap_qty","punch_qty","surface_area_m2","qty","unit_price","total_price"])        
        ws_q.append_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            customer, part_no, material,
            length_mm, width_mm, thickness_mm,
            perimeter_m, bends, weld_len_m, tap_qty, punch_qty, surface_area_m2,
            qty, int(single_breakdown['unit_price']), int(single_breakdown['total_price'])
        ])
        st.success("已寫入 Quotes 工作表！")
    except Exception as e:
        st.error(f"寫入失敗：{e}")

st.subheader("單件成本拆解")
colA, colB = st.columns([2, 1])
with colA:
    bd_df = pd.DataFrame([
        {"項目": "材料", "金額": single_breakdown['material_cost']},
        {"項目": "切割", "金額": single_breakdown['cutting_cost']},
        {"項目": "折彎", "金額": single_breakdown['bending_cost']},
        {"項目": "焊接", "金額": single_breakdown['welding_cost']},
        {"項目": "攻牙", "金額": single_breakdown['tap_cost']},
        {"項目": "沖壓", "金額": single_breakdown['punch_cost']},
        {"項目": "表面處理", "金額": single_breakdown['surface_cost']},
        {"項目": "間接費", "金額": single_breakdown['overhead_cost']},
    ])
    st.dataframe(bd_df.style.format({"金額": "{:.0f}"}), use_container_width=True)
with colB:
    st.metric("單價 (含利潤)", f"NT$ {int(single_breakdown['unit_price'])}")
    st.metric("數量", f"{single_breakdown['qty']} 件")
    st.metric("總價", f"NT$ {int(single_breakdown['total_price'])}")

# -----------------------------
# 批次報價 (CSV)
# -----------------------------
st.header("批次報價 (CSV)")
st.caption("欄位: part_no, material, length_mm, width_mm, thickness_mm, perimeter_m, bends, weld_len_m, tap_qty, punch_qty, surface_area_m2, qty")
file = st.file_uploader("上傳 CSV", type=["csv"], key="csv_upload")

if file is not None:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        st.error(f"讀取 CSV 失敗：{e}")
        df = None

    if df is not None:
        required = ["part_no","material","length_mm","width_mm","thickness_mm","perimeter_m","bends","weld_len_m","tap_qty","punch_qty","surface_area_m2","qty"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"缺少欄位: {missing}")
        else:
            results = []
            for _, r in df.iterrows():
                bd = compute_quote_row(r, mat)
                results.append({**{k: r.get(k, None) for k in required}, **bd})
            out_df = pd.DataFrame(results)
            out_df["unit_price"] = out_df["unit_price"].astype(int)
            out_df["total_price"] = out_df["total_price"].astype(int)
            st.success("計算完成！")
            st.dataframe(out_df, use_container_width=True)

            # 產生 Excel 供下載
            with BytesIO() as buffer:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    meta = pd.DataFrame({
                        '欄位': ['客戶','建立時間','開機費','利潤率','損耗率','間接費率'],
                        '值': [customer, datetime.now().strftime('%Y-%m-%d %H:%M'), setup_cost, profit_margin, scrap_rate, overhead_rate]
                    })
                    meta.to_excel(writer, sheet_name='Quote_Meta', index=False)
                    out_df.to_excel(writer, sheet_name='Quote_Items', index=False)
                dl = buffer.getvalue()
            st.download_button("下載 Excel 報價檔", data=dl,
                               file_name=f"quote_{customer}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="dl_excel")

# -----------------------------
# 對內：參數管理（寫回 Google Sheets）
# -----------------------------
if use_gs and GSPREAD_AVAILABLE and gs_book is not None:
    st.header("內部管理（對內）")
    st.caption("直接在這裡維護 Google Sheets：Materials / Rates / Settings。省去打開複雜表單的麻煩。")

    tab_m, tab_r, tab_s = st.tabs(["Materials", "Rates", "Settings"])

    with tab_m:
        try:
            ws_m = gs_book.worksheet("Materials")
            m_rows = ws_m.get_all_records()
            m_df = pd.DataFrame(m_rows or [{"material":"SPCC 冷軋鋼","density":7.85,"price_per_kg":35}])
            st.write("編輯材料清單（material, density, price_per_kg）：")
            m_edit = st.data_editor(m_df, num_rows="dynamic", use_container_width=True, key="m_editor")
            if st.button("儲存 Materials", key="save_mat"):
                ws_m.clear()
                ws_m.update([m_edit.columns.tolist()] + m_edit.fillna("").values.tolist())
                st.success("Materials 已更新！")
        except Exception as e:
            st.warning(f"Materials 無法讀寫：{e}")

    with tab_r:
        try:
            try:
                ws_r = gs_book.worksheet("Rates")
            except Exception:
                ws_r = gs_book.add_worksheet(title="Rates", rows=50, cols=10)
                ws_r.update([["laser_per_m","bend_per_pass","weld_per_m","tap_per_hole","punch_per_hit","paint_per_m2"],[25,12,120,3,1.5,80]])
            r_row = ws_r.get_all_records(head=1)
            r_df = pd.DataFrame(r_row or [{"laser_per_m":25,"bend_per_pass":12,"weld_per_m":120,"tap_per_hole":3,"punch_per_hit":1.5,"paint_per_m2":80}])
            r_edit = st.data_editor(r_df, use_container_width=True, key="r_editor")
            if st.button("儲存 Rates", key="save_rates"):
                ws_r.clear()
                ws_r.update([r_edit.columns.tolist()] + r_edit.fillna("").values.tolist())
                st.success("Rates 已更新！")
        except Exception as e:
            st.warning(f"Rates 無法讀寫：{e}")

    with tab_s:
        try:
            try:
                ws_s = gs_book.worksheet("Settings")
            except Exception:
                ws_s = gs_book.add_worksheet(title="Settings", rows=50, cols=10)
                ws_s.update([["scrap_rate","overhead_rate","setup_cost","profit_margin"],[0.05,0.15,150,0.12]])
            s_row = ws_s.get_all_records(head=1)
            s_df = pd.DataFrame(s_row or [{"scrap_rate":0.05,"overhead_rate":0.15,"setup_cost":150,"profit_margin":0.12}])
            s_edit = st.data_editor(s_df, use_container_width=True, key="s_editor")
            if st.button("儲存 Settings", key="save_settings"):
                ws_s.clear()
                ws_s.update([s_edit.columns.tolist()] + s_edit.fillna("").values.tolist())
                st.success("Settings 已更新！")
        except Exception as e:
            st.warning(f"Settings 無法讀寫：{e}")
else:
    st.info("若要啟用『內部管理』與 Sheets 回寫，請先在側邊欄連線 Google Sheets（離線模式下亦可完整估價與匯出）。")

# -----------------------------
# Footer / Notes
# -----------------------------
st.info("本原型為示意，實際係數/費率請依工廠實際成本、工時與良率調整。可擴充：PDF 報價單、階梯價、最低毛利警示、角色權限、簽核、歷史版本控管、DXF/DWG 解析、ERP/MES 串接等。")
