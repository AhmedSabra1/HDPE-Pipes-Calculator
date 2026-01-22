import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. Page Config & Professional Styling
# ==========================================
st.set_page_config(
    page_title="Infra Cost Master | Eng. Ahmed",
    layout="wide",
    page_icon="🏗️"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem; 
        color: #0E1117; 
        text-align: center; 
        font-weight: 800; 
        margin-bottom: 10px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-header {
        font-size: 1.2rem; 
        color: #555; 
        text-align: center; 
        margin-bottom: 25px; 
        font-style: italic;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
    }
</style>
<div class="main-header">🏗️ Infrastructure Pricing Master Tool</div>
<div class="sub-header">Advanced Estimation & Reverse Engineering System</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State (Shopping Cart)
# ==========================================
if 'quote_list' not in st.session_state:
    st.session_state.quote_list = []

# ==========================================
# 3. Sidebar (Settings & Branding)
# ==========================================
st.sidebar.header("⚙️ System Settings")

material_type = st.sidebar.radio(
    "Select Pipe Material:",
    ("HDPE", "uPVC"),
    index=0
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 👨‍💻 Developed By")
st.sidebar.markdown("**Eng. Ahmed**")
st.sidebar.caption("Infrastructure Cost Estimation Expert")
st.sidebar.markdown(
    """
    <a href="https://www.linkedin.com/in/ahmed-sabra-115386164/" target="_blank" style="text-decoration:none;">
        <button style="
            background-color:#0077b5; 
            color:white; 
            border:none; 
            padding:10px; 
            border-radius:5px; 
            cursor:pointer; 
            width:100%;
            font-weight:bold;">
            Connect on LinkedIn 🔗
        </button>
    </a>
    """, 
    unsafe_allow_html=True
)

# ==========================================
# 4. Helper Functions (Logic Core)
# ==========================================
data_file = 'data.xlsx'

@st.cache_data
def load_data(file_path, sheet_name):
    try:
        xl = pd.ExcelFile(file_path)
        if sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Auto-Cleaning Loop
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
                    df[col] = df[col].replace('NAN', '-')
            
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
            
            return df
        return None
    except Exception as e:
        return None

def create_pdf(dataframe):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=18, alignment=1, spaceAfter=20)
    elements.append(Paragraph(f"Pipe Quotation: {material_type}", title_style))
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    info_text = f"<b>Date:</b> {date_str}<br/><b>Prepared By:</b> Eng. Ahmed<br/><b>Generated via:</b> Infra Cost Master Tool"
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    print_df = dataframe.copy()
    data = [print_df.columns.to_list()] + print_df.values.tolist()
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3D59")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 40))
    footer_text = "This quotation is an estimation based on raw material market prices."
    elements.append(Paragraph(footer_text, styles['Italic']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# 5. Main Application Logic
# ==========================================
df = None
if os.path.exists(data_file):
    df = load_data(data_file, material_type)

if df is None:
    st.warning(f"⚠️ Database file 'data.xlsx' not found. Please upload '{material_type}' sheet.")
    uploaded = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name=material_type)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
        except:
            st.error("Error reading uploaded file.")

if df is not None:
    base_cols = ['Diameter', 'Weight']
    # هنا الكود هيشوف العماويد الجديدة بتاعتك (SDR, SN, Class, Application...)
    spec_cols = [c for c in df.columns if c not in base_cols]

    tab1, tab2 = st.tabs([f"💰 {material_type} Quotation Builder", "🕵️ Reverse Analysis"])

    # ----------------------------------------------------
    # TAB 1: Quotation Builder
    # ----------------------------------------------------
    with tab1:
        st.info("💡 **Batch Mode:** Enter multiple diameters separated by comma (e.g., 110, 160, 200).")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            ton_label = "Raw Material Price" if material_type == "HDPE" else "Mix Price"
            ton_price = st.number_input(f"{ton_label} (EGP/Ton):", min_value=0.0, step=500.0, format="%.2f")
            dia_unit = st.radio("Diameter Unit:", ["mm", "Inch"], horizontal=True)
        
        with c2:
            dia_input_str = st.text_input("Diameters (comma separated):", placeholder="e.g. 110, 200, 315")

        user_specs = {}
        if spec_cols:
            st.markdown("### 🛠️ Pipe Specifications")
            cols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with cols[idx]:
                    unique_vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    unique_vals.insert(0, "-") 
                    val = st.selectbox(f"{col}", unique_vals, key=f"t1_{col}")
                    user_specs[col] = val

        if st.button(f"Calculate Batch 🚀", type="primary"):
            if ton_price > 0 and dia_input_str:
                try:
                    raw_dias = dia_input_str.replace(" ", ",").split(",")
                    target_dias = [float(x) for x in raw_dias if x.strip() != ""]
                    
                    batch_results = []
                    all_dias_db = sorted(df['Diameter'].unique().tolist())

                    for d_in in target_dias:
                        target_mm = d_in * 25.4 if dia_unit == "Inch" else d_in
                        actual_dia = all_dias_db[(np.abs(np.asarray(all_dias_db) - target_mm)).argmin()]
                        
                        mask = (df['Diameter'] == actual_dia)
                        for k, v in user_specs.items():
                            if v != "-":
                                mask &= (df[k] == v)
                        
                        row = df[mask]
                        if not row.empty:
                            match = row.iloc[0]
                            weight = match['Weight']
                            if weight > 0:
                                price = (ton_price / 1000) * weight
                                item = {
                                    "Material": material_type,
                                    "Diameter": actual_dia,
                                    "Weight (kg/m)": round(weight, 3),
                                    "Price (EGP/m)": round(price, 2)
                                }
                                for col in spec_cols:
                                    item[col] = match[col]
                                batch_results.append(item)
                    
                    if batch_results:
                        st.session_state.current_batch = batch_results
                        st.success(f"✅ Successfully calculated {len(batch_results)} items!")
                    else:
                        st.warning("❌ No matching pipes found.")
                except ValueError:
                    st.error("⚠️ Invalid input.")

        if 'current_batch' in st.session_state and st.session_state.current_batch:
            st.markdown("---")
            st.markdown("### 👁️ Preview Results")
            st.dataframe(pd.DataFrame(st.session_state.current_batch), use_container_width=True)
            
            col_add, col_disc = st.columns([1, 4])
            with col_add:
                if st.button("➕ Add to Final Quotation"):
                    st.session_state.quote_list.extend(st.session_state.current_batch)
                    full_df = pd.DataFrame(st.session_state.quote_list)
                    sort_keys = ['Material', 'Diameter'] + [c for c in spec_cols if c in full_df.columns]
                    full_df = full_df.sort_values(by=sort_keys, ascending=True)
                    st.session_state.quote_list = full_df.to_dict('records')
                    del st.session_state.current_batch
                    st.toast("Items Added & Sorted!", icon="✅")
                    st.rerun()
            with col_disc:
                if st.button("❌ Discard Batch"):
                    del st.session_state.current_batch
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Final Quotation List")
        if len(st.session_state.quote_list) > 0:
            final_df = pd.DataFrame(st.session_state.quote_list)
            st.dataframe(final_df, use_container_width=True)
            ac1, ac2 = st.columns(2)
            with ac1:
                pdf_byte = create_pdf(final_df)
                st.download_button("📄 Download PDF Quotation", data=pdf_byte, file_name=f"Infra_Offer.pdf", mime='application/pdf', type="primary")
            with ac2:
                if st.button("🗑️ Clear All Items"):
                    st.session_state.quote_list = []
                    st.rerun()
        else:
            st.info("Your quotation is empty.")

    # ----------------------------------------------------
    # TAB 2: Reverse Engineering
    # ----------------------------------------------------
    with tab2:
        st.markdown("### 🕵️ Analyze Supplier Offer")
        rc1, rc2 = st.columns(2)
        with rc1:
            offer_price = st.number_input("Offer Price (EGP/m):", min_value=0.0, step=10.0)
        with rc2:
            rev_dia = st.selectbox("Select Diameter:", sorted(df['Diameter'].unique().tolist()), key="rev_dia")
        
        rev_specs = {}
        if spec_cols:
            st.markdown("**Specific Pipe Details:**")
            rcols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with rcols[idx]:
                    clean_vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    val = st.selectbox(f"{col}", clean_vals, key=f"t2_{col}")
                    rev_specs[col] = val

        if st.button("Analyze Price 🔍", type="secondary"):
            if offer_price > 0:
                mask2 = (df['Diameter'] == rev_dia)
                for k, v in rev_specs.items():
                    mask2 &= (df[k] == v)
                row2 = df[mask2]
                if row2.empty:
                    st.warning("❌ No pipe found.")
                else:
                    w2 = row2.iloc[0]['Weight']
                    if w2 > 0:
                        est_ton = (offer_price / w2) * 1000
                        st.success(f"🏭 Estimated Ton Price: **{est_ton:,.2f} EGP**")
                        m1, m2 = st.columns(2)
                        m1.metric("Pipe Weight", f"{w2} kg/m")
                        m2.metric("Offer Price", f"{offer_price} EGP")
                    else:
                        st.error("⚠️ Error: Pipe weight is 0.")
else:
    st.info("👋 Welcome! Upload 'data.xlsx' to start.")
