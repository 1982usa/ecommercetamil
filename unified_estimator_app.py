import streamlit as st
import pandas as pd
import math
import io
from openpyxl import Workbook

st.set_page_config(page_title="Unified Estimator", layout="wide")
st.title("🧮 Unified Implementation Estimator")

# --- Module Selector ---
module = st.selectbox("🧩 Select Estimation Module", [
    "Rule Implementation",
    "UI Implementation",
    "Rating Implementation",
    "Form Implementation",
    "Data Transformation"
])

# --- Shared Metadata ---
st.header("📁 Project Details")
project_name = st.text_input("Project Name")
user_story = st.text_input("User Story Name")
sub_story = st.text_input("Sub User Story Name")
task_name = st.text_input("Task Name")

# --- Shared Override Toggle ---
use_override = st.toggle("🔧 Use Override Rates", value=True)

# --- Task Definitions ---
task_definitions = {
    "Rule Implementation": [
        ("A. Rating Rules", 10, 0.1),
        ("B. Impacted Tables", 20, 0.1),
        ("C. Impacted Fields", 200, 0.1),
        ("D. Pages Impacted", 10, 0.1),
        ("E. Forms Impacted", 10, 0.1),
        ("F. PLSQL Lines", 50, 0.1),
        ("H. Programming Lines", 50, 0.1),
        ("I. Line of Business Adjustment", 1, 1.0),
        ("J. Complexity Factor", 1, 1.02),
    ],
    "UI Implementation": [
        ("A. Page Rules", 100, 0.01),
        ("B. Impacted Pages", 200, 0.02),
        ("C. Impacted Tables", 20, 0.05),
        ("D. Impacted Fields", 200, 0.01),
        ("E. Page Impacted", 10, 0.1),
        ("F. Forms Impacted", 10, 0.1),
        ("H. PLSQL Lines", 50, 0.1),
        ("I. Programming Lines", 50, 0.1),
        ("J. Line of Business Adjustment", 1, 2.0),
        ("K. Complexity Factor", 1, 1.02),
    ],
    "Rating Implementation": [
        ("A. Number of Rules", 10, 2.0),
        ("B. Rating Elements", 1, 1.0),
        ("C. Impacted Tables", 20, 1.0),
        ("D. Impacted Fields", 200, 1.0),
        ("E. Pages Impacted", 10, 1.0),
        ("G. Forms Impacted", 10, 0.1),
        ("H. PLSQL Lines", 50, 0.1),
        ("I. Programming Lines", 50, 0.1),
        ("J. Line of Business Adjustment", 2, 1.0),
        ("K. Complexity Factor", 1, 1.02),
    ],
    "Form Implementation": [
        ("A. Number of Forms", 10, 2.0),
        ("B. Form Elements", 1, 1.0),
        ("C. Impacted Tables", 20, 1.0),
        ("D. Impacted Fields", 200, 1.0),
        ("E. Pages Impacted", 10, 1.0),
        ("G. Forms Impacted", 10, 0.1),
        ("H. PLSQL Lines", 50, 0.1),
        ("I. Programming Lines", 50, 0.1),
        ("J. Line of Business Adjustment", 2, 1.0),
        ("K. Complexity Factor", 1, 1.02),
    ],
    "Data Transformation": [
        ("A. Number of Fields", 500, 10.0),
        ("B. Number of Policies", 90000, 100000.0),
        ("C. Transactions per Policy", 1, 1.0),
        ("D. Line of Business Adjustment", 1, 1.0),
        ("E. Complexity Factor", 1, 1.0),
    ],
}

# --- Task Inputs ---
st.header("📐 Task Inputs (Quantity × Rate)")
task_data = []
for label, default_qty, default_rate in task_definitions[module]:
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        qty = st.number_input(f"{label} Quantity", value=default_qty, key=f"{label}_qty")
    with col2:
        rate = st.number_input(f"{label} Rate", value=default_rate if use_override else default_rate, key=f"{label}_rate")
    with col3:
        cost = qty * rate
        st.metric(f"{label} Cost", f"${cost:,.4f}")
    task_data.append((label, qty, rate, cost))

# --- Data Point Calculation ---
base_data_point = 1000.0
revised_data_point = 1.0
for _, _, _, cost in task_data:
    revised_data_point *= cost if cost > 0 else 1.0
scaling_factor = math.sqrt(revised_data_point / base_data_point)

