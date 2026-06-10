import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
import io

st.set_page_config(layout="wide")
st.title("🛒 Makro Auto-Fill: ระบบกรอกข้อมูลบิลเข้า Excel")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

# 1. โหลด Master List (Excel ของคุณ)
master_file = st.file_uploader("อัปโหลดไฟล์ Master List (Excel)", type=["xlsx"])
# 2. โหลดรูปบิล
bill_img = st.file_uploader("อัปโหลดรูปภาพบิล", type=["jpg", "png"])

if master_file and bill_img:
    df = pd.read_excel(master_file) # สมมติว่ามีคอลัมน์ 'ลำดับที่'
    
    img = np.array(Image.open(bill_img))
    with st.spinner("กำลังประมวลผล..."):
        results = reader.readtext(img)
        
        # ค้นหาลำดับที่ และ จำนวน
        scanned_data = {}
        for i, (bbox, text, prob) in enumerate(results):
            # ตรวจสอบว่าเป็นเลขลำดับที่ (สมมติว่าเป็นเลข 1-51)
            if text.isdigit() and 1 <= int(text) <= 60:
                seq = int(text)
                # คาดเดาว่าจำนวนจะอยู่ห่างจากลำดับที่ในแนวนอน
                # ในขั้นตอนนี้หากได้ผลลัพธ์ไม่ตรง สามารถปรับค่า i+1 ได้ครับ
                try:
                    qty = results[i+1][1] 
                    scanned_data[seq] = qty
                except:
                    pass
        
        # เติมค่าลงในคอลัมน์ 'จำนวนที่สั่งซื้อ'
        df['จำนวนที่สั่งซื้อ'] = df['ลำดับที่'].map(scanned_data).fillna(0)
        
        st.dataframe(df)
        
        # ปุ่มดาวน์โหลด
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 ดาวน์โหลด Excel ที่เติมค่าแล้ว", buffer.getvalue(), "Updated_Order.xlsx")
