import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

# 1. ข้อมูล Master List ที่ฝังไว้ในโค้ดเลย (ไม่ต้องอัปโหลดไฟล์เพิ่ม)
master_data = {
    1: "หน้ากากหมู", 2: "สันในหมู", 3: "สันนอกหมู", 4: "สะโพกหมู", 
    5: "หัวไหล่หมู", 6: "สันคอหมูบั้ง", 7: "สามชั้นหมู", 12: "ตับหมู", 
    13: "กระเพาะหมู", 16: "ไส้ตันหมูเล็ก" # ใส่ให้ครบทุกรายการตามตารางคุณ
}

st.title("🛒 อัปโหลดรูปบิลเพื่อรับไฟล์ Excel")

uploaded_img = st.file_uploader("อัปโหลดรูปใบสั่งสินค้า", type=["jpg", "png"])

if uploaded_img:
    img = np.array(Image.open(uploaded_img))
    reader = easyocr.Reader(['th', 'en'])
    results = reader.readtext(img)
    
    # ดึงข้อมูลจากรูป
    found_data = {}
    for i, (bbox, text, prob) in enumerate(results):
        if text.isdigit() and int(text) in master_data:
            # สมมติว่าจำนวนอยู่ถัดไป 1 ช่อง
            try:
                qty = results[i+1][1]
                found_data[int(text)] = qty
            except:
                pass
    
    # สร้างตารางจาก Master + ข้อมูลที่พบ
    df = pd.DataFrame(list(master_data.items()), columns=['ลำดับที่', 'รายการสินค้า'])
    df['จำนวนที่สั่งซื้อ'] = df['ลำดับที่'].map(found_data).fillna(0)
    
    st.dataframe(df)
    
    # สร้างปุ่มดาวน์โหลด
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button("📥 ดาวน์โหลด Excel", towrite, "Result.xlsx")
""", unsafe_allow_html=True)
