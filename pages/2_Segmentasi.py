import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind
from utils import inject_css, load_clean_data, apply_premium_layout, chart_card, CUSTOM_RDBU

st.set_page_config(
    page_title="Segmentasi — Dashboard AI Mahasiswa",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

df = load_clean_data()
if df is None:
    st.stop()

# ── Option lists ──────────────────────────────────────────────────────────────
major_options  = sorted(df['Major_Category'].dropna().unique().tolist())
study_order    = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
year_options   = [y for y in study_order if y in df['Year_of_Study'].unique()]
policy_options = sorted(df['Institutional_Policy'].dropna().unique().tolist())
segment_opts   = ['Light User', 'Moderate User', 'Heavy User']
burnout_opts   = ['Low', 'Medium', 'High']
prompt_opts    = sorted(df['Prompt_Engineering_Skill'].dropna().unique().tolist())

# ── Sidebar filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filter Data")
    st.markdown("---")

    if 'wv' not in st.session_state:
        st.session_state.wv = 0
    wv = st.session_state.wv

    sel_majors = st.multiselect(
        "Bidang Studi",
        options=major_options,
        default=major_options,
        key=f"sb_major_{wv}",
    )
    sel_years = st.multiselect(
        "Jenjang Studi",
        options=year_options,
        default=year_options,
        key=f"sb_year_{wv}",
    )
    sel_policies = st.multiselect(
        "Kebijakan Institusi terhadap AI",
        options=policy_options,
        default=policy_options,
        key=f"sb_policy_{wv}",
    )
    sel_segments = st.multiselect(
        "Segmen Pengguna AI",
        options=segment_opts,
        default=segment_opts,
        key=f"sb_seg_{wv}",
    )
    sel_burnout = st.multiselect(
        "Tingkat Risiko Burnout",
        options=burnout_opts,
        default=burnout_opts,
        key=f"sb_burn_{wv}",
    )

    st.markdown("---")
    if st.button("Reset Semua Filter", use_container_width=True):
        st.session_state.wv += 1
        st.rerun()

# ── Apply filters ─────────────────────────────────────────────────────────────
filt_majors   = sel_majors   if sel_majors   else major_options
filt_years    = sel_years    if sel_years    else year_options
filt_policies = sel_policies if sel_policies else policy_options
filt_segments = sel_segments if sel_segments else segment_opts
filt_burnout  = sel_burnout  if sel_burnout  else burnout_opts

df_f = df[
    (df['Major_Category'].isin(filt_majors)) &
    (df['Year_of_Study'].isin(filt_years)) &
    (df['Institutional_Policy'].isin(filt_policies)) &
    (df['AI_Usage_Segment'].isin(filt_segments)) &
    (df['Burnout_Risk_Level'].isin(filt_burnout))
]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;color:#0F172A;margin-top:6px;font-weight:800;'>"
    "Analisis Segmentasi Terfilter</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center;color:#475569;font-size:15px;'>"
    f"Menampilkan <b>{len(df_f):,}</b> dari {len(df):,} responden berdasarkan filter aktif di sidebar.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if len(df_f) == 0:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter ini. Ubah filter di sidebar.")
    st.stop()

# ── KPI row (terfilter) ───────────────────────────────────────────────────────
avg_gpa_f  = df_f['Post_Semester_GPA'].mean()
avg_ret_f  = df_f['Skill_Retention_Score'].mean()
burn_f     = (df_f['Burnout_Risk_Level'] == 'High').mean() * 100
avg_ai_f   = df_f['Weekly_GenAI_Hours'].mean()
avg_dep_f  = df_f['Perceived_AI_Dependency'].mean()

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "IPK Akhir Rata-rata",         f"{avg_gpa_f:.2f} / 4.00",  "Kelompok terfilter",        "#312E81"),
    (k2, "Retensi Ilmu Rata-rata",       f"{avg_ret_f:.1f}%",        "Skor retensi pasca-semester","#0F766E"),
    (k3, "Risiko Burnout Tinggi",        f"{burn_f:.1f}%",           "Kategori High",              "#991B1B"),
    (k4, "Jam AI per Minggu (Rata)",     f"{avg_ai_f:.1f} jam",      "Penggunaan mingguan",        "#1E3A8A"),
    (k5, "Ketergantungan AI Rata-rata",  f"{avg_dep_f:.1f} / 10",    "Skor persepsi ketergantungan","#581C87"),
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

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  BQ-1 : Apakah penggunaan AI berdampak pada IPK?
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Dampak Penggunaan AI terhadap Performa Akademik</h2>", unsafe_allow_html=True)


