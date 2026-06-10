import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import openpyxl

st.title("🛒 ระบบอัปเดตข้อมูล Makro")

FILE_PATH = 'n1.xlsx'

# 1. โหลดข้อมูลแบบเจาะจงบรรทัด
@st.cache_data
def load_data():
    # Sheet1 เริ่มข้อมูลที่บรรทัด 7 (skiprows=6)
    df1 = pd.read_excel(FILE_PATH, sheet_name='Sheet1', skiprows=6)
    # Sheet2 เริ่มข้อมูลที่บรรทัด 5 (skiprows=4)
    df2 = pd.read_excel(FILE_PATH, sheet_name='Sheet2', skiprows=4)
    return df1, df2

try:
    df_s1, df_s2 = load_data()
except Exception as e:
    st.error(f"โหลดไฟล์ไม่ได้: {e}")
    st.stop()

# 2. อ่านรูปภาพ
uploaded_img = st.file_uploader("📸 อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png", "jpeg"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # ดึงค่ามาอัปเดต
    found = False
    for i, (bbox, text, prob) in enumerate(results):
        if text.isdigit() and int(text) <= 50:
            seq = int(text)
            try:
                # ลองอ่านตัวเลขถัดไป
                qty = results[i+1][1]
                if qty.isdigit():
                    val = int(qty)
                    # อัปเดตทั้ง 2 ชีต
                    df_s1.loc[df_s1['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = val
                    df_s2.loc[df_s2['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = val
                    found = True
            except: pass
    
    if found:
        # 3. บันทึกทับไฟล์เดิม
        with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
            df_s1.to_excel(writer, sheet_name='Sheet1', index=False)
            df_s2.to_excel(writer, sheet_name='Sheet2', index=False)
        st.success("✅ อัปเดตข้อมูลเรียบร้อย!")
    else:
        st.warning("⚠️ ไม่พบข้อมูลลำดับที่/จำนวนในภาพ โปรดตรวจสอบรูปภาพ")

st.subheader("ตาราง Sheet1 (Master)")
st.dataframe(df_s1)
