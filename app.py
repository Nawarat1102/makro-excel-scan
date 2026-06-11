import streamlit as st
import pandas as pd
import easyocr
import re
from PIL import Image
import numpy as np

# โหลด OCR ครั้งเดียว
reader = easyocr.Reader(['th', 'en'])

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    scan_result = reader.readtext(img_np, detail=0)
    full_text = " ".join(scan_result)

    # 1. ระบบตรวจจับประเภทบิล
    if "MAKRO" in full_text.upper() or "แม็คโคร" in full_text:
        st.info("Detected: บิล Makro")
        # ใช้ Logic ดึงข้อมูล Makro (หาเลข 6 หลัก)
        items = re.findall(r'(\d{6})\s+(.*?)\s+(\d+[\.,]\d{2})', full_text)
        
    elif "BIG C" in full_text.upper() or "บิ๊กซี" in full_text:
        st.info("Detected: บิล Big C")
        # ใช้ Logic ดึงข้อมูล Big C (อาจจะหาเลข 13 หลัก หรือรูปแบบอื่น)
        items = re.findall(r'(\d{13})\s+(.*?)\s+(\d+)', full_text)
        
    else:
        st.warning("⚠️ ไม่รู้จักรูปแบบบิลนี้ หรืออ่านชื่อร้านไม่ชัด")
        items = []

    # 2. แสดงผล
    if items:
        df = pd.DataFrame(items, columns=["Code", "Description", "Qty"])
        st.dataframe(df)