seg_order = ['Light User', 'Moderate User', 'Heavy User']
b1c1, b1c2 = st.columns(2)

with b1c1:
    with chart_card("Perubahan Rata-rata IPK per Segmen Pengguna AI"):
        df_seg_gpa = (df_f.groupby('AI_Usage_Segment')[['Pre_Semester_GPA','Post_Semester_GPA']]
                      .mean().reindex(seg_order).reset_index())
        df_seg_gpa_m = df_seg_gpa.melt(id_vars='AI_Usage_Segment',
                                        value_vars=['Pre_Semester_GPA','Post_Semester_GPA'],
                                        var_name='Semester', value_name='IPK')
        df_seg_gpa_m['Semester'] = df_seg_gpa_m['Semester'].map({'Pre_Semester_GPA':'IPK Awal','Post_Semester_GPA':'IPK Akhir'})
        fig_bq1a = px.bar(df_seg_gpa_m, x='AI_Usage_Segment', y='IPK', color='Semester', barmode='group',
                          labels={'AI_Usage_Segment':'Segmen Pengguna AI','IPK':'Rata-rata IPK'},
                          color_discrete_sequence=['#94A3B8','#4F46E5'],
                          category_orders={'AI_Usage_Segment': seg_order})
        fig_bq1a.update_yaxes(range=[2.5, 4.0])
        apply_premium_layout(fig_bq1a, "")
        st.plotly_chart(fig_bq1a, use_container_width=True)

with b1c2:
    with chart_card("Jam Penggunaan AI vs IPK Akhir (Sampel)"):
        # Scatter: Weekly AI hours vs Post GPA
        fig_bq1b = px.scatter(
            df_f.sample(min(3000, len(df_f)), random_state=42),
            x='Weekly_GenAI_Hours', y='Post_Semester_GPA',
            color='AI_Usage_Segment',
            labels={'Weekly_GenAI_Hours':'Jam AI per Minggu','Post_Semester_GPA':'IPK Akhir',
                    'AI_Usage_Segment':'Segmen'},
            color_discrete_map={'Light User':'#0EA5E9','Moderate User':'#0D9488','Heavy User':'#7C3AED'},
            opacity=0.55,
        )
        fig_bq1b.update_traces(marker=dict(size=4))
        apply_premium_layout(fig_bq1b, "")
        st.plotly_chart(fig_bq1b, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  BQ-2 : Apakah penggunaan AI berdampak pada retensi pengetahuan?
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Dampak Penggunaan AI terhadap Retensi Pengetahuan</h2>", unsafe_allow_html=True)


b2c1, b2c2 = st.columns(2)

with b2c1:
    with chart_card("Retensi Pengetahuan vs Skor Ketergantungan AI"):
        df_ret_dep = df_f.groupby('Perceived_AI_Dependency')['Skill_Retention_Score'].mean().reset_index()
        fig_bq2a = px.bar(df_ret_dep, x='Perceived_AI_Dependency', y='Skill_Retention_Score',
                          labels={'Perceived_AI_Dependency':'Skor Ketergantungan AI (1–10)',
                                  'Skill_Retention_Score':'Rata-rata Retensi (%)'},
                          color='Skill_Retention_Score',
                          color_continuous_scale=[[0,'#4F46E5'],[1,'#0EA5E9']])
        apply_premium_layout(fig_bq2a, "")
        fig_bq2a.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bq2a, use_container_width=True)

