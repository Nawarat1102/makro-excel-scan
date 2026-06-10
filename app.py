import import streamlit as st
import pandas as pd
import easyocr
import re
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Makro Automated Scan", layout="wide")

st.title("🛒 ระบบสแกนใบสั่งซื้อ Makro เข้า Excel")
st.write("วิธีใช้: เพียงแค่อัปโหลดรูปภาพใบสั่งซื้อ ระบบจะสกัดข้อมูลเข้าตารางให้ทันที")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("เลือกไฟล์รูปภาพใบสั่งซื้อ (JPG หรือ PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 รูปภาพใบสั่งซื้อ")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("📊 ข้อมูลที่ดึงเข้าล็อก Excel")
        with st.spinner("🤖 ระบบกำลังอ่านข้อความภาษาไทยและตัวเลข..."):
            img_np = np.array(image)
            ocr_results = reader.readtext(img_np)
            excel_rows = []
            
            for (bbox, text, prob) in ocr_results:
                clean_text = text.strip()
                match_code = re.search(r'\b(\d{6})\b', clean_text)
                
                if match_code:
                    item_code = match_code.group(1)
                    match_qty = re.search(r'(\d+[\.,]\d{2})', clean_text)
                    item_des = clean_text.split(item_code)[0].replace("F4A", "").strip()
                    if not item_des or len(item_des) < 2:
                        item_des = "รายการสินค้า Makro"
                    
                    qty_str = match_qty.group(1).replace(',', '.') if match_qty else "1.00"
                    
                    excel_rows.append({
                        "Item": item_code,
                        "Item des": item_des,
                        "11/10/2026": float(qty_str)
                    })
            
            df = pd.DataFrame(excel_rows)
            if not df.empty:
                df = df.drop_duplicates(subset=['Item']).reset_index(drop=True)
            
        if not df.empty:
            st.success(f"✨ ดึงข้อมูลสำเร็จทั้งหมด {len(df)} รายการ!")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel",
                data=output_excel.getvalue(),
                file_name="สรุปออเดอร์_Makro.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ ไม่พบข้อมูลรหัสสินค้า 6 หลัก ลองใช้รูปที่ชัดกว่านี้ครับ")
            st.warning("⚠️ ไม่พบข้อมูลรหัสสินค้า 6 หลักในรูปภาพนี้ ลองตรวจสอบความชัดเจนหรือปรับมุมกล้องถ่ายตรงๆ อีกครั้งครับ")
