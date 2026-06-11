import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO

# ตั้งค่าหน้าเว็บ
st.set_page_config(layout="wide")
st.title("🛒 ระบบสแกน Makro เข้าไฟล์ n1.xlsx")

# 1. โหลดไฟล์ Excel (n1.xlsx) ต้องอยู่ใน Repository เดียวกับโค้ด
@st.cache_data
def load_template():
    # header=6 คือข้าม 6 บรรทัดแรก เพื่อเริ่มอ่านข้อมูลที่บรรทัดที่ 7
    df_s1 = pd.read_excel('n1.xlsx', sheet_name='Sheet1', header=6)
    return df_s1

# 2. ฟังก์ชันหลัก
uploaded_file = st.file_uploader("อัปโหลดรูปบิล Makro", type=["jpg", "png"])
df_master = load_template()

if uploaded_file:
    reader = easyocr.Reader(['th', 'en'])
    img = np.array(Image.open(uploaded_file))
    results = reader.readtext(img)
    
    with st.spinner("🤖 กำลังสแกนเลขและเติมลงช่อง..."):
        for i, (bbox, text, prob) in enumerate(results):
            # หาเลขลำดับที่ (1-50)
            if text.isdigit() and 1 <= int(text) <= 50:
                seq = int(text)
                try:
                    # อ่านจำนวนที่สั่งซื้อ
                    qty = results[i+1][1]
                    if qty.isdigit():
                        val = int(qty)
                        # เติมตัวเลขลงใน DataFrame ให้ตรงแถว
                        df_master.loc[df_master['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = val
                except: continue

    # แสดงผลให้คุณตรวจก่อน
    st.success("✅ สแกนเสร็จแล้ว! ตรวจสอบตัวเลขด้านล่าง")
    edited_df = st.data_editor(df_master, use_container_width=True)
    
    # ปุ่มดาวน์โหลดไฟล์ที่อัปเดตแล้ว
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button("📥 ดาวน์โหลด n1_Updated.xlsx", output.getvalue(), "n1_Updated.xlsx")
