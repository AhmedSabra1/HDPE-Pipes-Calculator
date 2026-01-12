import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="HDPE Pricing Tool", layout="wide", page_icon="🛠️")
st.title("🛠️ HDPE Pipe Pricing & Analysis Tool")

# 2. تحميل قاعدة البيانات (أوتوماتيك)
data_file = 'data.xlsx'  # <-- ده اسم الملف اللي رفعناه

# دالة لتحميل الداتا
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        df.fillna(0, inplace=True)
        return df
    except Exception as e:
        return None

# محاولة تحميل الملف المرفوع مسبقاً
df = None
if os.path.exists(data_file):
    df = load_data(data_file)
    st.success("✅ Database Auto-Loaded successfully!")
else:
    st.warning("⚠️ Default 'data.xlsx' not found in repository.")

# خيار لرفع ملف جديد (لو حبيت تغير الأسعار مؤقتاً)
st.sidebar.header("📂 Update Data")
uploaded_file = st.sidebar.file_uploader("Upload New Excel (Optional)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.fillna(0, inplace=True)
    st.sidebar.success("✅ New Data Loaded!")

# --- باقي البرنامج ---
if df is not None:
    # التأكد من الأعمدة
    required_cols = ['Diameter', 'PN', 'SDR', 'Weight']
    missing = [c for c in required_cols if c not in df.columns]
    
    if missing:
        st.error(f"⚠️ Error: Missing columns {missing}")
    else:
        # دالة البحث عن أقرب قطر
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        # 3. التبويبات (Tabs)
        tab1, tab2 = st.tabs(["1️⃣ Price Calculator (Forward)", "2️⃣ Reverse Analysis (Backward)"])

        # ==========================
        # TAB 1: حساب السعر
        # ==========================
        with tab1:
            st.subheader("1. Calculate Meter Price from Ton Price")
            
            col1, col2 = st.columns(2)
            with col1:
                ton_price = st.number_input("HDPE Ton Price (EGP):", min_value=0.0, step=1000.0, format="%.2f")
                unit = st.radio("Input Unit:", ["mm", "Inch"], horizontal=True)
                dia_input = st.number_input("Diameter:", min_value=0.0, step=10.0)
            
            with col2:
                mode = st.radio("Class Specification:", ["PN", "SDR"], horizontal=True, key="t1_mode")
                if mode in df.columns:
                    avail_vals = sorted(df[mode].unique().tolist())
                    spec_val = st.selectbox(f"Select {mode} Value:", avail_vals, key="t1_spec")
                else:
                    st.error(f"Column {mode} not found in Excel")
                    spec_val = None
            
            if st.button("Calculate Price 🚀", type="primary"):
                if ton_price > 0 and dia_input > 0 and spec_val is not None:
                    avail_dias = sorted(df['Diameter'].unique().tolist())
                    target_dia_mm = dia_input * 25.4 if unit == "Inch" else dia_input
                    actual_dia = find_nearest(avail_dias, target_dia_mm)
                    
                    mask = (df['Diameter'] == actual_dia) & (df[mode] == spec_val)
                    row = df[mask]
                    
                    st.markdown("### 📊 Result:")
                    if row.empty:
                        st.warning(f"❌ Standard Not Found: {actual_dia}mm with {mode} {spec_val}")
                    else:
                        weight = row.iloc[0]['Weight']
                        if weight <= 0:
                            st.error(f"⚠️ NOT PRODUCED: Diameter {actual_dia}mm is not manufactured.")
                        else:
                            price = (ton_price / 1000) * weight
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Selected Pipe (mm)", f"{actual_dia}")
                            m2.metric("Weight / Meter", f"{weight} kg")
                            m3.metric("Final Price / Meter", f"{price:,.2f} EGP")
                            if unit == "Inch":
                                st.caption(f"ℹ️ Converted from {dia_input} Inch → {target_dia_mm:.1f} mm")

        # ==========================
        # TAB 2: الهندسة العكسية
        # ==========================
        with tab2:
            st.subheader("2. Analyze Offer (Find Hidden Ton Price)")
            
            c1, c2 = st.columns(2)
            with c1:
                offer_price = st.number_input("Offer Meter Price (EGP):", min_value=0.0, step=10.0)
                t2_dia = st.selectbox("Select Diameter (mm):", sorted(df['Diameter'].unique().tolist()))
            
            with c2:
                t2_mode = st.radio("Class Specification:", ["PN", "SDR"], horizontal=True, key="t2_mode")
                if t2_mode in df.columns:
                    t2_vals = sorted(df[t2_mode].unique().tolist())
                    t2_spec = st.selectbox(f"Select {t2_mode} Value:", t2_vals, key="t2_spec")
                else:
                    t2_spec = None

            if st.button("Analyze Offer 🔍", type="secondary"):
                if offer_price > 0 and t2_spec is not None:
                    mask2 = (df['Diameter'] == t2_dia) & (df[t2_mode] == t2_spec)
                    row2 = df[mask2]
                    
                    if row2.empty:
                        st.warning("❌ Item not found in database.")
                    else:
                        w2 = row2.iloc[0]['Weight']
                        if w2 <= 0:
                            st.error("⚠️ Cannot Analyze: Weight is 0 (Not Produced).")
                        else:
                            est_ton = (offer_price / w2) * 1000
                            st.success(f"🏭 Estimated HDPE Ton Price: **{est_ton:,.2f} EGP**")
else:
    st.info("👋 Please upload 'data.xlsx' to GitHub or use the uploader on the left.")
