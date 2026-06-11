import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🔎 โหมดอ่านละเอียด: ดึงข้อมูลทุกตัวจากบิล")

uploaded_file = st.file_uploader("อัปโหลดรูปบิลเพื่ออ่านข้อมูลทั้งหมด", type=["jpg", "png"])

if uploaded_file:
    img = np.array(Image.open(uploaded_file))
    
    # 1. ตั้งค่า Reader ให้ทำงานละเอียดขึ้น
    with st.spinner("🤖 กำลังอ่านบิลทุกบรรทัด..."):
        reader = easyocr.Reader(['th', 'en'])
        # detail=1 จะเก็บพิกัดของข้อความด้วย ช่วยให้เรียงลำดับถูก
        results = reader.readtext(img, detail=1) 
        
    st.subheader("ผลการอ่านข้อมูลทั้งหมด:")
    
    # 2. แสดงผลทุกบรรทัดที่อ่านได้
    data_list = []
    for (bbox, text, prob) in results:
        # กรองเอาเฉพาะข้อความที่อ่านได้ชัดเจน (confidence > 0.3)
        if prob > 0.3:
            data_list.append(text)
            st.write(f"• {text}")

    # 3. ให้คุณตรวจสอบว่าครบไหม
    if len(data_list) > 0:
        st.success(f"อ่านพบทั้งหมด {len(data_list)} รายการ!")
        st.write("ถ้าข้อมูลยังขาดตรงไหน หรืออ่านสลับบรรทัด บอกผมนะครับ ผมจะปรับ Logic การเรียงบรรทัดให้แม่นขึ้น!")
