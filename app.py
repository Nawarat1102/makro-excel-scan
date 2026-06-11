import streamlit as st
import pandas as pd
import easyocr
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🛒 ระบบสแกน Makro (เวอร์ชันรวมร่าง: ชัดขึ้น + ลงตารางถูกต้อง)")

# 1. โหลด Template
@st.cache_data
def load_template():
    return pd.read_excel('n1.xlsx', sheet_name='Sheet1', header=6)

df_master = load_template()
reader = easyocr.Reader(['th', 'en'])

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    # 2. ปรับภาพให้ชัดด้วย OpenCV ก่อนอ่าน
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    with st.spinner("🤖 กำลังสแกนและจับคู่ข้อมูล..."):
        # 3. อ่านภาพที่ปรับแล้ว
        results = reader.readtext(thresh, detail=1)
        
        # 4. Logic จับคู่: หา "ลำดับที่" แล้วเอา "จำนวน" มาลง
        for i, (bbox, text, prob) in enumerate(results):
            if text.isdigit() and 1 <= int(text) <= 50:
                seq = int(text)
                try:
                    # พยายามหาเลขจำนวนที่อยู่ถัดไปในแถว
                    qty = results[i+1][1]
                    if qty.isdigit():
                        df_master.loc[df_master['ลำดับที่'] == seq, 'จำนวนที่สั่งซื้อ'] = int(qty)
                except: continue

    st.success("✅ อัปเดตข้อมูลเสร็จแล้ว!")
    edited_df = st.data_editor(df_master, use_container_width=True)
    
    # 5. ปุ่มดาวน์โหลด
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
    st.download_button("📥 ดาวน์โหลดไฟล์ที่อัปเดต", output.getvalue(), "n1_Updated.xlsx")
