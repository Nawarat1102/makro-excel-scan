import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.title("🛒 ระบบอัปเดตข้อมูล (n1.xlsx)")

# 1. โหลดข้อมูลโดยระบุ header=6 (เพราะหัวตารางอยู่ในบรรทัดที่ 7 ของไฟล์คุณ)
@st.cache_data
def get_data():
    # ไฟล์ n1.xlsx ต้องวางอยู่ในโฟลเดอร์เดียวกับ app.py
    df1 = pd.read_excel('n1.xlsx', sheet_name='Sheet1', header=6)
    df2 = pd.read_excel('n1.xlsx', sheet_name='Sheet2', header=4)
    return df1, df2

df_s1, df_s2 = get_data()

# 2. ส่วนอ่านรูปภาพ
uploaded_img = st.file_uploader("📸 อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # อ่านตัวเลขจากรูป
    for i, (bbox, text, prob) in enumerate(results):
        # ถ้าเจอตัวเลขที่เป็นลำดับที่ 1-26
        if text.isdigit() and int(text) <= 26:
            seq = int(text)
            try:
                # ลองอ่านจำนวนที่อยู่ข้างๆ
                qty = results[i+1][1]
                if qty.isdigit():
                    val = int(qty)
                    # อัปเดตใน DataFrame
                    df_s1.loc[df_s1['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] += val
                    df_s2.loc[df_s2['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] += val
            except: pass
    
    # 3. บันทึกทับไฟล์เดิม (แยกชีตให้ถูกต้อง)
    with pd.ExcelWriter('n1.xlsx', engine='openpyxl') as writer:
        df_s1.to_excel(writer, sheet_name='Sheet1', index=False)
        df_s2.to_excel(writer, sheet_name='Sheet2', index=False)
    
    st.success("✅ บันทึกข้อมูลลง n1.xlsx เรียบร้อย!")

# 4. แสดงผล
st.dataframe(df_s1)
