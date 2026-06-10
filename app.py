import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide")
st.title("🛒 Makro Excel Generator")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(image)
    
    with st.spinner("กำลังดึงรายการสินค้า..."):
        # อ่านค่าแบบ Raw text
        results = reader.readtext(img_np)
        
        # กรองเอาเฉพาะตัวเลข 6 หลัก (รหัสสินค้า)
        extracted_data = []
        for (bbox, text, prob) in results:
            if len(text) == 6 and text.isdigit():
                extracted_data.append({"Item": text, "Qty": 1})
        
        # สร้าง DataFrame พื้นฐาน
        df = pd.DataFrame(extracted_data)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # ปุ่มโหลด Excel (ตรงนี้จะกลับมาครับ)
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False)
            towrite.seek(0)
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel",
                data=towrite,
                file_name="makro_data.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("ไม่พบรหัสสินค้า 6 หลักในภาพ โปรดเช็คความชัดของรูป")
