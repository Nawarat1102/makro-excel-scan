import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Makro Order Merger", layout="wide")
st.title("🛒 ระบบรวมข้อมูลใบสั่งสินค้า Makro")
st.subheader("อัปโหลดไฟล์ Master (Sheet1) และไฟล์ข้อมูลจำนวน (Sheet2) เพื่อรวมตาราง")

# 1. อัปโหลดไฟล์ Master (Sheet1)
file1 = st.file_uploader("อัปโหลดไฟล์ Master (Sheet1)", type=["csv", "xlsx"])
# 2. อัปโหลดไฟล์จำนวน (Sheet2)
file2 = st.file_uploader("อัปโหลดไฟล์ที่มีจำนวน (Sheet2)", type=["csv", "xlsx"])

if file1 and file2:
    # อ่านไฟล์
    df1 = pd.read_csv(file1) if file1.name.endswith('.csv') else pd.read_excel(file1)
    df2 = pd.read_csv(file2) if file2.name.endswith('.csv') else pd.read_excel(file2)
    
    # ล้างข้อมูลและจับคู่: ใช้คอลัมน์ 'ลำดับที่' เชื่อมกัน
    # เราจะดึงคอลัมน์ 'จำนวนที่สั่งซื้อ' จาก df2 ไปแปะใน df1
    df_merged = df1.copy()
    
    # ทำการ Merge ข้อมูล
    df_merged = df_merged.merge(df2[['ลำดับที่', 'จำนวนที่สั่งซื้อ']], on='ลำดับที่', how='left', suffixes=('', '_new'))
    
    # อัปเดตช่องจำนวนให้เป็นค่าใหม่จากไฟล์ที่ 2
    if 'จำนวนที่สั่งซื้อ_new' in df_merged.columns:
        df_merged['จำนวนที่สั่งซื้อ'] = df_merged['จำนวนที่สั่งซื้อ_new'].fillna(df_merged['จำนวนที่สั่งซื้อ'])
        df_merged = df_merged.drop(columns=['จำนวนที่สั่งซื้อ_new'])
        
    st.success("✅ รวมข้อมูลสำเร็จ! ดาวน์โหลดได้เลย")
    st.dataframe(df_merged)
    
    # ปุ่มดาวน์โหลด
    towrite = io.BytesIO()
    df_merged.to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button("📥 ดาวน์โหลดไฟล์ที่รวมแล้ว", towrite, "Final_Order_List.xlsx")
