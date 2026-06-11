import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🔎 โหมดทดสอบ: ดูว่า AI อ่านเลขอะไรจากรูปได้บ้าง")

uploaded_file = st.file_uploader("อัปโหลดรูปบิล เพื่อทดสอบอ่านเลข", type=["jpg", "png"])

if uploaded_file:
    img = np.array(Image.open(uploaded_file))
    st.image(img, caption="รูปที่อัปโหลด", use_container_width=True)
    
    with st.spinner("🤖 กำลังสแกนเลขจากรูป..."):
        reader = easyocr.Reader(['th', 'en'])
        results = reader.readtext(img)
        
        # สร้างรายการแสดงเลขที่อ่านได้
        st.subheader("ผลการอ่านข้อมูลจากภาพ:")
        detected_data = []
        for (bbox, text, prob) in results:
            if text.isdigit(): # กรองเอาเฉพาะตัวเลข
                detected_data.append(text)
        
        # แสดงเลขที่อ่านได้ทั้งหมดให้คุณดู
        st.write("ตัวเลขที่อ่านได้จากรูปมีดังนี้:")
        st.info(", ".join(detected_data))
        
        st.write("---")
        st.write("ลองดูครับว่ามีเลข ลำดับที่ หรือ จำนวนที่คุณต้องการอยู่ในนี้ไหม?")
        st.write("ถ้ามีเลขที่ถูกต้องแล้ว เดี๋ยวผมจะพาไปขั้นตอนถัดไป คือการจับคู่เลขพวกนี้ลงตารางครับ")
