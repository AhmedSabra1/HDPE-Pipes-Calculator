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
# 1. Page Config (Simple & Clean)
# ==========================================
st.set_page_config(
    page_title="HDPE & uPVC Pricing Tool",
    layout="wide",
    page_icon="🔧" 
)

# تصميم هادي وبسيط جداً بدون أيقونات ونش
st.markdown("""
<style>
    .main-container {
        padding: 1.5rem;
        border-bottom: 2px solid #eee;
        margin-bottom: 2rem;
    }
    .main-header {
        font-size: 2.5rem; 
        color: #333; 
        text-align: left; 
        font-weight: bold; 
        margin-bottom: 0.5rem;
        font-family: sans-serif;
    }
    .sub-header {
        font-size: 1.1rem; 
        color: #666; 
        text-align: left;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        height: 3em;
    }
</style>
<div class="main-container">
    <div class="main-header">HDPE & uPVC Pipe Pricing Tool</div>
    <div class="sub-header">Developed by Eng. Ahmed Sabra</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State
# ==========================================
if 'quote_list' not in st.session_state:
    st.session_state.quote_list = []

# ==========================================
# 3. Sidebar (Control)
# ==========================================
st.sidebar.header("Settings")

# اختيار الخامة
material_type = st.sidebar.radio(
    "Select Material:",
    ("HDPE", "uPVC"), # التأكد من تطابق الأسماء
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Contact Info")
st.sidebar.info("**Eng. Ahmed Sabra**\n\n📞 +201148777463")

# ==========================================
# 4. Helper Functions
# ==========================================
data_file = 'data.xlsx'

@st.cache_data
def load_data(file_path, sheet_name):
    try:
        xl = pd.ExcelFile(file_path)
        # البحث عن الشيت بغض النظر عن حالة الحروف (كابتل أو سمول)
        sheet_map = {name.upper(): name for name in xl.sheet_names}
        target_sheet = sheet_map.get(sheet_name.upper())
        
        if target_sheet:
            df = pd.read_excel(file_path, sheet_name=target_sheet)
            # تنظيف الداتا
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
                    df[col] = df[col].replace('NAN', '-')
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
            return df, None
        else:
            # لو الشيت مش موجود، نرجع أسماء الشيتات الموجودة عشان نعرف الغلط فين
            return None, xl.sheet_names
    except Exception as e:
        return None, str(e)

def create_pdf(dataframe):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=18, alignment=1, spaceAfter=15, textColor=colors.black)
    elements.append(Paragraph(f"Pipe Quotation: {material_type}", title_style))
    
    # Date
    date_str = datetime.now().strftime("%Y-%m-%d")
    elements.append(Paragraph(f"Date: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Table
    print_df = dataframe.copy()
    data = [print_df.columns.to_list()] + print_df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    
    # Simple Footer
    elements.append(Spacer(1, 40))
    footer_text = "<b>Tool by Eng. Ahmed Sabra | Contact: +201148777463</b>"
    elements.append(Paragraph(footer_text, styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# 5. Main Logic
# ==========================================
df = None
error_msg = None

if os.path.exists(data_file):
    df, error_msg = load_data(data_file, material_type)

# لو ملقاش الملف أو الشيت
if df is None:
    if error_msg and isinstance(error_msg, list):
        st.error(f"❌ Could not find sheet '{material_type}'. Found sheets: {error_msg}")
        st.info("💡 Please rename your Excel sheet to match 'HDPE' or 'uPVC'.")
    else:
        st.warning("⚠️ Database file 'data.xlsx' not found.")
    
    # خيار الرفع اليدوي
    uploaded = st.sidebar.file_uploader("Upload Excel Manually", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name=material_type)
            # تنظيف سريع
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
        except:
            st.error(f"Failed to load '{material_type}' from uploaded file.")

if df is not None:
    # تحديد الأعمدة حسب الخامة
    if material_type == "HDPE":
        allowed_cols = ['PN', 'SDR']
        spec_cols = [c for c in df.columns if c in allowed_cols]
    else:
        # للـ uPVC: استبعاد القطر والوزن فقط، وعرض الباقي
        base_cols = ['Diameter', 'Weight']
        spec_cols = [c for c in df.columns if c not in base_cols]

    tab1, tab2 = st.tabs([f"💰 {material_type} Pricing", "🕵️ Reverse Analysis"])

    # --- TAB 1: Calculator ---
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            ton_price = st.number_input(f"Ton Price (EGP):", min_value=0.0, step=500.0)
            dia_unit = st.radio("Unit:", ["mm", "Inch"], horizontal=True)
        with c2:
            dia_input_str = st.text_input("Diameters (e.g. 110, 200):")

        # Specs Filters
        user_specs = {}
        if spec_cols:
            st.markdown("#### Specifications")
            cols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with cols[idx]:
                    vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    vals.insert(0, "-")
                    user_specs[col] = st.selectbox(f"{col}", vals, key=f"t1_{col}")

        if st.button("Calculate 🚀", type="primary"):
            if ton_price > 0 and dia_input_str:
                try:
                    raw_dias = dia_input_str.replace(" ", ",").split(",")
                    target_dias = [float(x) for x in raw_dias if x.strip() != ""]
                    
                    batch_results = []
                    all_dias_db = sorted(df['Diameter'].unique().tolist())

                    for d_in in target_dias:
                        target_mm = d_in * 25.4 if dia_unit == "Inch" else d_in
                        # أقرب قطر
                        actual_dia = all_dias_db[(np.abs(np.asarray(all_dias_db) - target_mm)).argmin()]
                        
                        mask = (df['Diameter'] == actual_dia)
                        for k, v in user_specs.items():
                            if v != "-": mask &= (df[k] == v)
                        
                        row = df[mask]
                        if not row.empty:
                            w = row.iloc[0]['Weight']
                            if w > 0:
                                p = (ton_price / 1000) * w
                                item = {"Material": material_type, "Diameter": actual_dia, "Weight": w, "Price": round(p, 2)}
                                for col in spec_cols: item[col] = row.iloc[0][col]
                                batch_results.append(item)
                    
                    if batch_results:
                        st.session_state.current_batch = batch_results
                    else:
                        st.warning("No matches found.")
                except:
                    st.error("Invalid input numbers.")

        # Preview & Add
        if 'current_batch' in st.session_state and st.session_state.current_batch:
            st.dataframe(pd.DataFrame(st.session_state.current_batch), use_container_width=True)
            
            c_add, c_clr = st.columns([1, 4])
            with c_add:
                if st.button("Add to List"):
                    st.session_state.quote_list.extend(st.session_state.current_batch)
                    full = pd.DataFrame(st.session_state.quote_list)
                    # Sorting
                    keys = ['Material', 'Diameter'] + [c for c in spec_cols if c in full.columns]
                    valid_keys = [k for k in keys if k in full.columns]
                    full = full.sort_values(by=valid_keys, ascending=True)
                    st.session_state.quote_list = full.to_dict('records')
                    del st.session_state.current_batch
                    st.rerun()
            with c_clr:
                if st.button("Clear Preview"):
                    del st.session_state.current_batch
                    st.rerun()

        # Final List
        st.markdown("---")
        if len(st.session_state.quote_list) > 0:
            st.markdown("### Final Quotation")
            final_df = pd.DataFrame(st.session_state.quote_list)
            st.dataframe(final_df, use_container_width=True)
            
            cp, cc = st.columns(2)
            with cp:
                pdf = create_pdf(final_df)
                st.download_button("Download PDF", pdf, "Quotation.pdf", "application/pdf", type="primary")
            with cc:
                if st.button("Clear All"):
                    st.session_state.quote_list = []
                    st.rerun()

    # --- TAB 2: Reverse ---
    with tab2:
        st.markdown("#### Reverse Analysis")
        c1, c2 = st.columns(2)
        op = c1.number_input("Offer Price/m:", min_value=0.0)
        rd = c2.selectbox("Diameter:", sorted(df['Diameter'].unique().tolist()), key="rev")
        
        rev_specs = {}
        if spec_cols:
            cols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with cols[idx]:
                    vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    rev_specs[col] = st.selectbox(f"{col}", vals, key=f"t2_{col}")

        if st.button("Analyze"):
            mask = (df['Diameter'] == rd)
            for k, v in rev_specs.items(): mask &= (df[k] == v)
            row = df[mask]
            if not row.empty:
                w = row.iloc[0]['Weight']
                if w > 0:
                    st.success(f"Estimated Ton Price: **{(op/w)*1000:,.2f} EGP**")
                else:
                    st.error("Weight is 0.")
            else:
                st.warning("Pipe not found.")
else:
    st.info("Loading data...")
