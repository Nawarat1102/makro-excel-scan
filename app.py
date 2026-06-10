import streamlit as st
import pandas as pd
import easyocr
import io

st.set_page_config(layout="wide")
st.title("🛒 Makro Data Processor (Final Version)")

# โหลด OCR ครั้งเดียว
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

# 1. รับไฟล์ Master List
master_file = st.file_uploader("อัปโหลดไฟล์ Master Excel (ต้องมีคอลัมน์ 'Code')", type=["xlsx"])

if master_file:
    master_df = pd.read_excel(master_file)
    st.write("Master List ที่โหลดเข้ามา:")
    st.dataframe(master_df.head())
    
    # 2. รับไฟล์ภาพบิล
    img_file = st.file_uploader("อัปโหลดรูปบิล Makro", type=["jpg", "png"])
    
    if img_file:
        with st.spinner("กำลังประมวลผลข้อมูล..."):
            # สแกนเอา Text ทั้งหมดออกมาเป็น List
            raw_data = reader.readtext(img_file.getvalue(), detail=0)
            
            # แปลง Text เป็น Dictionary: {รหัส: จำนวน}
            # เราใช้เงื่อนไข: ถ้าเจอตัวเลข 6 หลัก ให้มองหาตัวเลขที่เป็นจำนวนสั่งซื้อ
            processed_map = {}
            for i, text in enumerate(raw_data):
                if len(text) == 6 and text.isdigit():
                    # บิล Makro ตัวเลขจำนวนมักจะอยู่ถัดไป 1-2 ลำดับ
                    try:
                        qty = float(raw_data[i+1])
                        processed_map[text] = qty
                    except:
                        pass
            
            # อัปเดตตาราง Master
            master_df['จำนวน'] = master_df['Code'].astype(str).map(processed_map).fillna(0)
            
            st.success("✨ จับคู่ข้อมูลสำเร็จ!")
            st.dataframe(master_df)
            
            # ปุ่มดาวน์โหลด
            buffer = io.BytesIO()
            master_df.to_excel(buffer, index=False)
            st.download_button("📥 ดาวน์โหลด Excel ที่ใส่จำนวนแล้ว", buffer.getvalue(), "Result_Makro.xlsx")
