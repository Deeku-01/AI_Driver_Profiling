import streamlit as st

def apply_custom_style():
    """Apply custom styling to the Streamlit app"""
    st.markdown("""
        <style>
        /* Header bar */
        .header-bar {
            background-color: #1E3D59;
            padding: 1rem 2rem;
            margin: -1rem -1rem 1rem -1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-bar h1 {
            color: white !important;
            font-size: 1.8rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .header-bar p {
            color: #e9ecef;
            font-size: 1rem;
            margin: 0.25rem 0 0 0;
            opacity: 0.9;
        }
        
        /* Header bar */
        div[data-testid="stToolbar"] {
            display: none;
        }
        
        header[data-testid="stHeader"] {
            display: none;
        }
        
        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
        }
        
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
        }
        
        .header-title {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: white;
        }
        
        .header-title h1 {
            color: white !important;
            font-size: 1.5rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .header-subtitle {
            color: #e9ecef;
            font-size: 0.9rem;
            margin-left: 1rem;
        }
        
        /* Adjust main content to account for fixed header */
        .main .block-container {
            padding-top: 80px;
        }
        
        /* Main container */
        .main {
            padding: 1rem;
        }
        
        /* Headers */
        .stMarkdown h1 {
            color: #1E3D59;
            font-size: 2rem !important;
            margin-bottom: 0.5rem !important;
            padding: 0 !important;
        }
        
        .stMarkdown p {
            color: #6c757d;
            font-size: 1rem;
            margin: 0 0 1.5rem 0;
        }
        
        /* Header container */
        .header-container {
            padding: 0.5rem 0;
            margin-bottom: 1rem;
            border-bottom: 2px solid #f0f2f6;
        }
        
        /* Override Streamlit's default header styles */
        .header-container h1 {
            color: #1E3D59;
            font-size: 2rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .header-container p {
            color: #6c757d;
            font-size: 1rem;
            margin: 0.25rem 0 0 0;
        }
        
        /* Override Streamlit's default header styles */
        h1 {
            color: #1E3D59;
            font-size: 2rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        h2, h3 {
            color: #1E3D59;
            font-size: 1.5rem !important;
            margin: 1rem 0 !important;
            padding: 0 !important;
        }
        
        /* Cards */
        .css-1r6slb0 {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Metrics */
        .css-1r6slb0.e16nr0p34 {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #17A2B8;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background-color: #138496;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Navigation */
        .css-1d391kg {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
        }
        
        /* Input fields */
        .stTextInput input {
            border-radius: 5px;
            border: 1px solid #ced4da;
            padding: 0.5rem;
        }
        
        .stTextInput input:focus {
            border-color: #17A2B8;
            box-shadow: 0 0 0 0.2rem rgba(23, 162, 184, 0.25);
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 4rem;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #1E3D59;
            font-size: 1rem;
            font-weight: 400;
            border: none;
            padding: 1rem;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(23, 162, 184, 0.1);
            border-bottom: 2px solid #17A2B8;
        }
        
        /* Cards for dashboard */
        .dashboard-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active {
            background-color: #28a745;
        }
        
        .status-inactive {
            background-color: #dc3545;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #17A2B8;
            margin-bottom: 1rem;
            width: 100%;
            box-sizing: border-box;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .metric-value {
            color: #1E3D59;
            font-size: 1.2rem;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Column layout fixes */
        .element-container {
            width: 100%;
        }
        
        .row-widget.stButton {
            width: 100%;
        }
        
        /* Progress bars */
        .stProgress > div > div {
            background-color: #17A2B8;
        }
        
        /* Plotly chart containers */
        .js-plotly-plot {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def card(title, content):
    """Create a styled card with title and content"""
    return st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #1E3D59; margin-bottom: 1rem;">{title}</h3>
            <div class="card-content">{content}</div>
        </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None):
    """Create a styled metric card"""
    delta_html = f'<div style="color: {"#28a745" if delta >= 0 else "#dc3545"}">{"↑" if delta >= 0 else "↓"} {abs(delta)}%</div>' if delta is not None else ''
    return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """ 