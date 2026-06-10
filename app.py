import streamlit as st
import pandas as pd
import pdfplumber
import io

st.set_page_config(layout="wide")
st.title("🛒 Makro Excel Generator (PDF Master Mode)")

uploaded_file = st.file_uploader("อัปโหลดไฟล์ใบสั่งสินค้า (PDF)", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        # ดึงข้อความจากหน้าแรก
        page = pdf.pages[0]
        table = page.extract_table()
        
        if table:
            # สร้างตารางจากข้อมูลใน PDF
            df = pd.DataFrame(table[1:], columns=table[0])
            st.success("✨ ดึงข้อมูลจาก PDF สำเร็จ!")
            st.dataframe(df, use_container_width=True)
            
            # ปุ่มดาวน์โหลด Excel
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False)
            towrite.seek(0)
            st.download_button("📥 ดาวน์โหลดไฟล์ Excel", towrite, "Makro_Order.xlsx")
        else:
            st.warning("ไม่พบตารางใน PDF นี้")
