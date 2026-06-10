import streamlit as st
import pandas as pd
import easyocr
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🛒 Makro Pro Scanner: โหมดตรวจจับตาราง")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("อัปโหลดรูปบิล Makro", type=["jpg", "png"])

if uploaded_file:
    # 1. แปลงรูปให้บอทอ่านง่าย (Binarization - ทำให้เข้มขึ้น)
    img = Image.open(uploaded_file).convert('L') # ปรับเป็นขาวดำ
    img_np = np.array(img)
    _, thresh = cv2.threshold(img_np, 150, 255, cv2.THRESH_BINARY)
    
    st.image(thresh, caption="ภาพที่ AI มองเห็น (เน้นเส้นตาราง)", use_container_width=True)
    
    with st.spinner("กำลังสกัดข้อมูลจากตาราง..."):
        results = reader.readtext(thresh, detail=0)
        
        # ค้นหารหัสสินค้าและชื่อสินค้าด้วยการจับคู่ Pattern
        # บิล Makro: [ชื่อสินค้า] [รหัสสินค้า] [จำนวน]
        data = []
        for i in range(len(results)):
            # ดูว่ามีเลข 6 หลักไหม
            if len(results[i]) == 6 and results[i].isdigit():
                # ถ้าเจอเลขรหัส ให้เอาข้อความก่อนหน้าเป็นชื่อสินค้า
                item_des = results[i-1] if i > 0 else "ไม่ทราบชื่อ"
                qty = results[i+1] if i+1 < len(results) else "0"
                data.append({"Item": results[i], "Item des": item_des, "Qty": qty})
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
