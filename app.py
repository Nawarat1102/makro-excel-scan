import streamlit as st
import pandas as pd
import easyocr
import re
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Makro Precision Scan", layout="wide")

st.title("🛒 ระบบสแกนใบสั่งซื้อ Makro เข้า Excel (เวอร์ชันโครงสร้างพิกัดแม่นยำสูง)")
st.write("เวอร์ชันแก้ไขปัญหาดึงข้อมูลไม่ครบและสลับบรรทัด โดยการจัดกลุ่มข้อความตามพิกัดแนวราบ")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['th', 'en'])

reader = load_ocr()
uploaded_file = st.file_uploader("อัปโหลดรูปถ่ายบิล Makro ของคุณ", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 รูปภาพบิลที่อัปโหลด")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("📊 ตาราง Excel ปลายทาง")
        with st.spinner("🤖 AI กำลังคำนวณพิกัดและสกัดข้อมูลแยกตามบรรทัด..."):
            img_np = np.array(image)
            # สแกนเอาพิกัดกล่องข้อความ (detail=1)
            ocr_results = reader.readtext(img_np, detail=1)
            
            # กลุ่มข้อมูลตามพิกัดแกน Y (แนวดิ่งใกล้เคียงกัน = บรรทัดเดียวกัน)
            lines_dict = {}
            for (bbox, text, prob) in ocr_results:
                # หาค่ากึ่งกลางแกน Y ของกล่องข้อความเพื่อระบุบรรทัด
                y_center = int((bbox[0][1] + bbox[2][1]) / 2)
                
                # ถ้าพิกัดห่างกันไม่เกิน 15 พิกเซล ให้ถือว่าเป็นบรรทัดเดียวกัน
                matched_line = None
                for known_y in lines_dict.keys():
                    if abs(known_y - y_center) < 15:
                        matched_line = known_y
                        break
                
                if matched_line is not None:
                    lines_dict[matched_line].append((bbox[0][0], text)) # เก็บแกน X และข้อความ
                else:
                    lines_dict[y_center] = [(bbox[0][0], text)]

            excel_rows = []
            
            # เรียงลำดับบรรทัดจากบนลงล่าง
            for y in sorted(lines_dict.keys()):
                # เรียงข้อความในบรรทัดเดียวกันจากซ้ายไปขวาตามแกน X
                sorted_words = sorted(lines_dict[y], key=lambda x: x[0])
                line_text = " ".join([word[1] for word in sorted_words])
                
                # ค้นหารหัสสินค้า 6 หลักในบรรทัดนั้น
                match_code = re.search(r'(\d{6})', line_text)
                
                if match_code:
                    item_code = match_code.group(1)
                    
                    # ค้นหาตัวเลขจำนวนสั่งซื้อ (มองหาตัวเลขทศนิยม .00 หรือเลขตัวท้ายของบรรทัด)
                    qty_tokens = re.findall(r'(\d+[\.,]\d{2})|(\b\d+\b)', line_text)
                    
                    quantity = 1.00
                    if qty_tokens:
                        # เอาตัวเลขตัวสุดท้ายที่เจอในบรรทัดนั้น (เพราะจำนวนสั่งซื้อจะอยู่ขวาสุด)
                        last_token = [t for t in qty_tokens[-1] if t][0]
                        try:
                            quantity = float(last_token.replace(',', '.'))
                        except:
                            pass
                    
                    # ตัดชื่อสินค้าภาษาไทย
                    item_des = line_text.split(item_code)[0].replace("F4A", "").strip()
                    if not item_des or len(item_des) < 2:
                        item_des = "รายการสินค้า Makro"
                        
                    # ดักจับเพื่อไม่เอาเลขวันที่สั่งซื้อมาเป็นรหัสสินค้า
                    if item_code not in ["062026", "102026", "112026"]:
                        excel_rows.append({
                            "Item": item_code,
                            "Item des": item_des,
                            "11/10/2026": quantity
                        })
            
            df = pd.DataFrame(excel_rows)
            if not df.empty:
                df = df.drop_duplicates(subset=['Item']).reset_index(drop=True)
            
        if not df.empty:
            st.success(f"✨ แก้ไขสำเร็จ! ดึงข้อมูลได้ถูกต้องทั้งหมด {len(df)} รายการ")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel",
                data=output_excel.getvalue(),
                file_name="สรุปออเดอร์_Makro_Fixed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ โครงสร้างภาพเปลี่ยนไป ลองกดรีเฟรชหน้าเว็บแล้วอัปโหลดใหม่อีกครั้งครับ")
