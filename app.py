import streamlit as st
import pandas as pd
import easyocr
import re
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Makro Pro Scan", layout="wide")
st.title("🛒 ระบบสแกน Makro (เวอร์ชันเจาะจงตำแหน่ง)")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("อัปโหลดรูปบิล Makro", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    with st.spinner("🤖 กำลังสแกนโดยโฟกัสที่รายการสินค้า..."):
        img_np = np.array(image)
        results = reader.readtext(img_np)
        
        # ค้นหาตำแหน่งบรรทัด "รหัสสินค้า"
        start_y = 0
        for (bbox, text, prob) in results:
            if "รหัส" in text:
                start_y = bbox[0][1] # เก็บตำแหน่งแกน Y ที่เจอคำนี้
                break
        
        # ดึงเฉพาะรายการที่อยู่ใต้บรรทัด "รหัสสินค้า"
        items = []
        for (bbox, text, prob) in results:
            if bbox[0][1] > start_y + 20: # ต้องอยู่ต่ำกว่าจุดเริ่มต้น
                # มองหาชุดตัวเลขรหัส 6 หลัก
                match_code = re.search(r'\b(\d{6})\b', text)
                if match_code:
                    items.append({"Item": match_code.group(1), "Data": text})
        
        df = pd.DataFrame(items)
        if not df.empty:
            st.success("✨ เจอรายการสินค้าแล้ว!")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ ยังหาจุดเริ่มอ่านไม่เจอ ลองถ่ายรูปให้เห็นหัวตารางชัดๆ ครับ")
