import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🔎 โหมดอ่านข้อมูลดิบ (Raw Extraction)")

# โหลดโมเดล
@st.cache_resource
def load_ocr():
    # ใช้ค่า default เพื่อความเสถียรที่สุด
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    
    with st.spinner("กำลังอ่านข้อมูล..."):
        # ใช้ detail=1 เพื่อดึงข้อมูลเชิงพิกัดมาเรียงใหม่
        results = reader.readtext(img_np, detail=1)
        
        # กรองผลลัพธ์ตามค่า Y (ความสูง) เพื่อเรียงบรรทัดจากบนลงล่าง
        # วิธีนี้จะทำให้ลำดับตัวหนังสือไม่สลับไปมา
        results.sort(key=lambda x: x[0][0][1])
        
        # แสดงผลลัพธ์ดิบ
        st.subheader("ผลการอ่านข้อมูลทั้งหมด:")
        
        all_text = []
        for (bbox, text, prob) in results:
            all_text.append(text)
            st.write(f"- {text}")
        
        # ให้คุณก๊อปปี้ไปวางใน Excel ได้ง่ายที่สุด
        st.subheader("📋 ก๊อปปี้ข้อมูลไปวางใน Excel:")
        st.text_area("ข้อมูลที่อ่านได้", value="\n".join(all_text), height=400)