st.subheader("📈 Calculated Metrics")
st.metric("Revised Data Points", f"{revised_data_point:,.4f}")
st.metric("Adjusted Scaling Factor", f"{scaling_factor:.4f}")

# --- Negotiation Adjustments ---
st.header("⚙️ Negotiation Adjustments")
col1, col2, col3 = st.columns(3)
with col1:
    platform_multiplier = st.number_input("Platform Adjustment (%)", value=0.6, format="%.2f", key="platform")
with col2:
    profit_margin = st.number_input("Company Profit (%)", value=0.5, format="%.2f", key="profit")
with col3:
    override_scaling = st.number_input("Override Scaling Factor", value=scaling_factor, format="%.4f", key="override")

# --- Resource Table ---
st.header("✏️ Resource Allocation")
resource_template = [
    {"Role": "Business Analyst", "Count": 1.0, "Hours": 480.0, "Rate": 32.18, "Location": "Offshore"},
    {"Role": "Architect", "Count": 1.0, "Hours": 480.0, "Rate": 126.56, "Location": "Onsite"},
    {"Role": "Sr. Engineer", "Count": 1.0, "Hours": 480.0, "Rate": 121.64, "Location": "Onsite"},
    {"Role": "Sr. Engineer", "Count": 2.0, "Hours": 480.0, "Rate": 38.11, "Location": "Offshore"},
    {"Role": "QA", "Count": 2.0, "Hours": 480.0, "Rate": 21.17, "Location": "Offshore"},
    {"Role": "Delivery Manager", "Count": 1.0, "Hours": 240.0, "Rate": 124.64, "Location": "Onsite"},
]
df_resources = pd.DataFrame(resource_template)
edited_resources = st.data_editor(df_resources, num_rows="dynamic", use_container_width=True)

required_cols = {"Count", "Hours", "Rate"}
if required_cols.issubset(edited_resources.columns):
    edited_resources["Cost"] = edited_resources["Count"] * edited_resources["Hours"] * edited_resources["Rate"]
else:
    st.error(f"❌ Missing columns: {required_cols - set(edited_resources.columns)}")
    edited_resources["Cost"] = 0

# --- Cost Calculation ---
base_cost = edited_resources["Cost"].sum()
adjusted_cost = base_cost * override_scaling
platform_cost = adjusted_cost * platform_multiplier
profit = adjusted_cost * profit_margin
final_estimate = adjusted_cost + platform_cost + profit

st.subheader("📊 Cost Breakdown")
st.write(f"**Base Cost:** ${base_cost:,.2f}")
st.write(f"**Adjusted Cost (× {override_scaling:.4f}):** ${adjusted_cost:,.2f}")
st.write(f"**Platform Adjustment ({platform_multiplier:.2f}×):** ${platform_cost:,.2f}")
st.write(f"**Company Profit ({profit_margin:.2f}×):** ${profit:,.2f}")
st.markdown(f"### ✅ Final Estimate: **${final_estimate:,.2f}**")

# --- Excel Export ---
wb = Workbook()
ws = wb.active
ws.title = f"{module} Estimate"
ws.append(["Project Name", project_name])
ws.append(["User Story", user_story])
ws.append(["Sub Story", sub_story])
ws.append(["Task Name", task_name])
ws.append(["Selected Module", module])
ws.append(["Use Override Mode", use_override])
ws.append([])

# Task breakdown
ws.append(["Task", "Quantity", "Rate", "Cost"])
for label, qty, rate, cost in task_data:
    ws.append([label, qty, rate, cost])

ws.append([])
ws.append(["Revised Data Points", revised_data_point])
ws.append(["Scaling Factor", override_scaling])
ws.append(["Base Cost", base_cost])
ws.append(["Adjusted Cost", adjusted_cost])
ws.append(["Platform Cost", platform_cost])
ws.append(["Company Profit", profit])
ws.append(["Final Estimate", final_estimate])
ws.append([])

# Resource breakdown
ws.append(["Role", "Count", "Hours", "Rate", "Location", "Cost"])
for _, row in edited_resources.iterrows():
    ws.append([
        row["Role"], row["Count"], row["Hours"], row["Rate"],
        row["Location"], row["Cost"]
    ])

# Finalize and download
buffer = io.BytesIO()
wb.save(buffer)
buffer.seek(0)

st.download_button(
    label="📥 Download Estimate as Excel",
    data=buffer,
    file_name=f"{module.replace(' ', '_')}_Estimate.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)