with b2c2:
    with chart_card("Rata-rata Retensi per Segmen Pengguna AI"):
        df_ret_seg = df_f.groupby('AI_Usage_Segment')['Skill_Retention_Score'].mean().reindex(seg_order).reset_index()
        fig_bq2b = px.bar(df_ret_seg, x='AI_Usage_Segment', y='Skill_Retention_Score',
                          labels={'AI_Usage_Segment':'Segmen Pengguna AI','Skill_Retention_Score':'Rata-rata Retensi (%)'},
                          color='Skill_Retention_Score',
                          color_continuous_scale=[[0,'#4F46E5'],[1,'#10B981']],
                          category_orders={'AI_Usage_Segment': seg_order})
        apply_premium_layout(fig_bq2b, "")
        fig_bq2b.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bq2b, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  BQ-3 : Apakah penggunaan AI berdampak pada kesehatan mental?
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Dampak Penggunaan AI terhadap Kesehatan Mental & Burnout</h2>", unsafe_allow_html=True)


b3c1, b3c2 = st.columns(2)

with b3c1:
    with chart_card("Proporsi Risiko Burnout per Kebijakan Institusi"):
        df_burnout_policy = pd.crosstab(df_f['Institutional_Policy'], df_f['Burnout_Risk_Level'], normalize='index').reset_index()
        for lvl in ['Low','Medium','High']:
            if lvl not in df_burnout_policy.columns:
                df_burnout_policy[lvl] = 0
        df_bp_m = df_burnout_policy.melt(id_vars='Institutional_Policy', value_vars=['Low','Medium','High'],
                                          var_name='Risiko Burnout', value_name='Proporsi')
        df_bp_m['Persentase (%)'] = df_bp_m['Proporsi'] * 100
        fig_bq3a = px.bar(df_bp_m, x='Institutional_Policy', y='Persentase (%)', color='Risiko Burnout',
                          labels={'Institutional_Policy':'Kebijakan Kampus'},
                          color_discrete_map={'Low':'#10B981','Medium':'#F59E0B','High':'#EF4444'},
                          category_orders={'Risiko Burnout':['Low','Medium','High']})
        apply_premium_layout(fig_bq3a, "")
        st.plotly_chart(fig_bq3a, use_container_width=True)

with b3c2:
    with chart_card("Tingkat Kecemasan Ujian per Segmen Pengguna AI"):
        df_anx = df_f.groupby('AI_Usage_Segment')['Anxiety_Level_During_Exams'].mean().reindex(seg_order).reset_index()
        fig_bq3b = px.bar(df_anx, x='AI_Usage_Segment', y='Anxiety_Level_During_Exams',
                          labels={'AI_Usage_Segment':'Segmen Pengguna AI',
                                  'Anxiety_Level_During_Exams':'Rata-rata Kecemasan Ujian (1–10)'},
                          color='Anxiety_Level_During_Exams',
                          color_continuous_scale=[[0,'#F59E0B'],[1,'#EF4444']],
                          category_orders={'AI_Usage_Segment': seg_order})
        apply_premium_layout(fig_bq3b, "")
        fig_bq3b.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bq3b, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  BQ-4 / BQ-5 : Perbandingan per Kategori (Major/Jenjang/Kebijakan)
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Perbandingan Antar Kelompok Kategori</h2>", unsafe_allow_html=True)


var_pembanding = st.selectbox(
    "Pilih Kategori Pembanding:",
    options=[
        ("Major_Category",       "Rumpun Bidang Studi"),
        ("Year_of_Study",        "Jenjang Studi"),
        ("Institutional_Policy", "Kebijakan Institusi terhadap AI"),
    ],
    format_func=lambda x: x[1],
    key="cat_compare_select",
)[0]

label_map_cat = {
    "Major_Category": "Bidang Studi",
    "Year_of_Study": "Jenjang Studi",
    "Institutional_Policy": "Kebijakan Institusi",
}
name_x = label_map_cat[var_pembanding]

df_cmp = df_f.groupby(var_pembanding).agg(
    IPK_Akhir=('Post_Semester_GPA', 'mean'),
    Retensi=('Skill_Retention_Score', 'mean'),
    Burnout_Tinggi=('Burnout_Risk_Level', lambda x: (x=='High').mean() * 100),
    Jam_AI=('Weekly_GenAI_Hours', 'mean'),
).reset_index().rename(columns={var_pembanding: name_x})

cc1, cc2 = st.columns(2)

