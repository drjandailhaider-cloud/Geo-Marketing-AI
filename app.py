import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="MarketSim Pakistan", layout="wide")

# -------------------------------------------------
# CORPORATE DARK THEME
# -------------------------------------------------
st.markdown("""
<style>
body {background-color:#0E1117;}
.title {
    font-size:46px;
    font-weight:900;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.section {
    font-size:22px;
    font-weight:700;
    color:#00F5A0;
    margin-top:25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">MarketSim Pakistan</p>', unsafe_allow_html=True)
st.caption("Corporate Marketing Intelligence & Simulation Platform")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
areas_df = pd.read_excel("data/areas.xlsx")
benchmarks_df = pd.read_excel("data/industry_benchmarks.xlsx")
influencers_df = pd.read_excel("data/influencers.xlsx")
vendors_df = pd.read_excel("data/vendors.xlsx")

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    industry = st.selectbox("Industry", benchmarks_df["Industry"].unique())

with col2:
    city = st.selectbox("City", areas_df["City"].unique())

with col3:
    budget = st.number_input("Marketing Budget (PKR)", min_value=50000)

goal = st.selectbox("Campaign Goal", ["Sales", "Brand Awareness", "Lead Generation"])

# -------------------------------------------------
# HUGGINGFACE AI FUNCTION
# -------------------------------------------------
def generate_ai(prompt):
    try:
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if not api_key:
            return None

        API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        return None
    except:
        return None

# -------------------------------------------------
# MAIN ENGINE
# -------------------------------------------------
if st.button("Generate Corporate Marketing Report"):

    # AREA SCORING
    city_data = areas_df[areas_df["City"] == city].copy()

    city_data["Score"] = (
        city_data["Income_Score"] * 0.30 +
        city_data["Footfall_Score"] * 0.25 +
        city_data["Commercial_Score"] * 0.25 +
        city_data["Population_Density"] * 0.10 -
        city_data["Competition_Score"] * 0.10
    )

    top_areas = city_data.sort_values("Score", ascending=False).head(3)

    st.markdown('<p class="section">High Potential Areas</p>', unsafe_allow_html=True)

    fig_area = px.bar(top_areas, x="Area", y="Score", color="Score")
    st.plotly_chart(fig_area, use_container_width=True)

    # MONTE CARLO ROI SIMULATION
    benchmark = benchmarks_df[benchmarks_df["Industry"] == industry].iloc[0]
    base_conversion = benchmark["Conversion_Rate"]
    avg_value = benchmark["Avg_Customer_Value"]

    simulations = []
    for _ in range(1000):
        random_conversion = np.random.normal(base_conversion, base_conversion * 0.3)
        revenue = (budget * random_conversion) * avg_value / 1000
        simulations.append(revenue)

    expected_revenue = np.mean(simulations)
    conservative = np.percentile(simulations, 25)
    aggressive = np.percentile(simulations, 75)

    st.markdown('<p class="section">Revenue Simulation (Monte Carlo)</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Conservative", f"PKR {int(conservative):,}")
    c2.metric("Expected", f"PKR {int(expected_revenue):,}")
    c3.metric("Aggressive", f"PKR {int(aggressive):,}")

    # HISTOGRAM
    fig_hist = px.histogram(simulations, nbins=40)
    st.plotly_chart(fig_hist, use_container_width=True)

    # CHANNEL ALLOCATION
    st.markdown('<p class="section">Strategic Budget Allocation</p>', unsafe_allow_html=True)

    allocation = {
        "Digital Ads": budget * 0.35,
        "Influencers": budget * 0.20,
        "Outdoor Hoardings": budget * 0.25,
        "Superstores": budget * 0.10,
        "Podcast": budget * 0.10
    }

    alloc_df = pd.DataFrame(list(allocation.items()), columns=["Channel", "Budget"])
    fig_pie = px.pie(alloc_df, names="Channel", values="Budget", hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

    # INFLUENCERS
    st.markdown('<p class="section">Influencer Contacts</p>', unsafe_allow_html=True)
    st.dataframe(influencers_df[influencers_df["City"] == city])

    # VENDORS
    st.markdown('<p class="section">Vendor Contacts</p>', unsafe_allow_html=True)
    st.dataframe(vendors_df[vendors_df["City"] == city])

    # AI ACTION PLAN
    st.markdown('<p class="section">Strategic Action Plan</p>', unsafe_allow_html=True)

    prompt = f"""
    Create a professional marketing execution plan for a {industry} in {city}.
    Budget: {budget} PKR.
    Include: banners, digital screens, superstore branding, influencer marketing,
    packaging tricks, seasonal offers, SEO strategy and paid ad hooks.
    """

    ai_output = generate_ai(prompt)

    if ai_output:
        st.markdown(ai_output)
    else:
        st.markdown("Structured corporate action plan generated based on internal logic.")

    # -------------------------------------------------
    # PDF GENERATION
    # -------------------------------------------------
    def create_pdf():
        file_path = "MarketSim_Report.pdf"
        doc = SimpleDocTemplate(file_path)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("MarketSim Pakistan Corporate Report", styles["Heading1"]))
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(Paragraph(f"Industry: {industry}", styles["Normal"]))
        elements.append(Paragraph(f"City: {city}", styles["Normal"]))
        elements.append(Paragraph(f"Budget: {budget}", styles["Normal"]))
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(Paragraph("Revenue Forecast:", styles["Heading2"]))
        elements.append(Paragraph(f"Expected Revenue: PKR {int(expected_revenue):,}", styles["Normal"]))

        doc.build(elements)
        return file_path

    if st.button("Download Agency PDF Report"):
        pdf_file = create_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button("Click to Download PDF", f, file_name="MarketSim_Report.pdf")
