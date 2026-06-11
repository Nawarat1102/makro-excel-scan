import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🛒 ระบบสแกน Makro (อ่านแม่นยำ & ลงตารางถูกต้อง)")

# 1. โหลดไฟล์แม่แบบจาก GitHub (ไฟล์ n1.xlsx ต้องมีอยู่แล้ว)
@st.cache_data
def load_template():
    # ใช้ header=6 เพื่อให้บรรทัดที่ 7 เป็นหัวตาราง (ลำดับที่, รหัส, รายการ, จำนวน)
    # วิธีนี้จะทำให้ได้ตารางที่ตรงกับไฟล์ n1.xlsx ของคุณเป๊ะๆ
    df = pd.read_excel('n1.xlsx', sheet_name='Sheet1', header=6)
    # ตัดคอลัมน์ที่ไม่จำเป็นออก (ถ้ามี)
    return df

df_master = load_template()

# 2. ส่วนสแกนรูปภาพ
uploaded_file = st.file_uploader("อัปโหลดรูปบิล Makro", type=["jpg", "png", "jpeg"])

if uploaded_file:
    reader = easyocr.Reader(['th', 'en'])
    img = np.array(Image.open(uploaded_file))
    results = reader.readtext(img)
    
    with st.spinner("🤖 กำลังสแกนบิล..."):
        # หาเลขจากบิลและนำไป "แปะ" ใน df_master
        for i, (bbox, text, prob) in enumerate(results):
            # ตรวจสอบว่าเป็นเลขลำดับที่ (1-26)
            if text.isdigit() and 1 <= int(text) <= 26:
                seq = int(text)
                try:
                    # อ่านจำนวนที่สั่งซื้อ (เลขถัดไปในภาพ)
                    qty = results[i+1][1]
                    if qty.isdigit():
                        # เติมตัวเลขลงในช่องที่ตรงกัน
                        df_master.loc[df_master['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = int(qty)
                except: continue
    st.success("✅ สแกนเสร็จแล้ว! ตรวจสอบตัวเลขในตารางด้านล่างได้เลย")

# 3. แสดงตารางให้คุณแก้ไขได้ (ถ้า AI อ่านเลขผิด ก็แก้ตรงนี้ได้เลย)
edited_df = st.data_editor(df_master, use_container_width=True)

# 4. ปุ่มดาวน์โหลดไฟล์ที่ "ถูกต้องตามรูปแบบเดิม"
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    edited_df.to_excel(writer, index=False, sheet_name='Sheet1')

st.download_button(
    label="📥 ดาวน์โหลดไฟล์ Excel ที่กรอกข้อมูลแล้ว",
    data=output.getvalue(),
    file_name="n1_Updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