with cc1:
    with chart_card(f"IPK Akhir per {name_x}"):
        fig_cc1 = px.bar(df_cmp, x=name_x, y='IPK_Akhir',
                         labels={'IPK_Akhir':'Rata-rata IPK Akhir'},
                         color='IPK_Akhir', color_continuous_scale=[[0,'#4F46E5'],[1,'#0EA5E9']])
        fig_cc1.update_yaxes(range=[2.5,4.0])
        apply_premium_layout(fig_cc1, "")
        fig_cc1.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cc1, use_container_width=True)

    with chart_card(f"% Burnout Tinggi per {name_x}"):
        fig_cc3 = px.bar(df_cmp, x=name_x, y='Burnout_Tinggi',
                         labels={'Burnout_Tinggi':'Risiko Burnout Tinggi (%)'},
                         color='Burnout_Tinggi', color_continuous_scale=[[0,'#EF4444'],[1,'#F59E0B']])
        apply_premium_layout(fig_cc3, "")
        fig_cc3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cc3, use_container_width=True)

with cc2:
    with chart_card(f"Retensi Ilmu per {name_x}"):
        fig_cc2 = px.bar(df_cmp, x=name_x, y='Retensi',
                         labels={'Retensi':'Rata-rata Retensi (%)'},
                         color='Retensi', color_continuous_scale=[[0,'#4F46E5'],[1,'#10B981']])
        apply_premium_layout(fig_cc2, "")
        fig_cc2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cc2, use_container_width=True)

    with chart_card(f"Jam AI per Minggu per {name_x}"):
        fig_cc4 = px.bar(df_cmp, x=name_x, y='Jam_AI',
                         labels={'Jam_AI':'Rata-rata Jam AI / Minggu'},
                         color='Jam_AI', color_continuous_scale=[[0,'#4F46E5'],[1,'#7C3AED']])
        apply_premium_layout(fig_cc4, "")
        fig_cc4.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cc4, use_container_width=True)

with chart_card(f"Tabel Komparatif per {name_x}"):
    st.dataframe(
        df_cmp.rename(columns={'IPK_Akhir':'IPK Akhir','Retensi':'Retensi (%)','Burnout_Tinggi':'Burnout Tinggi (%)','Jam_AI':'Jam AI/Minggu'})
        .style.format({'IPK Akhir':'{:.2f}','Retensi (%)':'{:.1f}%','Burnout Tinggi (%)':'{:.1f}%','Jam AI/Minggu':'{:.1f} jam'}),
        use_container_width=True,
    )

# ══════════════════════════════════════════════════════════════════
#  BQ-6 : Berbayar vs Gratis — Kesetaraan Akses Digital
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Kesetaraan Akses Digital — Berbayar vs Gratis</h2>", unsafe_allow_html=True)


paid_f = df_f[df_f['Paid_Subscription'] == True]
free_f = df_f[df_f['Paid_Subscription'] == False]

