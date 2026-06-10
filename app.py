import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

st.title("🛒 ระบบอัปเดตฐานข้อมูล (n1.xlsx)")

# 1. โหลดฐานข้อมูลทั้ง 2 ชีต
FILE_PATH = 'n1.xlsx'

def get_data():
    # อ่านไฟล์ Excel โดยแยกชีต
    sheet1 = pd.read_excel(FILE_PATH, sheet_name='Sheet1')
    sheet2 = pd.read_excel(FILE_PATH, sheet_name='Sheet2')
    return sheet1, sheet2

df_s1, df_s2 = get_data()

# 2. ส่วนอัปโหลดรูปภาพ
uploaded_img = st.file_uploader("📸 อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # อัปเดตข้อมูล (บวกยอด)
    for i, (bbox, text, prob) in enumerate(results):
        if text.isdigit() and int(text) <= 26: 
            seq = int(text)
            try:
                qty = results[i+1][1]
                if qty.isdigit():
                    val = int(qty)
                    # อัปเดตทั้ง Sheet1 และ Sheet2 ตามลำดับที่
                    df_s1.loc[df_s1['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] += val
                    df_s2.loc[df_s2['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] += val
            except: pass
    
    # 3. บันทึกกลับลงไฟล์เดิม (บันทึกทับทั้ง 2 ชีต)
    with pd.ExcelWriter(FILE_PATH, engine='openpyxl') as writer:
        df_s1.to_excel(writer, sheet_name='Sheet1', index=False)
        df_s2.to_excel(writer, sheet_name='Sheet2', index=False)
    
    st.success("✅ อัปเดตข้อมูลสำเร็จทั้ง 2 ชีต!")

# 4. แสดงผล
st.subheader("ข้อมูล Sheet1")
st.dataframe(df_s1)
st.subheader("ข้อมูล Sheet2")
st.dataframe(df_s2)
