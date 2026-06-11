import streamlit as st
import pandas as pd
import easyocr
import re
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Makro Scan to n1.xlsx", layout="wide")
st.title("🛒 ระบบสแกน Makro เข้าไฟล์ n1.xlsx")

# 1. โหลดไฟล์ Excel หลัก (n1.xlsx)
@st.cache_data
def load_template():
    # โหลดไฟล์และกำหนดบรรทัดหัวตาราง (ปรับเลข 6 ให้ตรงกับไฟล์ของคุณ)
    df = pd.read_excel('n1.xlsx', sheet_name='Sheet1', header=6)
    # ตัดแถวที่รหัสสินค้าว่างทิ้ง (ถ้ามี)
    df = df.dropna(subset=['รหัสสินค้า']) 
    return df

df_master = load_template()
reader = easyocr.Reader(['th', 'en'])

uploaded_file = st.file_uploader("อัปโหลดรูปบิล", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    
    with st.spinner("🤖 กำลังสแกนและดึงข้อมูลลงตาราง..."):
        scan_result = reader.readtext(img_np, detail=0)
        full_text = " ".join(scan_result)
        
        # ค้นหารหัสสินค้า (6 หลัก) และจำนวน
        items_found = re.findall(r'(\d{6})\s+(.*?)\s+(\d+\.?\d*)', full_text)
        
        # 2. นำข้อมูลที่เจอ ไปอัปเดตลงใน df_master
        for item_code, desc, qty in items_found:
            # แปลงรหัสให้เป็น string เพื่อให้ตรงกับในไฟล์ Excel
            mask = df_master['รหัสสินค้า'].astype(str) == str(item_code)
            if mask.any():
                # เติมจำนวนลงในคอลัมน์ 'จำนวนที่สั่งซื้อ'
                df_master.loc[mask, 'จำนวนที่สั่งซื้อ'] = float(qty)

    st.success("✅ สแกนสำเร็จ! ข้อมูลถูกเติมลงในตารางเรียบร้อย")
    
    # 3. แสดงผลตารางที่เติมข้อมูลแล้วให้คุณตรวจทาน
    edited_df = st.data_editor(df_master, use_container_width=True)
    
    # 4. ดาวน์โหลดไฟล์ใหม่
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button("📥 ดาวน์โหลด n1_Updated.xlsx", output.getvalue(), "n1_Updated.xlsx")