k1, k2, k3, k4 = st.columns(4)
paid_kpis = [
    (k1, "IPK Akhir — Berbayar", f"{paid_f['Post_Semester_GPA'].mean():.2f}", f"{len(paid_f):,} mahasiswa", "#4F46E5"),
    (k2, "IPK Akhir — Gratis",   f"{free_f['Post_Semester_GPA'].mean():.2f}", f"{len(free_f):,} mahasiswa", "#94A3B8"),
    (k3, "Retensi — Berbayar",   f"{paid_f['Skill_Retention_Score'].mean():.1f}%", "Skor rata-rata", "#10B981"),
    (k4, "Retensi — Gratis",     f"{free_f['Skill_Retention_Score'].mean():.1f}%", "Skor rata-rata", "#94A3B8"),
]
for col, label, val, sub, color in paid_kpis:
    with col:
        st.markdown(
            f"""<div class="kpi-card" style="border-top-color:{color};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-subtext">{sub}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
bq6c1, bq6c2 = st.columns(2)

with bq6c1:
    with chart_card("IPK Akhir Berbayar vs Gratis per Segmen AI"):
        df_paid_seg = df_f.groupby(['AI_Usage_Segment','Paid_Subscription'])['Post_Semester_GPA'].mean().reset_index()
        df_paid_seg['Akses'] = df_paid_seg['Paid_Subscription'].map({True:'Berbayar',False:'Gratis'})
        fig_ps = go.Figure()
        for akses, color in [('Berbayar','#4F46E5'),('Gratis','#94A3B8')]:
            sub = df_paid_seg[df_paid_seg['Akses'] == akses]
            sub = sub.set_index('AI_Usage_Segment').reindex(seg_order).reset_index()
            fig_ps.add_trace(go.Bar(
                name=akses, x=sub['AI_Usage_Segment'], y=sub['Post_Semester_GPA'],
                marker_color=color, text=sub['Post_Semester_GPA'].round(2), textposition='outside',
            ))
        apply_premium_layout(fig_ps, "")
        fig_ps.update_layout(barmode='group',
                              yaxis=dict(range=[2.5,4.0],title='Rata-rata IPK Akhir'),
                              xaxis_title='Segmen Pengguna AI', legend_title='Jenis Akses')
        st.plotly_chart(fig_ps, use_container_width=True)

with bq6c2:
    # T-test
    if len(paid_f) > 1 and len(free_f) > 1:
        t_gpa, p_gpa = ttest_ind(paid_f['Post_Semester_GPA'].dropna(), free_f['Post_Semester_GPA'].dropna())
        t_ret, p_ret = ttest_ind(paid_f['Skill_Retention_Score'].dropna(), free_f['Skill_Retention_Score'].dropna())
        sig_gpa = "Signifikan (p < 0.05)" if p_gpa < 0.05 else "Tidak Signifikan (p ≥ 0.05)"
        sig_ret = "Signifikan (p < 0.05)" if p_ret < 0.05 else "Tidak Signifikan (p ≥ 0.05)"
        st.markdown(f"""
        <div class="stat-box">
          <b style='color:#0F172A;font-size:15px;'>Uji T-Test Independen (Berbayar vs Gratis)</b><br><br>
          <b>Uji IPK Akhir:</b><br>
          &nbsp;&nbsp;• t-hitung = {t_gpa:.3f}<br>
          &nbsp;&nbsp;• p-value = {p_gpa:.4f}<br>
          &nbsp;&nbsp;• Status: <b>{sig_gpa}</b><br><br>
          <b>Uji Skor Retensi:</b><br>
          &nbsp;&nbsp;• t-hitung = {t_ret:.3f}<br>
          &nbsp;&nbsp;• p-value = {p_ret:.4f}<br>
          &nbsp;&nbsp;• Status: <b>{sig_ret}</b><br><br>
          <span style='font-size:12px;color:#64748B;'>*Alpha = 5%. p &lt; 0.05 berarti perbedaan kedua kelompok signifikan secara statistik.</span>
        </div>""", unsafe_allow_html=True)

    with chart_card("Rata-rata Retensi: Berbayar vs Gratis"):
        df_ret_paid = df_f.groupby('Paid_Subscription')['Skill_Retention_Score'].mean().reset_index()
        df_ret_paid['Label'] = df_ret_paid['Paid_Subscription'].map({True:'Berbayar',False:'Gratis'})
        fig_rp = px.bar(df_ret_paid, x='Label', y='Skill_Retention_Score',
                        labels={'Skill_Retention_Score':'Skor Retensi','Label':'Jenis Akses'},
                        color='Label', color_discrete_map={'Berbayar':'#4F46E5','Gratis':'#94A3B8'},
                        text_auto='.1f')
        apply_premium_layout(fig_rp, "")
        fig_rp.update_layout(showlegend=False)
        st.plotly_chart(fig_rp, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  BQ-7 : Faktor Dominan Keberhasilan Akademik
# ══════════════════════════════════════════════════════════════════
st.markdown("<h2 class='section-header'>Faktor Dominan Keberhasilan Akademik</h2>", unsafe_allow_html=True)


if len(df_f) > 30:
    df_q7 = df_f[[
        'Post_Semester_GPA','Pre_Semester_GPA','Delta_IPK','Traditional_Study_Hours',
        'Weekly_GenAI_Hours','Perceived_AI_Dependency','Tool_Diversity',
        'Anxiety_Level_During_Exams','Skill_Retention_Score',
    ]].dropna()
    corr_f = df_q7.corr()
    lm = {
        'Post_Semester_GPA':'IPK Akhir','Pre_Semester_GPA':'IPK Awal',
        'Delta_IPK':'Perbedaan IPK',
        'Traditional_Study_Hours':'Belajar Mandiri','Weekly_GenAI_Hours':'Jam AI/Minggu',
        'Perceived_AI_Dependency':'Ketergantungan AI','Tool_Diversity':'Ragam Tools AI',
        'Anxiety_Level_During_Exams':'Kecemasan Ujian','Skill_Retention_Score':'Retensi Ilmu',
    }
    corr_f.index   = [lm.get(c,c) for c in corr_f.index]
    corr_f.columns = [lm.get(c,c) for c in corr_f.columns]

    bq7c1, bq7c2 = st.columns(2)
    with bq7c1:
        with chart_card("Heatmap Korelasi (Data Terfilter)"):
            fig_heat_f = go.Figure(data=go.Heatmap(
                z=corr_f.values, x=corr_f.columns.tolist(), y=corr_f.index.tolist(),
                colorscale=CUSTOM_RDBU, zmid=0,
                text=[[f"{v:.2f}" for v in row] for row in corr_f.values],
                texttemplate="%{text}", textfont={"size":9,"family":"Inter","color":"#0F172A"},
                hoverongaps=False,
            ))
            apply_premium_layout(fig_heat_f, "")
            fig_heat_f.update_layout(height=430, xaxis=dict(tickangle=-35))
            st.plotly_chart(fig_heat_f, use_container_width=True)

    with bq7c2:
        with chart_card("Peringkat Faktor Dominan terhadap IPK Akhir"):
            corr_t = corr_f['IPK Akhir'].drop(['IPK Akhir', 'Perbedaan IPK'], errors='ignore').sort_values()
            colors_bar = ['#EF4444' if v < 0 else '#4F46E5' for v in corr_t.values]
            fig_cbar_f = go.Figure(go.Bar(
                x=corr_t.values, y=corr_t.index, orientation='h',
                marker_color=colors_bar,
                text=[f"{v:.3f}" for v in corr_t.values], textposition='outside',
            ))
            apply_premium_layout(fig_cbar_f, "")
            fig_cbar_f.update_layout(xaxis_title="Koefisien Korelasi Pearson", height=430)
            fig_cbar_f.add_vline(x=0, line_color='#0F172A', line_width=1)
            st.plotly_chart(fig_cbar_f, use_container_width=True)

    # Delta IPK Visualizations row
    bq7c3, bq7c4 = st.columns(2)
    with bq7c3:
        with chart_card("Distribusi Perbedaan IPK (Delta IPK)"):
            fig_delta_dist = px.histogram(df_f, x='Delta_IPK', nbins=30, color_discrete_sequence=['#8B5CF6'])
            apply_premium_layout(fig_delta_dist, "")
            fig_delta_dist.update_layout(xaxis_title="Perbedaan IPK (IPK Akhir - IPK Awal)", yaxis_title="Frekuensi")
            st.plotly_chart(fig_delta_dist, use_container_width=True)

    with bq7c4:
        with chart_card("Rata-rata Perbedaan IPK per Segmen Pengguna AI"):
            df_delta_seg = df_f.groupby('AI_Usage_Segment')['Delta_IPK'].mean().reindex(seg_order).reset_index()
            fig_delta_seg = px.bar(df_delta_seg, x='AI_Usage_Segment', y='Delta_IPK',
                                   color='Delta_IPK', color_continuous_scale=[[0, '#8B5CF6'], [1, '#4F46E5']],
                                   labels={'AI_Usage_Segment': 'Segmen Pengguna AI', 'Delta_IPK': 'Rata-rata Perbedaan IPK'},
                                   category_orders={'AI_Usage_Segment': seg_order})
            apply_premium_layout(fig_delta_seg, "")
            fig_delta_seg.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_delta_seg, use_container_width=True)

else:
    st.warning("Data terlalu sedikit untuk analisis korelasi yang bermakna. Kurangi filter.")
