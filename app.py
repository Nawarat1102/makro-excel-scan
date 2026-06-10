import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
st.title("🛒 ระบบรวมไฟล์ใบสั่งสินค้า Makro")

# 1. อัปโหลด Master (Sheet1) และไฟล์สรุปยอด (Sheet2)
col1, col2 = st.columns(2)
with col1:
    file_master = st.file_uploader("อัปโหลดไฟล์ Master (Sheet1)", type=["csv", "xlsx"])
with col2:
    file_summary = st.file_uploader("อัปโหลดไฟล์สรุปยอด (Sheet2)", type=["csv", "xlsx"])

if file_master and file_summary:
    # อ่านไฟล์ตามประเภท
    df1 = pd.read_excel(file_master) if file_master.name.endswith('.xlsx') else pd.read_csv(file_master)
    df2 = pd.read_excel(file_summary) if file_summary.name.endswith('.xlsx') else pd.read_csv(file_summary)
    
    # ดึงข้อมูลจาก Sheet2 โดยสมมติว่าคอลัมน์แรกคือ "ลำดับที่" และคอลัมน์ที่ 3 คือ "จำนวน"
    # คุณอาจต้องปรับเลข index ถ้าไฟล์ของคุณเปลี่ยนคอลัมน์
    qty_map = dict(zip(df2.iloc[:, 0].astype(str), df2.iloc[:, 2]))
    
    # อัปเดตข้อมูลลง Sheet1
    df1['จำนวนที่สั่งซื้อ'] = df1.iloc[:, 0].astype(str).map(qty_map)
    
    # แสดงผล
    st.subheader("ตารางรายการที่รวมแล้ว:")
    st.dataframe(df1, use_container_width=True)
    
    # ปุ่มดาวน์โหลด
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 ดาวน์โหลดไฟล์ Excel ผลลัพธ์",
        data=buffer.getvalue(),
        file_name="Final_Order.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
