import streamlit as st
import pandas as pd
import easyocr
import re
from io import BytesIO
from PIL import Image
import numpy as np

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Makro Scan", layout="wide")
st.title("🛒 ระบบสแกนใบสั่งซื้อ Makro")

# ใช้ cache เพื่อไม่ให้โหลด OCR ใหม่ทุกครั้ง (ประหยัดแรมและเร็วขึ้น)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()

uploaded_file = st.file_uploader("อัปโหลดรูปถ่ายบิล Makro", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_np = np.array(image)
    
    with st.spinner("🤖 กำลังวิเคราะห์บิล..."):
        scan_result = reader.readtext(img_np, detail=0)
        full_text = " ".join(scan_result)
        
        excel_rows = []
        # ค้นหารหัส 6 หลัก ตามด้วยข้อความ และลงท้ายด้วยตัวเลข (รองรับทศนิยม)
        items_found = re.findall(r'(\d{6})\s+(.*?)\s+(\d+[\.,]\d{2})', full_text)
        
        if not items_found:
            for line in scan_result:
                match_code = re.search(r'(\d{6})', line)
                match_qty = re.search(r'(\d+[\.,]\d{2})', line)
                if match_code and match_qty:
                    excel_rows.append({
                        "Item": match_code.group(1),
                        "Item des": "รายการสินค้า Makro",
                        "Qty": float(match_qty.group(1).replace(',', '.'))
                    })
        else:
            for item in items_found:
                excel_rows.append({
                    "Item": item[0],
                    "Item des": item[1].strip(),
                    "Qty": float(item[2].replace(',', '.'))
                })
        
        df = pd.DataFrame(excel_rows)
        if not df.empty:
            df = df.drop_duplicates(subset=['Item']).reset_index(drop=True)
            st.success(f"✅ พบข้อมูล {len(df)} รายการ")
            edited_df = st.data_editor(df, use_container_width=True)
            
            # ปุ่มดาวน์โหลด
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False)
            st.download_button("📥 ดาวน์โหลด Excel", output.getvalue(), "Makro_Result.xlsx")
        else:
            st.warning("⚠️ ไม่พบข้อมูลที่อ่านได้จากภาพ ลองถ่ายรูปให้ชัดขึ้นครับ")
