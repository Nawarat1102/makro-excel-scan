import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

# โหลดฐานข้อมูลหลัก
DB_FILE = 'n1.xlsx'

st.title("🛒 ระบบอัปเดตฐานข้อมูลด้วยรูปใบสั่งสินค้า")

# 1. ส่วนรีเซ็ตฐานข้อมูล
if st.sidebar.button("🔄 รีเซ็ตฐานข้อมูลเป็น 0"):
    df = pd.read_excel(DB_FILE, sheet_name='Sheet1')
    df['จำนวนที่สั่งซื้อ'] = 0
    df.to_excel(DB_FILE, sheet_name='Sheet1', index=False)
    st.sidebar.success("ฐานข้อมูลถูกรีเซ็ตแล้ว!")

# 2. ส่วนอัปโหลดรูปภาพ
uploaded_img = st.file_uploader("ถ่ายรูปหรืออัปโหลดใบสั่งสินค้าที่นี่", type=["jpg", "png", "jpeg"])

if uploaded_img:
    with st.spinner("กำลังอ่านข้อมูลจากรูปภาพ..."):
        # อ่านรูปและทำ OCR
        img = np.array(Image.open(uploaded_img))
        reader = easyocr.Reader(['th', 'en'])
        results = reader.readtext(img)
        
        # ดึงเลขจากรูป (สมมติ OCR อ่านได้เป็นคู่ของ ลำดับที่:จำนวน)
        # ตรงนี้คือจุดที่ระบบจะ "เข้าใจ" ข้อมูลจากรูปคุณ
        scanned_data = {}
        for i, (bbox, text, prob) in enumerate(results):
            if text.isdigit(): # ถ้าเจอตัวเลข
                val = int(text)
                # Logic: ถ้าเป็นเลขลำดับที่ (1-26) ให้มองหาเลขจำนวนในตำแหน่งถัดไป
                if 1 <= val <= 26:
                    try:
                        qty_text = results[i+1][1]
                        if qty_text.isdigit():
                            scanned_data[val] = int(qty_text)
                    except: pass

        # 3. อัปเดตข้อมูลลงฐานข้อมูล
        df = pd.read_excel(DB_FILE, sheet_name='Sheet1')
        for seq, qty in scanned_data.items():
            mask = df['ลำดับที่'] == seq
            current_val = df.loc[mask, 'จำนวนที่สั่งซื้อ'].fillna(0)
            df.loc[mask, 'จำนวนที่สั่งซื้อ'] = current_val + qty
        
        # บันทึกทับไฟล์เดิม
        df.to_excel(DB_FILE, sheet_name='Sheet1', index=False)
        st.success("✅ อัปเดตยอดเพิ่มในฐานข้อมูลเรียบร้อย!")
        st.dataframe(df)

        # 4. ดาวน์โหลด
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 ดาวน์โหลดไฟล์อัปเดต", buffer.getvalue(), "Database_Updated.xlsx")
