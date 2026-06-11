import streamlit as st
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🚀 PaddleOCR: ระบบอ่านบิลประสิทธิภาพสูง")

# โหลดโมเดล (ใช้ภาษาไทย)
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang='th')

ocr = load_ocr()

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    
    with st.spinner("กำลังประมวลผลด้วยโมเดลประสิทธิภาพสูง..."):
        # อ่านภาพ
        result = ocr.ocr(img_np, cls=True)
        
        # จัดเรียงผลลัพธ์
        all_text = []
        for line in result:
            for word in line:
                # word[1][0] คือข้อความ, word[1][1] คือความมั่นใจ (Confidence)
                text = word[1][0]
                conf = word[1][1]
                all_text.append(f"{text} (ความมั่นใจ: {conf:.2f})")
                st.write(f"• {text}")
        
        st.subheader("📋 ข้อมูลดิบที่สกัดได้:")
        st.text_area("ก๊อปปี้ไปวางใน Excel:", value="\n".join([w[1][0] for line in result for w in line]), height=300)
        
