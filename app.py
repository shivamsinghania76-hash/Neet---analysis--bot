import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Page configuration must be called before other Streamlit commands.
st.set_page_config(
    page_title='NEET "Do or Die" Data Analysis Dashboard',
    page_icon="🩺",
    layout="wide",
)

# Custom styling
st.markdown(
    """
    <style>
        .reportview-container { background: #f5f7f8; }
        .main-header { color: #FF4B4B; font-weight: 700; }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Baseline consensus data (values are estimates supplied with this app).
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
    },
}


def assign_priority(questions):
    """Convert estimated question weight into a readable priority label."""
    if questions >= 6.0:
        return "🔥 Critical (Do or Die)"
    if questions >= 4.0:
        return "⭐ High Priority"
    return "📌 Medium Priority"


def allocate_days(weights, total_days=60):
    """Allocate whole days proportionally, ensuring the total equals total_days."""
    if not weights:
        return []
    if total_days < len(weights):
        raise ValueError("Total days must be at least the number of chapters.")

    remaining_days = total_days - len(weights)
    total_weight = sum(weights)
    if total_weight <= 0:
        return [total_days // len(weights)] * len(weights)

    exact_extra = [weight / total_weight * remaining_days for weight in weights]
    whole_extra = [int(value) for value in exact_extra]
    days_left = remaining_days - sum(whole_extra)
    order = sorted(
        range(len(weights)),
        key=lambda index: exact_extra[index] - whole_extra[index],
        reverse=True,
    )
    for index in order[:days_left]:
        whole_extra[index] += 1
    return [1 + value for value in whole_extra]


# Sidebar navigation
st.sidebar.title("🩺 NEET Analytics Bot v2.0")
st.sidebar.markdown("Consensus tracking across eSaral, PW Yakeen, and Unacademy.")
app_mode = st.sidebar.radio(
    "Navigate",
    ["Weightage Explorer", "Dynamic 60-Day Study Planner", "Custom PYQ File Analyzer"],
)

# MODE 1: WEIGHTAGE EXPLORER
if app_mode == "Weightage Explorer":
    st.title('📊 Consensus "Do or Die" Weightage Explorer')
    st.markdown(
        "Average questions per year based on exam trends from **2021 to 2026**. "
        "Treat these figures as estimates, not guaranteed predictions."
    )

    selected_subject = st.selectbox(
        "Select Subject to Filter", ["All", "Biology", "Physics", "Chemistry"]
    )
    subjects_to_show = (
        list(WEIGHTAGE_DATA)
        if selected_subject == "All"
        else [selected_subject]
    )

    for subject in subjects_to_show:
        st.subheader(f"📚 {subject} High-Priority Spectrum")
        df = pd.DataFrame(
            list(WEIGHTAGE_DATA[subject].items()),
            columns=["Chapter/Unit", "Avg Questions/Year"],
        ).sort_values(by="Avg Questions/Year", ascending=False)
        df["Priority Status"] = df["Avg Questions/Year"].apply(assign_priority)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(
                df.style.background_gradient(
                    cmap="Reds", subset=["Avg Questions/Year"]
                ),
                use_container_width=True,
                hide_index=True,
            )
        with col2:
            fig, ax = plt.subplots(figsize=(8, max(3.5, len(df) * 0.38)))
            bar_colors = df["Avg Questions/Year"].apply(
                lambda value: "#FF4B4B"
                if value >= 6.0
                else ("#FFAA00" if value >= 4.0 else "#2688E2")
            )
            ax.barh(df["Chapter/Unit"], df["Avg Questions/Year"], color=bar_colors)
            ax.set_xlabel("Expected Questions per Year")
            ax.invert_yaxis()
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# MODE 2: DYNAMIC STUDY PLANNER
elif app_mode == "Dynamic 60-Day Study Planner":
    st.title("📅 Weightage-Proportional 60-Day Study Schedule")
    st.markdown(
        "Days are distributed proportionally to the supplied chapter weights. "
        "Every chapter receives at least one day, and the schedule totals exactly 60 days."
    )

    rows = [
        {"Subject": subject, "Chapter": chapter, "Weight": weight}
        for subject, chapters in WEIGHTAGE_DATA.items()
        for chapter, weight in chapters.items()
    ]
    planner_df = pd.DataFrame(rows)
    planner_df["Allocated Days"] = allocate_days(planner_df["Weight"].tolist(), 60)

    critical_count = int((planner_df["Weight"] >= 6.0).sum())
    critical_weight = planner_df.loc[planner_df["Weight"] >= 6.0, "Weight"].sum()
    total_weight = planner_df["Weight"].sum()
    critical_share = (critical_weight / total_weight * 100) if total_weight else 0

    metric1, metric2 = st.columns(2)
    metric1.metric("Total planned days", int(planner_df["Allocated Days"].sum()))
    metric2.metric("Critical core chapters", critical_count)
    st.info(
        f"💡 Critical chapters account for approximately {critical_share:.1f}% "
        "of the total weight in this dataset."
    )
    st.dataframe(
        planner_df[["Subject", "Chapter", "Weight", "Allocated Days"]]
        .sort_values(by="Weight", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

# MODE 3: CUSTOM PYQ FILE ANALYZER
elif app_mode == "Custom PYQ File Analyzer":
    st.title("📂 Custom PYQ Processing & Channel Trend Tool")
    st.markdown(
        "Upload a CSV containing at least these columns: `year`, `subject`, and `chapter`."
    )
    uploaded_file = st.file_uploader("Upload your file (.csv)", type=["csv"])

    if uploaded_file is not None:
        try:
            custom_df = pd.read_csv(uploaded_file)
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
            st.error(f"Could not read this CSV file. Check its format and encoding. Details: {exc}")
        else:
            custom_df.columns = custom_df.columns.astype(str).str.strip().str.lower()
            required_cols = ["year", "subject", "chapter"]
            missing_cols = [column for column in required_cols if column not in custom_df.columns]

            if not missing_cols:
                if custom_df.empty:
                    st.warning("The CSV has headers but contains no question rows.")
                else:
                    st.success("✅ File verified successfully!")
                    col1, col2 = st.columns(2)
                    col1.metric("Total Questions Decoded", len(custom_df))
                    col2.metric("Unique Chapters Profiled", custom_df["chapter"].nunique())

                    st.subheader("📊 Relative Distribution Tracker")
                    chapter_values = custom_df["chapter"].dropna().astype(str).str.strip()
                    freq = chapter_values[chapter_values.ne("")].value_counts().head(10)
                    if freq.empty:
                        st.warning("No non-empty chapter names were found in the CSV.")
                    else:
                        fig, ax = plt.subplots(figsize=(9, 4))
                        freq.sort_values().plot(kind="barh", color="#FF4B4B", ax=ax)
                        ax.set_xlabel("Number of rows")
                        ax.set_ylabel("Chapter")
                        fig.tight_layout()
                        st.pyplot(fig)
                        plt.close(fig)
                    with st.expander("Preview uploaded data"):
                        st.dataframe(custom_df.head(100), use_container_width=True)
            else:
                st.error(
                    "Missing required headers: " + ", ".join(missing_cols)
                    + ". Required columns are: year, subject, chapter."
                )
    else:
        st.info("No file uploaded yet. Download a clean template below to start mapping:")
        template_df = pd.DataFrame(
            [
                {"year": 2026, "subject": "Biology", "chapter": "Molecular Basis of Inheritance"},
                {"year": 2026, "subject": "Physics", "chapter": "Current Electricity"},
            ]
        )
        template_csv = template_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV Template Structure",
            data=template_csv,
            file_name="neet_pyq_template.csv",
            mime="text/csv",
        )
        
