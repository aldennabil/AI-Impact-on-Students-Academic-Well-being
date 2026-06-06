import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import inject_css, load_clean_data, apply_premium_layout, chart_card, CUSTOM_RDBU

inject_css()

df = load_clean_data()
if df is None:
    st.stop()

# ── Page header ─────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;color:#0F172A;margin-top:6px;font-weight:800;'>"
    "Ringkasan Umum Responden</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:15px;'>"
    "Profil demografis, perilaku belajar, dan distribusi variabel utama </p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Global KPI row ───────────────────────────────────────────────────────────
avg_gpa_all       = df['Post_Semester_GPA'].mean()
avg_retention_all = df['Skill_Retention_Score'].mean()
high_burnout_all  = (df['Burnout_Risk_Level'] == 'High').mean() * 100
n_total           = len(df)
avg_ai_hours      = df['Weekly_GenAI_Hours'].mean()

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "IPK Akhir Rata-rata",       f"{avg_gpa_all:.2f} / 4.00",   "Seluruh dataset",                "#312E81"),
    (k2, "Retensi Ilmu Rata-rata",    f"{avg_retention_all:.1f}%",   "Pasca-semester",                  "#0F766E"),
    (k3, "Risiko Burnout Tinggi",     f"{high_burnout_all:.1f}%",    "Mahasiswa kategori High",          "#991B1B"),
    (k4, "Total Responden",           f"{n_total:,}",                 "Data bersih tervalidasi",          "#1E3A8A"),
    (k5, "Jam AI per Minggu (Rata)",  f"{avg_ai_hours:.1f} jam",     "Rata-rata penggunaan mingguan",    "#581C87"),
]
for col, label, val, sub, color in kpis:
    with col:
        st.markdown(
            f"""<div class="kpi-card" style="border-top-color:{color};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-subtext">{sub}</div>
            </div>""",
            unsafe_allow_html=True,
        )

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Distribusi Kategorik & Boolean",
    "Distribusi Variabel Numerik",
    "Matriks Korelasi Multivariat",
    "Asosiasi Kategorik",
])

# ────────────────────────────── TAB 1 ────────────────────────────────────────
with tab1:
    st.markdown(
        "<p class='section-desc' style='margin-left:4px;'>"
        "Distribusi seluruh variabel kategorik dan Boolean untuk memahami profil responden secara menyeluruh.</p>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)

    # --- LEFT column ---
    charts_left = [
        ("Major_Category",         "Bidang Studi",          "Distribusi Mahasiswa per Bidang Studi",          "#4F46E5"),
        ("Institutional_Policy",   "Kebijakan Institusi",   "Distribusi Kebijakan Institusi terhadap AI",     "#0EA5E9"),
        ("Primary_Use_Case",       "Use Case Utama",        "Tujuan Utama Penggunaan AI Generatif",           "#0D9488"),
        ("Prompt_Engineering_Skill","Kemampuan Prompt",     "Distribusi Kemampuan Prompt Engineering",        "#7C3AED"),
    ]
    with c1:
        for col_name, label, title, color in charts_left:
            with chart_card(title):
                counts = df[col_name].value_counts().reset_index()
                counts.columns = [label, "Jumlah"]
                fig = px.bar(counts, x=label, y="Jumlah", color_discrete_sequence=[color])
                apply_premium_layout(fig, "")
                st.plotly_chart(fig, use_container_width=True)

        # Paid Subscription (Boolean)
        with chart_card("Proporsi Akun AI Berbayar vs Gratis"):
            sub_counts = df['Paid_Subscription'].map({True: 'Berbayar', False: 'Gratis'}).value_counts().reset_index()
            sub_counts.columns = ['Status Berlangganan', 'Jumlah']
            fig_sub = px.bar(sub_counts, x='Status Berlangganan', y='Jumlah', color_discrete_sequence=['#10B981'])
            apply_premium_layout(fig_sub, "")
            st.plotly_chart(fig_sub, use_container_width=True)

    # --- RIGHT column ---
    charts_right = [
        ("Year_of_Study",    "Jenjang Studi",   "Distribusi Mahasiswa per Jenjang Studi",     "#4F46E5"),
        ("Burnout_Risk_Level","Tingkat Burnout", "Distribusi Tingkat Risiko Burnout",          "#EF4444"),
        ("AI_Usage_Segment", "Segmen Pengguna", "Distribusi Segmen Penggunaan AI",             "#10B981"),
    ]
    with c2:
        for col_name, label, title, color in charts_right:
            with chart_card(title):
                counts = df[col_name].value_counts().reset_index()
                counts.columns = [label, "Jumlah"]
                fig = px.bar(counts, x=label, y="Jumlah", color_discrete_sequence=[color])
                apply_premium_layout(fig, "")
                st.plotly_chart(fig, use_container_width=True)

        # Donut: Burnout risk breakdown
        with chart_card("Komposisi Risiko Burnout (Pie)"):
            burnout_pie = df['Burnout_Risk_Level'].value_counts().reset_index()
            burnout_pie.columns = ['Risiko', 'Jumlah']
            fig_pie = px.pie(
                burnout_pie, names='Risiko', values='Jumlah',
                color='Risiko',
                color_discrete_map={'Low': '#10B981', 'Medium': '#F59E0B', 'High': '#EF4444'},
                hole=0.45,
            )
            apply_premium_layout(fig_pie, "")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Donut: AI Usage segment
        with chart_card("Komposisi Segmen Pengguna AI (Pie)"):
            usage_pie = df['AI_Usage_Segment'].value_counts().reset_index()
            usage_pie.columns = ['Segmen', 'Jumlah']
            fig_usage_pie = px.pie(
                usage_pie, names='Segmen', values='Jumlah',
                color='Segmen',
                color_discrete_map={'Light User': '#0EA5E9', 'Moderate User': '#0D9488', 'Heavy User': '#7C3AED'},
                hole=0.45,
            )
            apply_premium_layout(fig_usage_pie, "")
            fig_usage_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_usage_pie, use_container_width=True)


