import streamlit as st
from config import THEME_COLORS

def apply_custom_css():
    """Apply custom CSS for modern, minimalistic design"""
    st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {{
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom Header */
    .app-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    
    .app-title {{
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    .app-subtitle {{
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-weight: 300;
    }}
    
    /* Sidebar Styling - Professional Dark Theme */
    .css-1d391kg {{
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%) !important;
    }}
    
    .css-1d391kg .css-1v0mbdj {{
        background: transparent !important;
    }}
    
    /* Navigation styling */
    .nav-item {{
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        color: #e2e8f0 !important;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .nav-item:hover {{
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
    }}
    
    .nav-item.active {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    
    .nav-icon {{
        margin-right: 0.75rem;
        font-size: 1.2rem;
    }}
    
    /* Card Styles */
    .custom-card {{
        background: {THEME_COLORS['card']};
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }}
    
    .custom-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }}
    
    .card-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {THEME_COLORS['text']};
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    /* Metric Cards - More Professional */
    .metric-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }}
    
    /* Form Styles */
    .stTextInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }}
    
    .stSelectbox > div > div > select {{
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }}
    
    .stNumberInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: #f7fafc;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        border: 2px solid transparent;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: {THEME_COLORS['card']};
        border-color: #667eea;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: #667eea !important;
        color: white !important;
        border-color: #667eea !important;
    }}
    
    /* Data Editor Styles */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }}
    
    /* File Uploader Styles */
    .stFileUploader {{
        border-radius: 10px;
        border: 2px dashed #667eea;
        background: rgba(102, 126, 234, 0.05);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.1);
    }}
    
    /* Success/Error Messages */
    .stSuccess {{
        background: #48bb78;
        color: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 500;
    }}
    
    .stError {{
        background: #f56565;
        color: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 500;
    }}
    
    /* Animation Classes */
    .fade-in {{
        animation: fadeIn 0.5s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .slide-up {{
        animation: slideUp 0.6s ease-out;
    }}
    
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* User Profile Card in Sidebar */
    .sidebar-profile {{
        text-align: center;
        padding: 1.5rem;
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .profile-avatar {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-size: 1.5rem;
        color: white;
    }}
    
    .profile-name {{
        color: #e2e8f0;
        font-weight: 600;
        margin: 0;
        font-size: 1.1rem;
    }}
    
    .profile-username {{
        color: #a0aec0;
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .app-title {{
            font-size: 2rem;
        }}
        
        .custom-card {{
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        .metric-value {{
            font-size: 2rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle=None):
    """Render modern app header"""
    header_html = f"""
    <div class="app-header fade-in">
        <h1 class="app-title">{title}</h1>
        {f'<p class="app-subtitle">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_metric_card(label, value, icon="💰"):
    """Render modern metric card"""
    metric_html = f"""
    <div class="metric-card slide-up">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <p class="metric-value">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)

def render_card(title, content, icon="📄"):
    """Render custom card with content"""
    card_html = f"""
    <div class="custom-card fade-in">
        <h3 class="card-title">
            <span style="font-size: 1.5rem;">{icon}</span>
            {title}
        </h3>
        <div>{content}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_success_message(message):
    """Create animated success message"""
    success_html = f"""
    <div class="slide-up" style="
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        <span style="font-size: 1.2rem;">✅</span>
        <span style="font-weight: 500;">{message}</span>
    </div>
    """
    st.markdown(success_html, unsafe_allow_html=True)

def create_info_card(title, description, icon="ℹ️"):
    """Create informational card"""
    info_html = f"""
    <div class="custom-card" style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
    ">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <h3 style="margin: 0; color: #667eea;">{title}</h3>
        </div>
        <p style="margin: 0; color: #718096; line-height: 1.6;">{description}</p>
    </div>
    """
    st.markdown(info_html, unsafe_allow_html=True)

def render_sidebar_profile(user_data, username):
    """Render user profile in sidebar"""
    profile_html = f"""
    <div class="sidebar-profile">
        <div class="profile-avatar">
            👤
        </div>
        <h3 class="profile-name">{user_data.get('name', 'User')}</h3>
        <p class="profile-username">@{username}</p>
    </div>
    """
    st.markdown(profile_html, unsafe_allow_html=True)