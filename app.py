import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("👁️ โหมดอ่านดิบ: ดึงทุกตัวอักษรจากบิล")

# โหลด OCR แบบไม่ต้องกรองอะไรเลย
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    
    with st.spinner("🤖 กำลังอ่านทุกบรรทัด..."):
        # detail=1 เพื่อเอาตำแหน่งมาช่วยเรียงลำดับ
        results = reader.readtext(img_np, detail=1)
        
        # เรียงลำดับจากบนลงล่างตามค่า Y
        results.sort(key=lambda x: x[0][0][1])
        
        st.subheader("📋 ข้อมูลดิบที่อ่านได้ (ทั้งหมด):")
        
        # แสดงผลแบบข้อความยาวๆ เพื่อให้คุณเช็คว่ามันอ่านครบไหม
        full_text_list = []
        for (bbox, text, prob) in results:
            full_text_list.append(text)
            st.text(f"อ่านได้: {text} (ความมั่นใจ: {prob:.2f})")
        
        st.divider()
        st.subheader("💡 รวบยอดเป็นข้อความเดียว:")
        st.text_area("ก๊อปปี้ไปวางใน Excel ได้เลย:", value="\n".join(full_text_list), height=300)