# ────────────────────────────── TAB 2 ────────────────────────────────────────
with tab2:
    st.markdown(
        "<p class='section-desc' style='margin-left:4px;'>"
        "Sebaran (distribusi) seluruh variabel numerik dalam dataset untuk memahami karakteristik data.</p>",
        unsafe_allow_html=True,
    )
    n1, n2 = st.columns(2)

    num_charts_left = [
        ('Pre_Semester_GPA',           "IPK Awal",                                    '#4F46E5', 30),
        ('Post_Semester_GPA',          "IPK Akhir",                                   '#4F46E5', 30),
        ('Delta_IPK',                  "Perbedaan IPK (IPK Akhir - IPK Awal)",        '#8B5CF6', 30),
        ('Weekly_GenAI_Hours',         "Jam Penggunaan AI per Minggu",                '#0EA5E9', 30),
        ('Tool_Diversity',             "Keragaman Alat AI (Jumlah Tools)",            '#0D9488', 10),
    ]
    num_charts_right = [
        ('Traditional_Study_Hours',    "Waktu Belajar Mandiri (Jam/Minggu)",          '#0D9488', 30),
        ('Perceived_AI_Dependency',    "Tingkat Ketergantungan AI (Skor 1–10)",       '#7C3AED', 10),
        ('Anxiety_Level_During_Exams', "Tingkat Kecemasan saat Ujian (Skor 1–10)",   '#EF4444', 10),
        ('Skill_Retention_Score',      "Skor Retensi Pengetahuan",                    '#10B981', 30),
    ]

    with n1:
        for col_name, label, color, bins in num_charts_left:
            with chart_card(f"Sebaran {label}"):
                fig = px.histogram(df, x=col_name, nbins=bins, color_discrete_sequence=[color])
                apply_premium_layout(fig, "")
                fig.update_layout(xaxis_title=label, yaxis_title="Frekuensi")
                st.plotly_chart(fig, use_container_width=True)

    with n2:
        for col_name, label, color, bins in num_charts_right:
            with chart_card(f"Sebaran {label}"):
                fig = px.histogram(df, x=col_name, nbins=bins, color_discrete_sequence=[color])
                apply_premium_layout(fig, "")
                fig.update_layout(xaxis_title=label, yaxis_title="Frekuensi")
                st.plotly_chart(fig, use_container_width=True)


