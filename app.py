import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
st.title("🛒 ระบบจัดการฐานข้อมูลใบสั่งสินค้า")

# โหลดฐานข้อมูล Master (ไฟล์ n1.xlsx)
# หมายเหตุ: คุณต้องอัปโหลดไฟล์ n1.xlsx ไว้ในโฟลเดอร์เดียวกับโค้ด
FILE_PATH = 'n1.xlsx'

# โหลดข้อมูล
try:
    df_master = pd.read_excel(FILE_PATH, sheet_name='Sheet1')
except:
    st.error("ไม่พบไฟล์ n1.xlsx โปรดตรวจสอบว่าอัปโหลดไฟล์ไว้ในระบบแล้ว")
    st.stop()

# 1. ส่วนรีเซ็ตฐานข้อมูล
if st.sidebar.button("🔄 รีเซ็ตฐานข้อมูลเป็น 0"):
    df_master['จำนวนที่สั่งซื้อ'] = 0
    df_master.to_excel(FILE_PATH, sheet_name='Sheet1', index=False)
    st.sidebar.success("รีเซ็ตฐานข้อมูลเรียบร้อย!")
    st.rerun()

# 2. อัปโหลดไฟล์รายการสั่งซื้อใหม่ (หรือจะเปลี่ยนเป็นอ่านจากรูปก็ได้)
uploaded_file = st.file_uploader("อัปโหลดไฟล์รายการสั่งซื้อ (Sheet2 format)", type=["csv", "xlsx"])

if uploaded_file:
    df_new = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # แมตช์ข้อมูลจากไฟล์ใหม่มาบวกเพิ่มใน Master
    # สมมติว่าคอลัมน์แรกคือลำดับที่ คอลัมน์ที่สองคือชื่อ และคอลัมน์ที่สามคือจำนวน
    for index, row in df_new.iterrows():
        seq = row[0] # ลำดับที่
        qty = row[2] # จำนวนที่สั่ง
        
        if pd.notnull(qty):
            mask = df_master['ลำดับที่'] == seq
            current_qty = df_master.loc[mask, 'จำนวนที่สั่งซื้อ'].fillna(0).values[0]
            df_master.loc[mask, 'จำนวนที่สั่งซื้อ'] = current_qty + qty

    # บันทึกทับไฟล์เดิม
    df_master.to_excel(FILE_PATH, sheet_name='Sheet1', index=False)
    st.success("✅ อัปเดตข้อมูลและบวกยอดในฐานข้อมูลเรียบร้อย!")

# 3. แสดงผลตาราง Master ปัจจุบัน
st.subheader("ฐานข้อมูลปัจจุบัน (Master List)")
st.dataframe(df_master, use_container_width=True)

# 4. ปุ่มดาวน์โหลด
buffer = io.BytesIO()
df_master.to_excel(buffer, index=False)
st.download_button("📥 ดาวน์โหลดฐานข้อมูลล่าสุด", buffer.getvalue(), "Master_Database_Updated.xlsx")
