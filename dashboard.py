import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
  page_title="Dashboard Analisis Perilaku Belajar & Kesejahteraan Mahasiswa",
  page_icon="",
  layout="wide",
  initial_sidebar_state="collapsed"
)

st.markdown("""
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }
  
  .stApp {
    background-color: #F8FAFC;
  }
  
  .kpi-card {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    border: 1px solid #E2E8F0;
    border-top: 5px solid #4F46E5;
    text-align: center;
    margin-bottom: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
  }
  
  .kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #0F172A;
    margin: 5px 0;
  }
  
  .kpi-label {
    font-size: 12px;
    color: #64748B;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .kpi-subtext {
    font-size: 11px;
    color: #94A3B8;
    font-style: italic;
  }
  
  .section-header {
    color: #0F172A;
    border-left: 5px solid #4F46E5;
    padding-left: 12px;
    margin-left: 8pt;
    margin-top: 30px;
    margin-bottom: 20px;
    font-weight: 700;
  }
  
  .filter-box {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    border: 1px solid #E2E8F0;
    margin-bottom: 25px;
    position: -webkit-sticky;
    position: sticky;
    top: 0px;
    z-index: 999;
  }
  </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_clean_data():
  try:
    df = pd.read_csv("ai_student_clean.csv")
    return df
  except FileNotFoundError:
    st.error("File 'ai_student_clean.csv' tidak ditemukan. Harap jalankan Notebook analisis terlebih dahulu untuk menghasilkan dataset bersih.")
    return None

df = load_clean_data()

if df is not None:
  st.markdown("<h1 style='text-align: center; color: #0F172A; margin-top: 10px;'> Dashboard Analisis Dampak AI Generatif Mahasiswa</h1>", unsafe_allow_html=True)
  st.markdown("<p style='text-align: center; color: #64748B; font-size: 15px;'>Analisis performa akademik, perilaku belajar, dan kesejahteraan mental terhadap 50.000 mahasiswa.</p>", unsafe_allow_html=True)
  st.markdown("---")

  st.markdown("<h2 class='section-header'> Ringkasan Umum Responden (Keseluruhan Data)</h2>", unsafe_allow_html=True)
  
  col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
  avg_gpa_all = df['Post_Semester_GPA'].mean()
  avg_retention_all = df['Skill_Retention_Score'].mean()
  high_burnout_all = (df['Burnout_Risk_Level'] == 'High').mean() * 100
  
  with col_kpi1:
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-label">IPK Akhir Rata-rata (Global)</div>
        <div class="kpi-value">{avg_gpa_all:.2f} / 4.00</div>
        <div class="kpi-subtext">Seluruh 50.000 data mahasiswa</div>
      </div>
    """, unsafe_allow_html=True)
    
  with col_kpi2:
    st.markdown(f"""
      <div class="kpi-card" style="border-top-color: #6366F1;">
        <div class="kpi-label">Retensi Ilmu Rata-rata (Global)</div>
        <div class="kpi-value">{avg_retention_all:.1f}%</div>
        <div class="kpi-subtext">Mengukur retensi pasca-semester</div>
      </div>
    """, unsafe_allow_html=True)
    
  with col_kpi3:
    st.markdown(f"""
      <div class="kpi-card" style="border-top-color: #EF4444;">
        <div class="kpi-label">Risiko Burnout Tinggi (Global)</div>
        <div class="kpi-value">{high_burnout_all:.1f}%</div>
        <div class="kpi-subtext">Mahasiswa dengan tingkat kelelahan ekstrem</div>
      </div>
    """, unsafe_allow_html=True)
    
  col_chart1, col_chart2 = st.columns([3, 2])
  
  with col_chart1:
    major_counts = df['Major_Category'].value_counts().reset_index()
    major_counts.columns = ['Bidang Studi', 'Jumlah Responden']
    fig_major = px.bar(
      major_counts, 
      x='Bidang Studi', 
      y='Jumlah Responden',
      title="Distribusi Mahasiswa per Bidang Studi",
      labels={'Jumlah Responden': 'Jumlah Mahasiswa'},
      color='Jumlah Responden',
      color_continuous_scale=px.colors.sequential.Purples
    )
    fig_major.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_major, use_container_width=True)
    
  with col_chart2:
    year_counts = df['Year_of_Study'].value_counts().reset_index()
    year_counts.columns = ['Jenjang Studi', 'Jumlah']
    fig_year = px.pie(
      year_counts, 
      values='Jumlah', 
      names='Jenjang Studi',
      title="Proporsi Jenjang Studi",
      color_discrete_sequence=px.colors.qualitative.Safe,
      hole=0.4
    )
    st.plotly_chart(fig_year, use_container_width=True)

  col_chart3, col_chart4 = st.columns(2)
  with col_chart3:
    tool_counts = df['Tool_Diversity'].value_counts().reset_index()
    tool_counts.columns = ['Jumlah Alat AI', 'Jumlah Mahasiswa']
    fig_tools = px.bar(
      tool_counts, x='Jumlah Alat AI', y='Jumlah Mahasiswa',
      title='Distribusi Keragaman Alat AI',
      color='Jumlah Mahasiswa',
      color_continuous_scale=px.colors.sequential.Purples
    )
    fig_tools.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_tools, use_container_width=True)
    
  with col_chart4:
    fig_hours = px.scatter(
      df.sample(1000, random_state=42),
      x='Traditional_Study_Hours', y='Weekly_GenAI_Hours',
      title='Korelasi Waktu Belajar Tradisional vs Jam AI (Sampel 1000 Mahasiswa)',
      labels={'Traditional_Study_Hours': 'Jam Belajar Tradisional', 'Weekly_GenAI_Hours': 'Jam Penggunaan AI'},
      color='Post_Semester_GPA',
      color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_hours.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_hours, use_container_width=True)

  st.markdown("<h2 class='section-header'> Filter Analisis Khusus</h2>", unsafe_allow_html=True)
  
  major_options = sorted(df['Major_Category'].dropna().unique().tolist())
  study_order = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
  year_options = [y for y in study_order if y in df['Year_of_Study'].unique()]
  policy_options = sorted(df['Institutional_Policy'].dropna().unique().tolist())
  
  if 'selected_majors2' not in st.session_state:
    st.session_state.selected_majors2 = major_options
  if 'selected_years2' not in st.session_state:
    st.session_state.selected_years2 = year_options
  if 'selected_policies2' not in st.session_state:
    st.session_state.selected_policies2 = policy_options
    
  st.markdown('<div class="filter-box">', unsafe_allow_html=True)
  col_filt1, col_filt2, col_filt3 = st.columns(3)
  
  with col_filt1:
    selected_majors = st.multiselect(
      "Bidang Studi (Major):",
      options=major_options,
      key='selected_majors2'
    )
  with col_filt2:
    selected_years = st.multiselect(
      "Jenjang Studi (Year):",
      options=year_options,
      key='selected_years2'
    )
  with col_filt3:
    selected_policies = st.multiselect(
      "Kebijakan Institusi terhadap AI:",
      options=policy_options,
      key='selected_policies2'
    )
    
  col_btn1, col_btn2 = st.columns([5, 1])
  with col_btn2:
    if st.button("Reset Filter", use_container_width=True):
      st.session_state.selected_majors2 = major_options
      st.session_state.selected_years2 = year_options
      st.session_state.selected_policies2 = policy_options
      st.rerun()
  st.markdown('</div>', unsafe_allow_html=True)
  
  filt_majors = selected_majors if selected_majors else major_options
  filt_years = selected_years if selected_years else year_options
  filt_policies = selected_policies if selected_policies else policy_options
  
  df_filtered = df[
    (df['Major_Category'].isin(filt_majors)) &
    (df['Year_of_Study'].isin(filt_years)) &
    (df['Institutional_Policy'].isin(filt_policies))
  ]
  
  st.markdown(f"Menampilkan **{len(df_filtered):,}** responden berdasarkan filter khusus di atas.")

  st.markdown("<h2 class='section-header'> Hasil Analisis Khusus</h2>", unsafe_allow_html=True)
  
  col_fkpi1, col_fkpi2, col_fkpi3 = st.columns(3)
  avg_gpa_f = df_filtered['Post_Semester_GPA'].mean()
  avg_ret_f = df_filtered['Skill_Retention_Score'].mean()
  burn_f = (df_filtered['Burnout_Risk_Level'] == 'High').mean() * 100
  
  with col_fkpi1:
    st.markdown(f"<div style='text-align: center; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px; background-color: #FFFFFF;'><b>IPK Rata-rata Terfilter:</b> <span style='color: #4F46E5; font-weight: bold;'>{avg_gpa_f:.2f}</span></div>", unsafe_allow_html=True)
  with col_fkpi2:
    st.markdown(f"<div style='text-align: center; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px; background-color: #FFFFFF;'><b>Retensi Terfilter:</b> <span style='color: #6366F1; font-weight: bold;'>{avg_ret_f:.1f}%</span></div>", unsafe_allow_html=True)
  with col_fkpi3:
    st.markdown(f"<div style='text-align: center; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px; background-color: #FFFFFF;'><b>Burnout Tinggi Terfilter:</b> <span style='color: #EF4444; font-weight: bold;'>{burn_f:.1f}%</span></div>", unsafe_allow_html=True)
    
  st.markdown("<br>", unsafe_allow_html=True)
  
  col_vis1, col_vis2 = st.columns(2)
  
  with col_vis1:
    seg_order = ['Light User', 'Moderate User', 'Heavy User']
    if len(df_filtered) > 0:
      df_grouped = df_filtered.groupby('AI_Usage_Segment')[['Pre_Semester_GPA', 'Post_Semester_GPA']].mean().reindex(seg_order).reset_index()
      df_melted = df_grouped.melt(id_vars=['AI_Usage_Segment'], value_vars=['Pre_Semester_GPA', 'Post_Semester_GPA'],
                     var_name='Semester', value_name='IPK')
      df_melted['Semester'] = df_melted['Semester'].map({'Pre_Semester_GPA': 'IPK Awal', 'Post_Semester_GPA': 'IPK Akhir'})
      
      fig_gpa = px.bar(
        df_melted, 
        x='AI_Usage_Segment', 
        y='IPK', 
        color='Semester', 
        barmode='group',
        title="Perubahan Rata-rata IPK Awal vs Akhir (Data Terfilter)",
        labels={'AI_Usage_Segment': 'Segmen Pengguna AI', 'IPK': 'Rata-rata IPK'},
        color_discrete_sequence=['#94A3B8', '#4F46E5']
      )
      fig_gpa.update_yaxes(range=[2.5, 4.0])
      fig_gpa.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_gpa, use_container_width=True)
    else:
      st.warning("Data kosong untuk filter ini.")
      
  with col_vis2:
    if len(df_filtered) > 0:
      df_crosstab = pd.crosstab(df_filtered['Institutional_Policy'], df_filtered['Burnout_Risk_Level'], normalize='index').reset_index()
      for level in ['Low', 'Medium', 'High']:
        if level not in df_crosstab.columns:
          df_crosstab[level] = 0
      df_crosstab_melted = df_crosstab.melt(id_vars=['Institutional_Policy'], value_vars=['Low', 'Medium', 'High'],
                         var_name='Risiko Burnout', value_name='Proporsi')
      df_crosstab_melted['Persentase (%)'] = df_crosstab_melted['Proporsi'] * 100
      
      fig_burnout = px.bar(
        df_crosstab_melted,
        x='Institutional_Policy',
        y='Persentase (%)',
        color='Risiko Burnout',
        title="Proporsi Risiko Burnout Mahasiswa (Data Terfilter)",
        labels={'Institutional_Policy': 'Kebijakan Kampus terhadap AI'},
        color_discrete_map={
          'Low': '#10B981',
          'Medium': '#F59E0B',
          'High': '#EF4444'
        },
        category_orders={'Risiko Burnout': ['Low', 'Medium', 'High']}
      )
      fig_burnout.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_burnout, use_container_width=True)

  if len(df_filtered) > 0:
    df_ret_dep = df_filtered.groupby('Perceived_AI_Dependency')['Skill_Retention_Score'].mean().reset_index()
    fig_dep_ret = px.bar(
        df_ret_dep,
        x='Perceived_AI_Dependency',
        y='Skill_Retention_Score',
        title='Rata-rata Skor Retensi Pengetahuan berdasarkan Ketergantungan AI (Data Terfilter)',
        labels={'Perceived_AI_Dependency': 'Skor Ketergantungan AI (1-10)', 'Skill_Retention_Score': 'Rata-rata Retensi (%)'},
        color='Skill_Retention_Score',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_dep_ret.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_dep_ret, use_container_width=True)

  st.markdown("<h2 class='section-header'> Fitur Perbandingan Kategori</h2>", unsafe_allow_html=True)
  st.markdown("Pilih satu variabel kategori di bawah ini untuk membandingkan secara langsung performa akademik, retensi, risiko burnout, dan durasi penggunaan AI antar kelompok kategori tersebut pada data yang terfilter.")
  
  var_pembanding = st.selectbox(
    "Pilih Kategori untuk Dibandingkan:",
    options=[
      ("Major_Category", "Rumpun Bidang Studi (Major Category)"),
      ("Year_of_Study", "Jenjang Studi (Year of Study)"),
      ("Institutional_Policy", "Kebijakan Institusi terhadap AI (Institutional Policy)")
    ],
    format_func=lambda x: x[1]
  )[0]
  
  if len(df_filtered) > 0:
    df_compare = df_filtered.groupby(var_pembanding).agg(
      Rata_IPK_Akhir=('Post_Semester_GPA', 'mean'),
      Rata_Retensi_Ilmu=('Skill_Retention_Score', 'mean'),
      Persentase_Burnout_Tinggi=('Burnout_Risk_Level', lambda x: (x == 'High').mean() * 100),
      Rata_Jam_AI_Mingguan=('Weekly_GenAI_Hours', 'mean')
    ).reset_index()
    
    label_map = {
      "Major_Category": "Bidang Studi",
      "Year_of_Study": "Jenjang Studi",
      "Institutional_Policy": "Kebijakan Kampus"
    }
    name_x = label_map[var_pembanding]
    df_compare.rename(columns={var_pembanding: name_x}, inplace=True)
    
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
      fig_comp_gpa = px.bar(
        df_compare,
        x=name_x,
        y='Rata_IPK_Akhir',
        title=f"Perbandingan Rata-rata IPK Akhir per {name_x}",
        labels={'Rata_IPK_Akhir': 'Rata-rata IPK Akhir'},
        color='Rata_IPK_Akhir',
        color_continuous_scale=px.colors.sequential.Blues
      )
      fig_comp_gpa.update_yaxes(range=[2.5, 4.0])
      fig_comp_gpa.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_comp_gpa, use_container_width=True)
      
      fig_comp_burn = px.bar(
        df_compare,
        x=name_x,
        y='Persentase_Burnout_Tinggi',
        title=f"Perbandingan % Risiko Burnout Tinggi per {name_x}",
        labels={'Persentase_Burnout_Tinggi': 'Risiko Burnout Tinggi (%)'},
        color='Persentase_Burnout_Tinggi',
        color_continuous_scale=px.colors.sequential.Reds
      )
      fig_comp_burn.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_comp_burn, use_container_width=True)
      
    with col_comp2:
      fig_comp_ret = px.bar(
        df_compare,
        x=name_x,
        y='Rata_Retensi_Ilmu',
        title=f"Perbandingan Rata-rata Retensi Ilmu per {name_x}",
        labels={'Rata_Retensi_Ilmu': 'Rata-rata Retensi (%)'},
        color='Rata_Retensi_Ilmu',
        color_continuous_scale=px.colors.sequential.Viridis
      )
      fig_comp_ret.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_comp_ret, use_container_width=True)
      
      fig_comp_hours = px.bar(
        df_compare,
        x=name_x,
        y='Rata_Jam_AI_Mingguan',
        title=f"Perbandingan Rata-rata Jam AI per Minggu per {name_x}",
        labels={'Rata_Jam_AI_Mingguan': 'Rata-rata Jam AI / Minggu'},
        color='Rata_Jam_AI_Mingguan',
        color_continuous_scale=px.colors.sequential.Oranges
      )
      fig_comp_hours.update_layout(coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
      st.plotly_chart(fig_comp_hours, use_container_width=True)
      
    st.markdown(f"#### Tabel Komparatif Statistik Rata-rata per {name_x}")
    st.dataframe(df_compare.style.format({
      'Rata_IPK_Akhir': '{:.2f}',
      'Rata_Retensi_Ilmu': '{:.1f}%',
      'Persentase_Burnout_Tinggi': '{:.1f}%',
      'Rata_Jam_AI_Mingguan': '{:.1f} jam'
    }), use_container_width=True)
    
  else:
    st.warning("Tidak ada data terfilter untuk melakukan perbandingan.")

  st.markdown("<h2 class='section-header'> Kesetaraan Akses Digital — Berbayar vs. Gratis</h2>", unsafe_allow_html=True)
  st.markdown("Apakah mahasiswa yang memiliki akses berbayar ke platform AI premium menunjukkan performa akademik dan retensi yang lebih baik? Dan apakah kesenjangan ini signifikan secara statistik?")

  if len(df_filtered) > 0:
    from scipy.stats import ttest_ind

    paid_f = df_filtered[df_filtered['Paid_Subscription'] == True]
    free_f = df_filtered[df_filtered['Paid_Subscription'] == False]

    col_q6_kpi1, col_q6_kpi2, col_q6_kpi3, col_q6_kpi4 = st.columns(4)
    with col_q6_kpi1:
      st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #4F46E5;">
          <div class="kpi-label">IPK Akhir — Berbayar</div>
          <div class="kpi-value">{paid_f['Post_Semester_GPA'].mean():.2f}</div>
          <div class="kpi-subtext">{len(paid_f):,} mahasiswa</div>
        </div>
      """, unsafe_allow_html=True)
    with col_q6_kpi2:
      st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #94A3B8;">
          <div class="kpi-label">IPK Akhir — Gratis</div>
          <div class="kpi-value">{free_f['Post_Semester_GPA'].mean():.2f}</div>
          <div class="kpi-subtext">{len(free_f):,} mahasiswa</div>
        </div>
      """, unsafe_allow_html=True)
    with col_q6_kpi3:
      st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #6366F1;">
          <div class="kpi-label">Retensi — Berbayar</div>
          <div class="kpi-value">{paid_f['Skill_Retention_Score'].mean():.1f}</div>
          <div class="kpi-subtext">Skor rata-rata retensi</div>
        </div>
      """, unsafe_allow_html=True)
    with col_q6_kpi4:
      st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #94A3B8;">
          <div class="kpi-label">Retensi — Gratis</div>
          <div class="kpi-value">{free_f['Skill_Retention_Score'].mean():.1f}</div>
          <div class="kpi-subtext">Skor rata-rata retensi</div>
        </div>
      """, unsafe_allow_html=True)

  st.markdown("<br>", unsafe_allow_html=True)
  col_q6a, col_q6b = st.columns(2)

  with col_q6a:
    df_paid_seg = df_filtered.groupby(['AI_Usage_Segment', 'Paid_Subscription'])['Post_Semester_GPA'].mean().reset_index()
    df_paid_seg['Akses'] = df_paid_seg['Paid_Subscription'].map({True: 'Berbayar', False: 'Gratis'})
    seg_order = ['Light User', 'Moderate User', 'Heavy User']
    fig_q6_bar = go.Figure()
    for akses, color in [('Berbayar', '#4F46E5'), ('Gratis', '#94A3B8')]:
      sub = df_paid_seg[df_paid_seg['Akses'] == akses]
      sub = sub.set_index('AI_Usage_Segment').reindex(seg_order).reset_index()
      fig_q6_bar.add_trace(go.Bar(
        name=akses, x=sub['AI_Usage_Segment'], y=sub['Post_Semester_GPA'],
        marker_color=color, text=sub['Post_Semester_GPA'].round(2),
        textposition='outside'
      ))
    fig_q6_bar.update_layout(
      barmode='group',
      title="IPK Akhir Berbayar vs Gratis per Segmen Pengguna AI",
      yaxis=dict(title='Rata-rata IPK Akhir', range=[2.5, 4.0]),
      xaxis_title='Segmen Pengguna AI',
      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
      legend_title='Jenis Akses'
    )
    st.plotly_chart(fig_q6_bar, use_container_width=True)

  with col_q6b:
    if len(paid_f) > 1 and len(free_f) > 1:
      t_gpa, p_gpa = ttest_ind(paid_f['Post_Semester_GPA'].dropna(), free_f['Post_Semester_GPA'].dropna())
      t_ret, p_ret = ttest_ind(paid_f['Skill_Retention_Score'].dropna(), free_f['Skill_Retention_Score'].dropna())
      sig_gpa = "Signifikan" if p_gpa < 0.05 else "Tidak Signifikan"
      sig_ret = "Signifikan" if p_ret < 0.05 else "Tidak Signifikan"
      st.markdown(f"""
        <div style='background:#FFFFFF;padding:18px;border-radius:12px;border:1px solid #E2E8F0;'>
          <b style='color:#0F172A;font-size:15px;'>Hasil Uji T-Test Independen</b><br><br>
          <b>IPK Akhir:</b> t = {t_gpa:.3f}, p = {p_gpa:.4f} &nbsp; ({sig_gpa})<br>
          <b>Skor Retensi:</b> t = {t_ret:.3f}, p = {p_ret:.4f} &nbsp; ({sig_ret})<br><br>
          <span style='font-size:12px;color:#64748B;'>Signifikan jika p-value &lt; 0.05</span>
        </div>
      """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    df_ret_paid = df_filtered.groupby('Paid_Subscription')['Skill_Retention_Score'].mean().reset_index()
    df_ret_paid['Label'] = df_ret_paid['Paid_Subscription'].map({True: 'Berbayar', False: 'Gratis'})
    fig_q6_ret = px.bar(
      df_ret_paid, x='Label', y='Skill_Retention_Score',
      title="Rata-rata Skor Retensi Pengetahuan: Berbayar vs Gratis",
      labels={'Skill_Retention_Score': 'Skor Retensi', 'Label': 'Jenis Akses'},
      color='Label',
      color_discrete_map={'Berbayar': '#4F46E5', 'Gratis': '#94A3B8'},
      text_auto='.1f'
    )
    fig_q6_ret.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_q6_ret, use_container_width=True)

  st.markdown("<h2 class='section-header'> Faktor Dominan Keberhasilan Akademik</h2>", unsafe_allow_html=True)
  st.markdown("Dari seluruh faktor perilaku belajar yang tersedia, faktor manakah yang memiliki pengaruh paling dominan terhadap IPK akhir mahasiswa? Visualisasi di bawah menampilkan kekuatan korelasi masing-masing variabel.")

  if len(df_filtered) > 10:
    import plotly.figure_factory as ff

    df_q7 = df_filtered[[
      'Post_Semester_GPA', 'Pre_Semester_GPA', 'Traditional_Study_Hours',
      'Weekly_GenAI_Hours', 'Perceived_AI_Dependency', 'Tool_Diversity',
      'Anxiety_Level_During_Exams', 'Skill_Retention_Score'
    ]].copy().dropna()

    corr = df_q7.corr()
    label_map_q7 = {
      'Post_Semester_GPA': 'IPK Akhir',
      'Pre_Semester_GPA': 'IPK Awal',
      'Traditional_Study_Hours': 'Jam Belajar Mandiri',
      'Weekly_GenAI_Hours': 'Jam AI/Minggu',
      'Perceived_AI_Dependency': 'Ketergantungan AI',
      'Tool_Diversity': 'Keragaman Alat AI',
      'Anxiety_Level_During_Exams': 'Kecemasan Ujian',
      'Skill_Retention_Score': 'Skor Retensi'
    }
    corr.index = [label_map_q7.get(c, c) for c in corr.index]
    corr.columns = [label_map_q7.get(c, c) for c in corr.columns]

    fig_heatmap = go.Figure(data=go.Heatmap(
      z=corr.values,
      x=corr.columns.tolist(),
      y=corr.index.tolist(),
      colorscale='RdYlBu',
      zmid=0,
      text=[[f"{v:.2f}" for v in row] for row in corr.values],
      texttemplate="%{text}",
      textfont={"size": 10},
      hoverongaps=False
    ))
    fig_heatmap.update_layout(
      title="Heatmap Korelasi Variabel Perilaku Belajar (Data Terfilter)",
      height=480,
      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
      xaxis=dict(tickangle=-35)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    corr_target = corr['IPK Akhir'].drop('IPK Akhir').sort_values()
    colors_q7 = ['#EF4444' if v < 0 else '#4F46E5' for v in corr_target.values]
    fig_corr_bar = go.Figure(go.Bar(
      x=corr_target.values,
      y=corr_target.index,
      orientation='h',
      marker_color=colors_q7,
      text=[f"{v:.3f}" for v in corr_target.values],
      textposition='outside'
    ))
    fig_corr_bar.update_layout(
      title="Peringkat Faktor Paling Dominan terhadap IPK Akhir",
      xaxis_title="Koefisien Korelasi Pearson",
      yaxis_title="Variabel",
      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
      height=380
    )
    fig_corr_bar.add_vline(x=0, line_color='black', line_width=1)
    st.plotly_chart(fig_corr_bar, use_container_width=True)

    top_positive = corr_target[corr_target > 0].idxmax()
    top_negative = corr_target[corr_target < 0].idxmin()
    st.info(f"**Insight:** Variabel **{top_positive}** memiliki korelasi positif terkuat terhadap IPK Akhir (r = {corr_target[top_positive]:.3f}), sementara **{top_negative}** memiliki korelasi negatif terkuat (r = {corr_target[top_negative]:.3f}).")

  else:
    st.warning("Data terlalu sedikit untuk analisis korelasi yang bermakna. Kurangi filter untuk melihat hasil.")