# ────────────────────────────── TAB 3 ────────────────────────────────────────
with tab3:
    st.markdown(
        "<p class='section-desc' style='margin-left:4px;'>"
        "Korelasi Pearson antar seluruh variabel numerik — menjawab BQ-1 hingga BQ-7 secara simultan.</p>",
        unsafe_allow_html=True,
    )
    df_corr = df[[
        'Post_Semester_GPA', 'Pre_Semester_GPA', 'Delta_IPK', 'Traditional_Study_Hours',
        'Weekly_GenAI_Hours', 'Perceived_AI_Dependency', 'Tool_Diversity',
        'Anxiety_Level_During_Exams', 'Skill_Retention_Score'
    ]].dropna()
    corr_all = df_corr.corr()
    label_map = {
        'Post_Semester_GPA': 'IPK Akhir', 'Pre_Semester_GPA': 'IPK Awal',
        'Delta_IPK': 'Perbedaan IPK',
        'Traditional_Study_Hours': 'Belajar Mandiri', 'Weekly_GenAI_Hours': 'Jam AI/Minggu',
        'Perceived_AI_Dependency': 'Ketergantungan AI', 'Tool_Diversity': 'Ragam Tools AI',
        'Anxiety_Level_During_Exams': 'Kecemasan Ujian', 'Skill_Retention_Score': 'Retensi Ilmu',
    }
    corr_all.index   = [label_map.get(c, c) for c in corr_all.index]
    corr_all.columns = [label_map.get(c, c) for c in corr_all.columns]

    with chart_card("Matriks Korelasi Variabel Numerik (Global)"):
        fig_heat = go.Figure(data=go.Heatmap(
            z=corr_all.values, x=corr_all.columns.tolist(), y=corr_all.index.tolist(),
            colorscale=CUSTOM_RDBU, zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in corr_all.values],
            texttemplate="%{text}",
            textfont={"size": 10, "family": "Inter", "color": "#0F172A"},
            hoverongaps=False,
        ))
        apply_premium_layout(fig_heat, "")
        fig_heat.update_layout(height=520, xaxis=dict(tickangle=-35))
        st.plotly_chart(fig_heat, use_container_width=True)

    # Correlation bar: target = IPK Akhir
    with chart_card("Peringkat Korelasi terhadap IPK Akhir (Global)"):
        corr_target = corr_all['IPK Akhir'].drop(['IPK Akhir', 'Perbedaan IPK'], errors='ignore').sort_values()
        colors_bar  = ['#EF4444' if v < 0 else '#4F46E5' for v in corr_target.values]
        fig_cbar = go.Figure(go.Bar(
            x=corr_target.values, y=corr_target.index,
            orientation='h', marker_color=colors_bar,
            text=[f"{v:.3f}" for v in corr_target.values], textposition='outside',
        ))
        apply_premium_layout(fig_cbar, "")
        fig_cbar.update_layout(xaxis_title="Koefisien Korelasi Pearson", yaxis_title="", height=360)
        fig_cbar.add_vline(x=0, line_color='#0F172A', line_width=1)
        st.plotly_chart(fig_cbar, use_container_width=True)


