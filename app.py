import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📄 ระบบใบสั่งผลิตสินค้า")

# ส่วนอัปโหลดไฟล์
uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel เพื่อแสดงตาราง", type=["xlsx", "csv"])

if uploaded_file:
    # อ่านไฟล์
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # 1. แสดงผลแบบตารางที่ดูสะอาดตา (เหมือนตารางในบิล)
    st.subheader("ตารางรายการสินค้า")
    
    # ใช้ st.dataframe พร้อมไฮไลท์แถว
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ลำดับที่": st.column_config.NumberColumn("ลำดับที่", width="small"),
            "รายการสินค้า": st.column_config.TextColumn("รายการสินค้า", width="large"),
            "จำนวนที่สั่งซื้อ": st.column_config.NumberColumn("จำนวนที่สั่งซื้อ", format="%d"),
        }
    )

    # 2. ส่วนของปุ่มดาวน์โหลด
    st.download_button(
        label="📥 ดาวน์โหลดไฟล์ตารางนี้",
        data=uploaded_file.getvalue(),
        file_name="Order_List_Output.xlsx"
    )
    st.markdown("""
    <style>
    thead tr th { background-color: #f0f2f6; border: 1px solid #ddd; }
    tbody tr td { border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)
