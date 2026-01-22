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
# 1. Page Config
# ==========================================
st.set_page_config(
    page_title="HDPE & uPVC Pricing Tool",
    layout="wide",
    page_icon="🔧"
)

st.markdown("""
<style>
    .main-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 8px solid #0077b5;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header {
        font-size: 3.5rem; 
        color: #2c3e50; 
        text-align: left; 
        font-weight: 900; 
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        letter-spacing: -1px;
    }
    .sub-header {
        font-size: 1.5rem; 
        color: #7f8c8d; 
        text-align: left; 
        font-weight: 500;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3.5em;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
<div class="main-container">
    <div class="main-header">HDPE & uPVC Pipe Pricing Tool</div>
    <div class="sub-header">Advanced Estimation System | Developed by Eng. Ahmed Sabra</div>
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
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, alignment=1, spaceAfter=20, textColor=colors.HexColor("#2c3e50"))
    elements.append(Paragraph(f"Pipe Quotation: {material_type}", title_style))
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    elements.append(Paragraph(f"Date: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 20))

    print_df = dataframe.copy()
    data = [print_df.columns.to_list()] + print_df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0077
