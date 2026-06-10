import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

# 1. ตั้งค่าฐานข้อมูล Master (ดึงจาก n1.xlsx)
FILE_MASTER = 'n1.xlsx'

st.set_page_config(layout="wide")
st.title("🛒 ระบบอัปเดตข้อมูลใบสั่งสินค้า (Makro)")

# โหลดข้อมูล (ใช้แคชเพื่อความเร็ว)
@st.cache_data
def load_db():
    return pd.read_excel(FILE_MASTER, sheet_name='Sheet1')

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# 2. เมนูทางซ้าย (ปุ่มรีเซ็ต)
if st.sidebar.button("🔄 รีเซ็ตฐานข้อมูลเป็น 0"):
    st.session_state.db['จำนวนที่สั่งซื้อ'] = 0
    st.sidebar.success("รีเซ็ตสำเร็จ!")

# 3. ส่วนอ่านภาพ
uploaded_img = st.file_uploader("📸 อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png", "jpeg"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # ดึงค่าจากภาพมาอัปเดต
    # โค้ดอ่านบรรทัดที่ 1..26 จากภาพ แล้วหาตัวเลขจำนวนที่อยู่ข้างๆ
    for i, (bbox, text, prob) in enumerate(results):
        if text.isdigit() and int(text) <= 26: # ถ้าเจอเลขลำดับที่ 1-26
            seq = int(text)
            try:
                # ลองอ่านค่าตัวเลขที่คาดว่าเป็นจำนวนที่อยู่ถัดไปในภาพ
                qty = results[i+1][1]
                if qty.isdigit():
                    # อัปเดตข้อมูลในฐานข้อมูล (บวกเพิ่ม)
                    mask = st.session_state.db['ลำดับที่'] == seq
                    current_val = st.session_state.db.loc[mask, 'จำนวนที่สั่งซื้อ'].fillna(0).values[0]
                    st.session_state.db.loc[mask, 'จำนวนที่สั่งซื้อ'] = current_val + int(qty)
            except:
                pass
    st.success("✅ อ่านข้อมูลจากภาพและอัปเดตฐานข้อมูลสำเร็จ!")

# 4. แสดงผลตารางปัจจุบัน
st.dataframe(st.session_state.db, use_container_width=True)

# 5. ปุ่มดาวน์โหลด
buffer = io.BytesIO()
st.session_state.db.to_excel(buffer, index=False)
st.download_button("📥 ดาวน์โหลดฐานข้อมูลล่าสุด", buffer.getvalue(), "Updated_n1.xlsx")
