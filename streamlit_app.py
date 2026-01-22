import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 1. Page Config
# ==========================================
st.set_page_config(
    page_title="HDPE & uPVC Pricing Tool",
    layout="wide",
    page_icon="🔧"
)

# --- CSS ذكي يعمل في الوضعين (Light & Dark) ---
st.markdown("""
<style>
    /* 1. الحاوية الرئيسية للهيدر */
    /* بنخلي الخلفية لونها أزرق ثابت، فالكلام جواها لازم يبقى أبيض دائماً */
    .main-container {
        background-color: #0077b5; /* لون البراند الأزرق */
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* العنوان الرئيسي (دائماً أبيض لأنه على خلفية زرقاء) */
    .main-header {
        font-size: 3.5rem; 
        color: #ffffff !important; 
        font-weight: 900; 
        margin-bottom: 0.2rem;
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: -1px;
    }
    
    /* العنوان الفرعي (أبيض شفاف شوية) */
    .sub-header {
        font-size: 1.4rem; 
        color: rgba(255, 255, 255, 0.9) !important; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 2. تكبير وتوضيح أسماء الخانات (Labels) */
    /* هنا السر: بنستخدم var(--text-color) عشان يقلب لوحده حسب وضع الجهاز */
    .stNumberInput label p, 
    .stTextInput label p, 
    .stSelectbox label p, 
    .stRadio label p {
        font-size: 1.3rem !important; /* خط كبير */
        font-weight: 800 !important;  /* خط عريض */
        color: var(--text-color) !important; /* ذكي: يسود في الفاتح ويبيض في الغامق */
    }

    /* 3. تكبير خيارات الراديو (HDPE / uPVC) */
    .stRadio div[role='radiogroup'] label div p {
        font-size: 1.4rem !important;
        font-weight: bold !important;
        color: var(--text-color) !important;
    }

    /* 4. الكلام اللي بيتكتب جوه الخانات */
    .stNumberInput input, .stTextInput input {
        font-size: 1.2rem !important;
        font-weight: bold;
        color: var(--text-color) !important;
    }

    /* 5. الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3.5em;
        font-size: 1.2rem;
        background-color: #0077b5; /* أزرق */
        color: white; /* كتابة بيضاء */
        border: none;
    }
    .stButton>button:hover {
        background-color: #005f91; /* أغمق سنة لما تقف عليه */
    }

    /* 6. تكبير التبويبات */
    button[data-baseweb="tab"] > div {
        font-size: 1.3rem !important;
        font-weight: bold !important;
    }
</style>

<div class="main-container">
    <div class="main-header">HDPE & uPVC Pipe Pricing Tool</div>
    <div class="sub-header">CREATED BY Eng. Ahmed Sabra</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State
# ==========================================
if 'quote_list' not in st.session_state:
    st.session_state.quote_list = []

# ==========================================
# 3. Sidebar
# ==========================================
st.sidebar.header("⚙️ Settings")

material_type = st.sidebar.radio(
    "Select Material:",
    ("HDPE", "uPVC"),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("**Eng. Ahmed Sabra**\n\n📞 +201148777463")

# ==========================================
# 4. Helper Functions
# ==========================================
data_file = 'data.xlsx'

@st.cache_data
def load_data(file_path, sheet_name):
    try:
        xl = pd.ExcelFile(file_path)
        sheet_map = {name.upper(): name for name in xl.sheet_names}
        target_sheet = sheet_map.get(sheet_name.upper())
        
        if target_sheet:
            df = pd.read_excel(file_path, sheet_name=target_sheet)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
                    df[col] = df[col].replace('NAN', '-')
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
            return df, None
        else:
            return None, xl.sheet_names
    except Exception as e:
        return None, str(e)

def create_pdf(dataframe):
    buffer = io.BytesIO()
    # Landscape A4
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=24, alignment=1, spaceAfter=20, textColor=colors.HexColor("#2c3e50"))
    elements.append(Paragraph(f"Pipe Quotation: {material_type}", title_style))
    
    # Date
    date_str = datetime.now().strftime("%Y-%m-%d")
    elements.append(Paragraph(f"Date: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Table
    print_df = dataframe.copy()
    data = [print_df.columns.to_list()] + print_df.values.tolist()
    table = Table(data, repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0077b5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(name='Footer', parent=styles['Normal'], alignment=1, fontSize=10)
    footer_text = "<b>CREATED BY Eng. Ahmed Sabra | Contact: +201148777463</b>"
    elements.append(Paragraph(footer_text, footer_style))

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

if df is None:
    if error_msg and isinstance(error_msg, list):
        st.error(f"❌ Could not find sheet '{material_type}'. Found: {error_msg}")
    else:
        st.warning("⚠️ Database file 'data.xlsx' not found.")
    
    uploaded = st.sidebar.file_uploader("Upload Excel Manually", type=["xlsx"])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name=material_type)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
            df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
            df.fillna("-", inplace=True)
        except: pass

if df is not None:
    if material_type == "HDPE":
        allowed_cols = ['PN', 'SDR']
        spec_cols = [c for c in df.columns if c in allowed_cols]
    else:
        base_cols = ['Diameter', 'Weight']
        spec_cols = [c for c in df.columns if c not in base_cols]

    tab1, tab2 = st.tabs([f"💰 {material_type} Pricing", "🕵️ Reverse Analysis"])

    # --- TAB 1: Forward Pricing ---
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            ton_price = st.number_input(f"Ton Price (EGP):", min_value=0.0, step=500.0)
            dia_unit = st.radio("Unit:", ["mm", "Inch"], horizontal=True)
        with c2:
            dia_input_str = st.text_input("Diameters (e.g. 110, 200):")

        user_specs = {}
        if spec_cols:
            st.markdown("#### Specifications")
            cols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with cols[idx]:
                    vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    vals.insert(0, "-")
                    user_specs[col] = st.selectbox(f"{col}", vals, key=f"t1_{col}")

        if st.button("Calculate Batch 🚀", type="primary"):
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
                    else: st.warning("No matches found.")
                except: st.error("Invalid input.")

        if 'current_batch' in st.session_state and st.session_state.current_batch:
            st.dataframe(pd.DataFrame(st.session_state.current_batch), use_container_width=True)
            
            c_add, c_clr = st.columns([1, 4])
            with c_add:
                if st.button("Add to List"):
                    st.session_state.quote_list.extend(st.session_state.current_batch)
                    full = pd.DataFrame(st.session_state.quote_list)
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

    # --- TAB 2: Reverse Analysis ---
    with tab2:
        st.markdown("#### Reverse Analysis (Find Ton Price)")
        st.caption("Tip: You don't have to fill all fields. Just select what you know.")
        
        c1, c2 = st.columns(2)
        op = c1.number_input("Offer Price (EGP/m):", min_value=0.0)
        rd = c2.selectbox("Diameter:", sorted(df['Diameter'].unique().tolist()), key="rev")
        
        rev_specs = {}
        if spec_cols:
            cols = st.columns(len(spec_cols))
            for idx, col in enumerate(spec_cols):
                with cols[idx]:
                    vals = [x for x in sorted(df[col].unique().tolist(), key=str) if x != "-"]
                    vals.insert(0, "-")
                    rev_specs[col] = st.selectbox(f"{col}", vals, key=f"t2_{col}")

        if st.button("Analyze Offer 🔍", type="primary"):
            if op > 0:
                mask = (df['Diameter'] == rd)
                for k, v in rev_specs.items():
                    if v != "-": mask &= (df[k] == v)
                
                row = df[mask]
                
                if row.empty:
                    st.warning("❌ No pipes found with these criteria.")
                else:
                    unique_weights = [w for w in row['Weight'].unique() if w > 0]
                    if len(unique_weights) == 0:
                        st.error("⚠️ Found pipes but weights are 0.")
                    elif len(unique_weights) == 1:
                        w = unique_weights[0]
                        est_ton = (op / w) * 1000
                        st.success(f"🏭 Estimated Ton Price: **{est_ton:,.2f} EGP**")
                        st.markdown(f"**Based on:** Weight {w} kg/m")
                    else:
                        st.info(f"💡 Found {len(row)} possible pipes:")
                        results_table = row.copy()
                        results_table['Calculated Ton Price'] = (op / results_table['Weight']) * 1000
                        display_cols = ['Diameter', 'Weight', 'Calculated Ton Price'] + [c for c in spec_cols if c in results_table.columns]
                        st.dataframe(results_table[display_cols].style.format({'Calculated Ton Price': '{:,.2f}', 'Weight': '{:.3f}'}))
            else:
                st.warning("Please enter a price.")
else:
    st.info("Loading...")
