import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🛒 Makro Scanner: อ่านรูปภาพลงตาราง Master")

# โหลด OCR
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

# ให้คุณอัปโหลดไฟล์ Master ที่คุณมีอยู่ก่อน
master_file = st.file_uploader("อัปโหลดไฟล์ Master List ของคุณ (Excel)", type=["xlsx"])
# อัปโหลดรูปบิลที่ถ่ายมา
bill_img = st.file_uploader("อัปโหลดรูปถ่ายบิล", type=["jpg", "jpeg", "png"])

if master_file and bill_img:
    df_master = pd.read_excel(master_file)
    
    # อ่านรูปภาพ
    img = np.array(Image.open(bill_img))
    results = reader.readtext(img)
    
    # ดึงข้อมูล รหัส + จำนวน จากรูป
    data_map = {}
    for i, (bbox, text, prob) in enumerate(results):
        # ถ้าเจอตัวเลข 6 หลัก (รหัส)
        if len(text) == 6 and text.isdigit():
            # ให้มองหาเลขจำนวนที่อยู่ใกล้ๆ (สมมติว่าเป็นช่องถัดไป)
            # ถ้าตำแหน่งผิด คุณบอกผมได้เลยครับ เดี๋ยวผมปรับเลข Index ให้
            qty = results[i+1][1] if i+1 < len(results) else 0
            data_map[text] = qty
            
    # ตรึงข้อมูลลงตาราง Master
    df_master['จำนวน'] = df_master['Code'].astype(str).map(data_map).fillna(0)
    
    st.dataframe(df_master)
