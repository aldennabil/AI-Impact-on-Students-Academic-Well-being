import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ── Shared colour / scale definitions ──────────────────────────────────────
CUSTOM_RDBU = [[0.0, '#991B1B'], [0.5, '#F8FAFC'], [1.0, '#1E3A8A']]


# ── CSS injected once per page ─────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Remove Streamlit branding / hamburger ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Page background ── */
.stApp { background-color: #F8FAFC; }

/* ── KPI card ── */
.kpi-card {
  background: #FFFFFF;
  padding: 22px 20px;
  border-radius: 14px;
  /* echo: white box + black shadow layers */
  box-shadow:
    0 0 0 1px #E2E8F0,
    2px 4px 0px 1px rgba(0,0,0,0.06),
    4px 8px 0px 2px rgba(0,0,0,0.04),
    6px 12px 0px 3px rgba(0,0,0,0.02);
  border-top: 5px solid #4F46E5;
  text-align: center;
  margin-bottom: 20px;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.kpi-card:hover {
  box-shadow:
    0 0 0 1px #CBD5E1,
    3px 6px 0px 2px rgba(0,0,0,0.09),
    6px 12px 0px 3px rgba(0,0,0,0.06),
    9px 18px 0px 4px rgba(0,0,0,0.03);
  transform: translateY(-2px);
}
.kpi-value  { font-size:28px; font-weight:700; color:#0F172A; margin:6px 0; }
.kpi-label  { font-size:11px; color:#475569; font-weight:600;
              text-transform:uppercase; letter-spacing:0.5px; }
.kpi-subtext{ font-size:11px; color:#64748B; font-style:italic; }

/* ── Chart card — simple border container without shadow effects, space-saving ── */
div[data-testid="stVerticalBlockBorder"] {
  background-color: #FFFFFF !important;
  padding: 12px 14px !important;
  border-radius: 8px !important;
  border: 1px solid #E2E8F0 !important;
  margin-bottom: 16px !important;
  box-shadow: none !important;
}

/* ── Section typography ── */
.section-header {
  color: #0F172A;
  border-left: 5px solid #4F46E5;
  padding-left: 14px;
  padding-top: 4px;
  padding-bottom: 4px;
  margin-left: 8px !important;
  margin-top: 32px;
  margin-bottom: 4px;
  font-weight: 700;
  font-size: 1.25rem;
}
.section-desc {
  margin-left: 8px !important;
  color: #475569;
  font-size: 14px;
  margin-top: 2px;
  margin-bottom: 22px;
}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
  background-color: #FFFFFF;
  border-right: 1px solid #E2E8F0;
}
[data-testid="stSidebar"] .stMarkdown h3 {
  color: #0F172A;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

/* ── Stat badge inside ttest box ── */
.stat-box {
  background:#FFFFFF;
  padding:20px;
  border-radius:14px;
  border:1px solid #E2E8F0;
  box-shadow:
    2px 4px 0px 1px rgba(0,0,0,0.07),
    4px 8px 0px 2px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_clean_data():
    try:
        df = pd.read_csv("ai_student_clean.csv")
        # Compute Delta IPK
        df['Delta_IPK'] = df['Post_Semester_GPA'] - df['Pre_Semester_GPA']
        return df
    except FileNotFoundError:
        st.error(
            "File 'ai_student_clean.csv' tidak ditemukan. "
            "Pastikan file berada di direktori yang sama dengan dashboard.py."
        )
        return None


# ── Plotly premium layout helper ──────────────────────────────────────────
def apply_premium_layout(fig, title_text: str = ""):
    layout_update = dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=11, color="#334155"),
        margin=dict(l=50, r=40, t=15, b=50),
        xaxis=dict(
            gridcolor='#F1F5F9',
            linecolor='#CBD5E1',
            tickfont=dict(color='#334155'),
            title=dict(font=dict(color='#0F172A', size=12)),
        ),
        yaxis=dict(
            gridcolor='#F1F5F9',
            linecolor='#CBD5E1',
            tickfont=dict(color='#334155'),
            title=dict(font=dict(color='#0F172A', size=12)),
        ),
    )
    if title_text:
        layout_update['title'] = {
            'text': title_text,
            'y': 0.95, 'x': 0.5,
            'xanchor': 'center', 'yanchor': 'top',
            'font': {'size': 14, 'color': '#0F172A', 'family': 'Inter', 'weight': 'bold'}
        }
        layout_update['margin']['t'] = 65
    else:
        layout_update['title'] = {'text': ''}
        
    fig.update_layout(**layout_update)



def chart_card(title: str = None):
    container = st.container(border=True)
    if title:
        container.markdown(f"<h4 style='color:#0F172A;font-size:14.5px;font-weight:700;margin-bottom:12px;margin-top:0;'>{title}</h4>", unsafe_allow_html=True)
    return container

