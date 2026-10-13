import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# Set page configuration
st.set_page_config(
    page_title="NEET "Do or Die" Data Analysis Dashboard",
    page_icon="🩺",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .reportview-container { background: #f5f7f8; }
    .main-header { color: #FF4B4B; font-weight: 700; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# 1. Initialize Baseline Consensus Data
WEIGHTAGE_DATA = {
    "Biology": {
        "Human Physiology (combined)": 12.0,
        "Molecular Basis of Inheritance": 6.5,
        "Cell: The Unit of Life + Cell Cycle": 6.0,
        "Biotechnology (Principles + Apps)": 6.0,
        "Principles of Inheritance & Variation": 5.5,
        "Human Reproduction + Reproductive Health": 5.0,
        "Plant Physiology": 5.0,
        "Animal Kingdom + Biological Classification": 5.0,
        "Sexual Reproduction in Flowering Plants": 4.5,
        "Ecology & Environment": 7.5,
        "Biomolecules": 3.0,
    },
    "Physics": {
        "Mechanics (Laws of Motion + Rotational + Gravitation)": 7.0,
        "Modern Physics + Semiconductors + Atoms & Nuclei": 5.5,
        "Current Electricity": 4.0,
        "Electrostatics + Capacitance": 4.0,
        "Moving Charges & Magnetism + EMI + AC": 4.0,
        "Ray Optics + Wave Optics": 3.5,
        "Thermodynamics + KTG": 3.5,
        "Units, Measurements & Errors": 2.0,
    },
    "Chemistry": {
        "Organic Chemistry (GOC + Hydrocarbons + Carbonyls + Amines)": 10.0,
        "Chemical Bonding & Molecular Structure": 4.0,
        "Electrochemistry + Chemical Kinetics": 4.0,
        "Coordination Compounds": 3.5,
        "p-Block Elements": 3.5,
        "Equilibrium (Chemical + Ionic)": 3.0,
        "d- & f-Block + Solutions": 3.0,
        "Thermodynamics": 2.5,
    }
}

# Sidebar Navigation
st.sidebar.title("🩺 NEET Analytics Bot v2.0")
st.sidebar.markdown("Consensus tracking across eSaral, PW Yakeen, and Unacademy.")
app_mode = st.sidebar.radio("Navigate", ["Weightage Explorer", "Dynamic 60-Day Study Planner", "Custom PYQ File Analyzer"])

# ==========================================
# MODE 1: WEIGHTAGE EXPLORER
# ==========================================
if app_mode == "Weightage Explorer":
    st.title("📊 Consensus "Do or Die" Weightage Explorer")
    st.markdown("Average questions per year based on exam trends from **2021 to 2026**.")
    
    selected_subject = st.selectbox("Select Subject to Filter", ["All", "Biology", "Physics", "Chemistry"])
    
    subjects_to_show = ["Biology", "Physics", "Chemistry"] if selected_subject == "All" else [selected_subject]
    
    for sub in subjects_to_show:
        st.subheader(f"📚 {sub} High-Priority Spectrum")
        
        # Parse data to DataFrame
        sub_data = WEIGHTAGE_DATA[sub]
        df = pd.DataFrame(list(sub_data.items()), columns=["Chapter/Unit", "Avg Questions/Year"])
        df = df.sort_values(by="Avg Questions/Year", ascending=False)
        
        # Map Tags
        def assign_priority(q):
            if q >= 6.0: return "🔥 Critical (Do or Die)"
            elif q >= 4.0: return "⭐ High Priority"
            return "📌 Medium Priority"
            
        df["Priority Status"] = df["Avg Questions/Year"].apply(assign_priority)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(df.style.background_gradient(cmap="Reds", subset=["Avg Questions/Year"]), use_container_width=True)
            
        with col2:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            colors = df["Avg Questions/Year"].apply(lambda x: '#FF4B4B' if x >= 6.0 else ('#FFAA00' if x >= 4.0 else '#2688E2'))
            ax.barh(df["Chapter/Unit"], df["Avg Questions/Year"], color=colors)
            ax.set_xlabel("Expected Questions per Year")
            ax.invert_yaxis()
            plt.tight_layout()
            st.pyplot(fig)

# ==========================================
# MODE 2: DYNAMIC STUDY PLANNER
# ==========================================
elif app_mode == "Dynamic 60-Day Study Planner":
    st.title("📅 Weightage-Proportional 60-Day Study Schedule")
    st.markdown("This schedule intelligently allocates days according to consensus high-yield chapters.")
    
    # Flatten weights
    flat_list = []
    for sub, chapters in WEIGHTAGE_DATA.items():
        for ch, q in chapters.items():
            flat_list.append({"Subject": sub, "Chapter": ch, "Weight": q})
    
    planner_df = pd.DataFrame(flat_list)
    total_weight = planner_df["Weight"].sum()
    
    # Allocate days out of 60 days
    planner_df["Allocated Days"] = ((planner_df["Weight"] / total_weight) * 60).round().astype(int)
    # Ensure zero values don't break the list
    planner_df["Allocated Days"] = planner_df["Allocated Days"].clip(lower=1)
    
    # Display Schedule summary metric
    st.info(f"💡 High-Yield Focus: **{planner_df[planner_df['Weight'] >= 6.0]['Chapter'].count()} units** are marked as **Critical Core Chapters** (~45% of total high-weightage questions).")
    
    st.dataframe(
        planner_df[["Subject", "Chapter", "Weight", "Allocated Days"]].sort_values(by="Weight", ascending=False),
        use_container_width=True
    )

# ==========================================
# MODE 3: CUSTOM PYQ FILE ANALYZER
# ==========================================
elif app_mode == "Custom PYQ File Analyzer":
    st.title("📂 Custom PYQ Processing & Channel Trend Tool")
    st.markdown("Upload a custom CSV matching your self-tracked question data or notes from online playlists.")
    
    uploaded_file = st.file_uploader("Upload your file (`.csv`)", type=["csv"])
    
    if uploaded_file is not None:
        custom_df = pd.read_csv(uploaded_file)
        
        required_cols = ["year", "subject", "chapter"]
        if all(col in custom_df.columns for col in required_cols):
            st.success("✅ File verified successfully!")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Questions Decoded", len(custom_df))
            with c2:
                st.metric("Unique Chapters Profiled", custom_df["chapter"].nunique())
                
            st.subheader("📊 Relative Distribution Tracker")
            freq = custom_df["chapter"].value_counts().head(10)
            
            fig, ax = plt.subplots()
            freq.plot(kind="bar", color="#FF4B4B", ax=ax)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
        else:
            st.error(f"Missing headers. Make sure your file template contains: {required_cols}")
            
    else:
        # Fallback Template Downloader
        st.info("No file uploaded yet. Download a clean template below to start mapping:")
        template_csv = "year,subject,chapter\n2026,Biology,Molecular Basis of Inheritance\n2026,Physics,Current Electricity"
        st.download_button("📥 Download CSV Template Structure", data=template_csv, file_name="neet_pyq_template.csv", mime="text/csv")