# ────────────────────────────── TAB 4 ────────────────────────────────────────
with tab4:
    st.markdown(
        "<p class='section-desc' style='margin-left:4px;'>"
        "Hubungan antar variabel kategorik menggunakan stacked bar berproporsi (100%).</p>",
        unsafe_allow_html=True,
    )
    a1, a2 = st.columns(2)

    with a1:
        # 1. Major ↔ Burnout
        with chart_card("Risiko Burnout per Bidang Studi"):
            df_mb = pd.crosstab(df['Major_Category'], df['Burnout_Risk_Level'], normalize='index').reset_index()
            df_mb = df_mb.melt(id_vars='Major_Category', value_vars=['Low', 'Medium', 'High'],
                               var_name='Risiko Burnout', value_name='Proporsi')
            df_mb['Persentase (%)'] = df_mb['Proporsi'] * 100
            fig_mb = px.bar(df_mb, x='Major_Category', y='Persentase (%)', color='Risiko Burnout',
                            labels={'Major_Category': 'Bidang Studi'},
                            color_discrete_map={'Low':'#10B981','Medium':'#F59E0B','High':'#EF4444'},
                            category_orders={'Risiko Burnout': ['Low','Medium','High']})
            apply_premium_layout(fig_mb, "")
            st.plotly_chart(fig_mb, use_container_width=True)

        # 2. Prompt Skill ↔ Paid Subscription
        with chart_card("Kepemilikan Akun Berbayar per Kemampuan Prompt"):
            df_pp = pd.crosstab(df['Prompt_Engineering_Skill'], df['Paid_Subscription'], normalize='index').reset_index()
            df_pp = df_pp.melt(id_vars='Prompt_Engineering_Skill', value_vars=[True, False],
                               var_name='Paid_Subscription', value_name='Proporsi')
            df_pp['Akses'] = df_pp['Paid_Subscription'].map({True: 'Berbayar', False: 'Gratis'})
            df_pp['Persentase (%)'] = df_pp['Proporsi'] * 100
            fig_pp = px.bar(df_pp, x='Prompt_Engineering_Skill', y='Persentase (%)', color='Akses',
                            labels={'Prompt_Engineering_Skill': 'Kemampuan Prompt'},
                            color_discrete_map={'Berbayar':'#4F46E5','Gratis':'#94A3B8'},
                            category_orders={'Prompt_Engineering_Skill': ['Beginner','Intermediate','Advanced']})
            apply_premium_layout(fig_pp, "")
            st.plotly_chart(fig_pp, use_container_width=True)

        # 3. Year of Study ↔ AI Usage Segment
        with chart_card("Segmen Penggunaan AI per Jenjang Studi"):
            study_order = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
            df_ys = pd.crosstab(df['Year_of_Study'], df['AI_Usage_Segment'], normalize='index').reset_index()
            df_ys = df_ys.melt(id_vars='Year_of_Study',
                               value_vars=[c for c in ['Light User','Moderate User','Heavy User'] if c in df['AI_Usage_Segment'].unique()],
                               var_name='Segmen', value_name='Proporsi')
            df_ys['Persentase (%)'] = df_ys['Proporsi'] * 100
            fig_ys = px.bar(df_ys, x='Year_of_Study', y='Persentase (%)', color='Segmen',
                            labels={'Year_of_Study': 'Jenjang Studi'},
                            color_discrete_map={'Light User':'#0EA5E9','Moderate User':'#0D9488','Heavy User':'#7C3AED'},
                            category_orders={'Year_of_Study': study_order,
                                             'Segmen': ['Light User','Moderate User','Heavy User']})
            apply_premium_layout(fig_ys, "")
            st.plotly_chart(fig_ys, use_container_width=True)

    with a2:
        # 4. AI Usage Segment ↔ Burnout
        with chart_card("Risiko Burnout per Segmen Penggunaan AI"):
            df_sb = pd.crosstab(df['AI_Usage_Segment'], df['Burnout_Risk_Level'], normalize='index').reset_index()
            df_sb = df_sb.melt(id_vars='AI_Usage_Segment', value_vars=['Low','Medium','High'],
                               var_name='Risiko Burnout', value_name='Proporsi')
            df_sb['Persentase (%)'] = df_sb['Proporsi'] * 100
            fig_sb = px.bar(df_sb, x='AI_Usage_Segment', y='Persentase (%)', color='Risiko Burnout',
                            labels={'AI_Usage_Segment': 'Segmen Pengguna AI'},
                            color_discrete_map={'Low':'#10B981','Medium':'#F59E0B','High':'#EF4444'},
                            category_orders={'AI_Usage_Segment':['Light User','Moderate User','Heavy User'],
                                             'Risiko Burnout':['Low','Medium','High']})
            apply_premium_layout(fig_sb, "")
            st.plotly_chart(fig_sb, use_container_width=True)

        # 5. Major ↔ Primary Use Case
        with chart_card("Distribusi Use Case AI per Bidang Studi"):
            df_mu = pd.crosstab(df['Major_Category'], df['Primary_Use_Case'], normalize='index').reset_index()
            df_mu = df_mu.melt(id_vars='Major_Category', var_name='Use Case', value_name='Proporsi')
            df_mu['Persentase (%)'] = df_mu['Proporsi'] * 100
            fig_mu = px.bar(df_mu, x='Major_Category', y='Persentase (%)', color='Use Case',
                            labels={'Major_Category': 'Bidang Studi'},
                            color_discrete_sequence=['#4F46E5','#0EA5E9','#0D9488','#7C3AED','#F59E0B'])
            apply_premium_layout(fig_mu, "")
            st.plotly_chart(fig_mu, use_container_width=True)

        # 6. Institutional Policy ↔ AI Usage Segment
        with chart_card("Segmen Penggunaan AI per Kebijakan Institusi"):
            df_pi = pd.crosstab(df['Institutional_Policy'], df['AI_Usage_Segment'], normalize='index').reset_index()
            df_pi = df_pi.melt(id_vars='Institutional_Policy',
                               value_vars=[c for c in ['Light User','Moderate User','Heavy User'] if c in df['AI_Usage_Segment'].unique()],
                               var_name='Segmen', value_name='Proporsi')
            df_pi['Persentase (%)'] = df_pi['Proporsi'] * 100
            fig_pi = px.bar(df_pi, x='Institutional_Policy', y='Persentase (%)', color='Segmen',
                            labels={'Institutional_Policy': 'Kebijakan Institusi'},
                            color_discrete_map={'Light User':'#0EA5E9','Moderate User':'#0D9488','Heavy User':'#7C3AED'},
                            category_orders={'Segmen':['Light User','Moderate User','Heavy User']})
            apply_premium_layout(fig_pi, "")
            st.plotly_chart(fig_pi, use_container_width=True)

