import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("🛒 Makro Scanner: แบบจัดเรียงตามบรรทัด")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(image)
    
    with st.spinner("กำลังประมวลผลตำแหน่งแถว..."):
        # อ่านรายละเอียดแบบละเอียด (detail=1)
        results = reader.readtext(img_np)
        
        # จัดกลุ่มข้อมูลเข้าบรรทัดเดียวกันตามตำแหน่ง Y
        lines = {}
        for (bbox, text, prob) in results:
            y_pos = bbox[0][1]
            found = False
            for line_y in lines:
                if abs(line_y - y_pos) < 20: # ถ้าห่างกันไม่เกิน 20px ให้อยู่แถวเดียวกัน
                    lines[line_y].append((bbox[0][0], text))
                    found = True
                    break
            if not found:
                lines[y_pos] = [(bbox[0][0], text)]
        
        # เรียงลำดับบรรทัดตามตำแหน่ง Y (จากบนลงล่าง)
        sorted_lines = sorted(lines.items())
        
        data = []
        for y, words in sorted_lines:
            # เรียงคำในบรรทัดจากซ้ายไปขวา (ตามแกน X)
            words.sort(key=lambda x: x[0])
            line_text = [w[1] for w in words]
            
            # กรองบรรทัดที่น่าจะเป็นสินค้า (ต้องมีเลข 6 หลัก)
            for item in line_text:
                if len(item) == 6 and item.isdigit():
                    # ดึงข้อมูลรอบๆ
                    idx = line_text.index(item)
                    item_code = item
                    item_des = " ".join(line_text[:idx])
                    qty = line_text[-1] if len(line_text) > idx else "0"
                    
                    data.append({"Item": item_code, "Item des": item_des, "Qty": qty})
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
