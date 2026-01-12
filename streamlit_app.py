import streamlit as st
import pandas as pd
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(page_title="HDPE Pricing Tool", layout="wide", page_icon="🛠️")

st.title("🛠️ HDPE Pipe Pricing & Analysis Tool")
st.markdown("---")

# 2. القائمة الجانبية لرفع الملف
st.sidebar.header("📂 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Excel Database", type=["xlsx"])

# دالة للبحث عن أقرب قطر (للتحويل من بوصة)
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

if uploaded_file is not None:
    # قراءة الملف
    try:
        df = pd.read_excel(uploaded_file)
        df.fillna(0, inplace=True)
        st.sidebar.success("✅ Database Loaded Successfully!")
        
        # التأكد من الأعمدة
        required_cols = ['Diameter', 'PN', 'SDR', 'Weight']
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ Excel file must contain columns: {required_cols}")
        else:
            
            # 3. إنشاء التبويبات (Tabs)
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
                    # قائمة القيم تتحدث بناء على الاختيار
                    avail_vals = sorted(df[mode].unique().tolist())
                    spec_val = st.selectbox(f"Select {mode} Value:", avail_vals, key="t1_spec")
                
                if st.button("Calculate Price 🚀", type="primary"):
                    if ton_price > 0 and dia_input > 0:
                        # منطق التحويل من بوصة
                        avail_dias = sorted(df['Diameter'].unique().tolist())
                        target_dia_mm = dia_input * 25.4 if unit == "Inch" else dia_input
                        
                        # البحث عن أقرب قطر قياسي
                        actual_dia = find_nearest(avail_dias, target_dia_mm)
                        
                        # البحث في الداتا
                        mask = (df['Diameter'] == actual_dia) & (df[mode] == spec_val)
                        row = df[mask]
                        
                        st.markdown("### 📊 Result:")
                        
                        if row.empty:
                            st.warning(f"❌ Standard Not Found: {actual_dia}mm with {mode} {spec_val}")
                        else:
                            weight = row.iloc[0]['Weight']
                            
                            if weight <= 0:
                                st.error(f"⚠️ NOT PRODUCED: Diameter {actual_dia}mm ({mode} {spec_val}) is not manufactured.")
                            else:
                                price = (ton_price / 1000) * weight
                                
                                # عرض النتيجة في كروت
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
                    t2_vals = sorted(df[t2_mode].unique().tolist())
                    t2_spec = st.selectbox(f"Select {t2_mode} Value:", t2_vals, key="t2_spec")

                if st.button("Analyze Offer 🔍", type="secondary"):
                    if offer_price > 0:
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
                                st.info("Use this price in Tab 1 to price other items!")

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("👋 Welcome! Please upload your Excel Database from the sidebar to start.")