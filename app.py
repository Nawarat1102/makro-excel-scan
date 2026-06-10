import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🛒 ระบบอัปเดตข้อมูล Makro")

# 1. โหลดไฟล์ (ระบุ skiprows เพื่อข้าม Header ที่เป็นข้อความออก)
# ไฟล์ n1.xlsx ต้องมีอยู่ใน Folder เดียวกับ app.py ใน GitHub
FILE_PATH = 'n1.xlsx'

def load_data():
    # skiprows=6 คือการข้าม 6 บรรทัดแรกเพื่อให้บรรทัดที่ 7 กลายเป็น Header
    df1 = pd.read_excel(FILE_PATH, sheet_name='Sheet1', skiprows=6)
    df2 = pd.read_excel(FILE_PATH, sheet_name='Sheet2', skiprows=4)
    return df1, df2

df_s1, df_s2 = load_data()

# 2. ส่วนอ่านภาพ
uploaded_img = st.file_uploader("📸 อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png", "jpeg"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # วนลูปอ่านค่า
    for i, (bbox, text, prob) in enumerate(results):
        if text.isdigit() and int(text) <= 50: # ลำดับที่
            seq = int(text)
            try:
                qty = results[i+1][1] # ตัวเลขจำนวน
                if qty.isdigit():
                    val = int(qty)
                    # อัปเดตใน DataFrame
                    df_s1.loc[df_s1['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = val
                    df_s2.loc[df_s2['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = val
            except: pass
            
    # 3. บันทึกกลับ
    with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
        df_s1.to_excel(writer, sheet_name='Sheet1', index=False)
        df_s2.to_excel(writer, sheet_name='Sheet2', index=False)
    
    st.success("✅ อัปเดตข้อมูลและบันทึกไฟล์เรียบร้อย!")

# 4. แสดงผล
st.subheader("ฐานข้อมูล Sheet1")
st.dataframe(df_s1)
