# AI Impact on Students Academic & Well-being

An interactive Streamlit dashboard and data analysis project exploring how Generative AI usage, study habits, institutional policies, and subscription types impact university students' academic performance (GPA) and mental well-being (burnout risks and exam anxiety).

## Project Overview

This project analyzes a dataset of 50,000 students to address key questions:
1. **Academic Impact**: How does different AI usage intensity (Light, Moderate, Heavy) correlate with GPA?
2. **Knowledge Retention**: Does high AI dependency associate with lower skill retention scores?
3. **Institutional Policy**: How do different policy levels (Strict Ban, Allowed with Citation, Actively Encouraged) affect exam anxiety and burnout?
4. **Burnout Profile**: Which student profiles are most vulnerable to high burnout risk?
5. **Subscription Tier (Digital Equity)**: Do paid/premium AI accounts lead to significant academic disparities compared to free tiers?
6. **Dominant Predictors**: Which study behavioral factors are the strongest predictors of final semester GPA?

## Key Features

- **Data Cleaning & Validation Pipeline**: Systematic preprocessing for corrupted rows, missing values, anomalies, and outliers.
- **Exploratory Data Analysis (EDA)**: High-contrast visualizations of numeric and categorical distributions, correlation heatmaps, and boxplots.
- **Statistical Testing & Modeling**: Independent T-Tests for subscription comparison and Multiple Linear Regression for feature importance.
- **Streamlit Dashboard**: A professional interactive web application containing KPI cards, grouped bar charts, and correlation heatmaps.

## Getting Started

### Prerequisites

Make sure you have Python 3.9+ installed.

### Installation

Clone this repository and install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the Dashboard

To launch the Streamlit dashboard locally, run:

```bash
streamlit run dashboard.py
```

### Running the Analysis Notebook

To review or run the complete analysis workflow, open the Jupyter Notebook:

```bash
jupyter notebook Analisis_AI_Mahasiswa.ipynb
```

## Dataset

- **Raw Data**: `ai_student_impact_dataset.csv` (contains raw survey records).
- **Cleaned Data**: `ai_student_clean.csv` (preprocessed data used in the analysis and dashboard).
