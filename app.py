import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Asset Operations",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

    /* ---------- APP ---------- */

    .stApp {
        background-color: #F8F9FB;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1450px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* ---------- TEXT ---------- */

    h1 {
        color: #172033 !important;
        font-size: 29px !important;
        font-weight: 700 !important;
        margin-bottom: 2px !important;
    }

    h2 {
        color: #172033 !important;
        font-size: 19px !important;
    }

    h3 {
        color: #172033 !important;
        font-size: 15px !important;
    }

    .description {
        color: #7A8494;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .small-description {
        color: #8A94A3;
        font-size: 11px;
        margin-top: -5px;
        margin-bottom: 10px;
    }

    /* ---------- METRIC ---------- */

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E8ED;
        border-radius: 7px;
        padding: 14px 16px;
        min-height: 105px;
    }

    [data-testid="stMetricLabel"] {
        color: #7A8494 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #172033 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
    }

    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        font-size: 12px;
        font-weight: 600;
    }

    /* ---------- DATAFRAME ---------- */

    [data-testid="stDataFrame"] {
        border: 1px solid #E5E8ED;
        border-radius: 7px;
    }

    /* ---------- DIVIDER ---------- */

    hr {
        border-color: #E5E8ED;
    }

    /* ---------- SIDEBAR LABEL ---------- */

    .sidebar-title {
        color: #172033;
        font-size: 17px;
        font-weight: 700;
    }

    .sidebar-subtitle {
        color: #8A94A3;
        font-size: 11px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "Asset_Maintenance_Inventory_Cleaned.csv"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
    )

    # Dates
    df["Maintenance_Date"] = pd.to_datetime(
        df["Maintenance_Date"],
        errors="coerce"
    )

    # Numeric columns
    numeric_columns = [
        "Maintenance_Cost_INR",
        "Maintenance_Days",
        "Inventory_Stock",
        "Reorder_Level",
        "Quantity"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

    # Text columns
    text_columns = [
        "Record_ID",
        "Asset_ID",
        "Asset_Type",
        "Unit",
        "Location",
        "Status",
        "Maintenance_Type",
        "Inventory_Item"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
            )

    # Create stock status if required
    if "Stock_Status" not in df.columns:

        df["Stock_Status"] = df.apply(
            lambda row:
            "Low Stock"
            if row["Inventory_Stock"] < row["Reorder_Level"]
            else "Adequate",
            axis=1
        )

    return df


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">ASSET OPERATIONS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Maintenance & Inventory Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Maintenance",
            "Inventory",
            "Asset Records"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("**FILTERS**")

    locations = sorted(
        df["Location"].dropna().unique().tolist()
    )

    selected_locations = st.multiselect(
        "Location",
        locations,
        default=locations
    )

    asset_types = sorted(
        df["Asset_Type"].dropna().unique().tolist()
    )

    selected_asset_types = st.multiselect(
        "Asset Type",
        asset_types,
        default=asset_types
    )

    statuses = sorted(
        df["Status"].dropna().unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Status",
        statuses,
        default=statuses
    )

    st.divider()

    st.caption(
        f"{len(df):,} source records"
    )


# ============================================================
# FILTER DATA
# ============================================================

data = df[
    df["Location"].isin(selected_locations)
    &
    df["Asset_Type"].isin(selected_asset_types)
    &
    df["Status"].isin(selected_statuses)
].copy()


# ============================================================
# COMMON METRICS
# ============================================================

total_records = len(data)

operational = int(
    (data["Status"] == "Operational").sum()
)

under_maintenance = int(
    (data["Status"] == "Under Maintenance").sum()
)

standby = int(
    (data["Status"] == "Standby").sum()
)

total_cost = data[
    "Maintenance_Cost_INR"
].sum()

total_days = data[
    "Maintenance_Days"
].sum()

low_stock = int(
    (data["Stock_Status"] == "Low Stock").sum()
)

operational_rate = (
    operational / total_records * 100
    if total_records > 0
    else 0
)


# ============================================================
# HEADER
# ============================================================

st.title("Asset Operations")

st.markdown(
    '<div class="description">'
    'A centralized view of asset availability, maintenance performance, '
    'maintenance expenditure and inventory readiness across operational locations.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TOP TABS
# ============================================================

tab_summary, tab_maintenance, tab_inventory = st.tabs(
    [
        "Summary",
        "Maintenance",
        "Inventory"
    ]
)


# ============================================================
# SUMMARY
# ============================================================

with tab_summary:

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Total Records",
            f"{total_records:,}",
            help="Number of asset records after applying the selected filters."
        )

    with c2:
        st.metric(
            "Operational Assets",
            f"{operational:,}",
            f"{operational_rate:.1f}%"
        )

    with c3:
        st.metric(
            "Under Maintenance",
            f"{under_maintenance:,}",
            help="Assets currently marked as under maintenance."
        )

    with c4:
        st.metric(
            "Maintenance Cost",
            f"₹{total_cost:,.0f}",
            help="Total recorded maintenance expenditure."
        )

    with c5:
        st.metric(
            "Low Stock Items",
            f"{low_stock:,}",
            help="Inventory records where stock is below the reorder level."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # MAIN SECTION
    # --------------------------------------------------------

    st.subheader("Operations Overview")

    st.markdown(
        '<div class="small-description">'
        'Asset status distribution and maintenance expenditure by operating location.'
        '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.45])

    # --------------------------------------------------------
    # STATUS DONUT
    # --------------------------------------------------------

    with left:

        status_data = (
            data["Status"]
            .value_counts()
            .reset_index()
        )

        status_data.columns = [
            "Status",
            "Records"
        ]

        fig_status = px.pie(
            status_data,
            names="Status",
            values="Records",
            hole=0.62
        )

        fig_status.update_traces(
            textposition="outside",
            textinfo="label+percent"
        )

        fig_status.update_layout(
            height=340,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend=dict(
                orientation="h",
                y=-0.05
            )
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )

    # --------------------------------------------------------
    # LOCATION COST
    # --------------------------------------------------------

    with right:

        location_cost = (
            data
            .groupby(
                "Location",
                as_index=False
            )["Maintenance_Cost_INR"]
            .sum()
            .sort_values(
                "Maintenance_Cost_INR",
                ascending=True
            )
        )

        fig_location = px.bar(
            location_cost,
            x="Maintenance_Cost_INR",
            y="Location",
            orientation="h"
        )

        fig_location.update_traces(
            texttemplate="₹%{x:,.0f}",
            textposition="outside"
        )

        fig_location.update_layout(
            height=340,
            margin=dict(
                l=10,
                r=75,
                t=20,
                b=10
            ),
            xaxis_title="Maintenance Cost (INR)",
            yaxis_title="",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig_location,
            use_container_width=True
        )

    # --------------------------------------------------------
    # MAINTENANCE TREND
    # --------------------------------------------------------

    st.subheader("Maintenance Activity")

    st.markdown(
        '<div class="small-description">'
        'Monthly maintenance expenditure and total maintenance workload based on recorded activity.'
        '</div>',
        unsafe_allow_html=True
    )

    monthly = (
        data
        .dropna(subset=["Maintenance_Date"])
        .assign(
            Month=lambda x:
            x["Maintenance_Date"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby(
            "Month",
            as_index=False
        )
        .agg(
            Maintenance_Cost=(
                "Maintenance_Cost_INR",
                "sum"
            ),
            Maintenance_Days=(
                "Maintenance_Days",
                "sum"
            )
        )
    )

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            monthly,
            x="Month",
            y="Maintenance_Cost"
        )

        fig.update_layout(
            height=320,
            xaxis_title="",
            yaxis_title="Maintenance Cost (INR)",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.line(
            monthly,
            x="Month",
            y="Maintenance_Days",
            markers=True
        )

        fig.update_traces(
            line_width=2.5
        )

        fig.update_layout(
            height=320,
            xaxis_title="",
            yaxis_title="Maintenance Days",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # MANAGEMENT SUMMARY
    # --------------------------------------------------------

    st.subheader("Management Summary")

    location_cost_sorted = location_cost.sort_values(
        "Maintenance_Cost_INR",
        ascending=False
    )

    asset_workload = (
        data
        .groupby(
            "Asset_Type",
            as_index=False
        )["Maintenance_Days"]
        .sum()
        .sort_values(
            "Maintenance_Days",
            ascending=False
        )
    )

    a, b, c = st.columns(3)

    if len(location_cost_sorted) > 0:

        with a:
            top_location = location_cost_sorted.iloc[0]

            st.metric(
                "Highest Cost Location",
                top_location["Location"],
                f"₹{top_location['Maintenance_Cost_INR']:,.0f}"
            )

    if len(asset_workload) > 0:

        with b:
            top_asset = asset_workload.iloc[0]

            st.metric(
                "Highest Maintenance Workload",
                top_asset["Asset_Type"],
                f"{top_asset['Maintenance_Days']:,.0f} days"
            )

    with c:

        st.metric(
            "Standby Assets",
            f"{standby:,}",
            help="Assets currently marked as standby."
        )


# ============================================================
# MAINTENANCE TAB
# ============================================================

with tab_maintenance:

    st.subheader("Maintenance Performance")

    st.markdown(
        '<div class="description">'
        'Analyse where maintenance effort and expenditure are concentrated, '
        'and identify asset categories requiring the most maintenance attention.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    avg_cost = (
        total_cost / total_records
        if total_records > 0
        else 0
    )

    with c1:
        st.metric(
            "Total Cost",
            f"₹{total_cost:,.0f}"
        )

    with c2:
        st.metric(
            "Maintenance Days",
            f"{total_days:,.0f}"
        )

    with c3:
        st.metric(
            "Average Cost / Record",
            f"₹{avg_cost:,.0f}"
        )

    st.markdown("---")

    left, right = st.columns(2)

    # Cost by maintenance type
    with left:

        maintenance_type = (
            data
            .groupby(
                "Maintenance_Type",
                as_index=False
            )["Maintenance_Cost_INR"]
            .sum()
            .sort_values(
                "Maintenance_Cost_INR",
                ascending=False
            )
        )

        fig = px.bar(
            maintenance_type,
            x="Maintenance_Type",
            y="Maintenance_Cost_INR"
        )

        fig.update_layout(
            height=350,
            xaxis_title="Maintenance Type",
            yaxis_title="Cost (INR)",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Asset maintenance workload
    with right:

        workload = (
            data
            .groupby(
                "Asset_Type",
                as_index=False
            )["Maintenance_Days"]
            .sum()
            .sort_values(
                "Maintenance_Days",
                ascending=True
            )
        )

        fig = px.bar(
            workload,
            x="Maintenance_Days",
            y="Asset_Type",
            orientation="h"
        )

        fig.update_layout(
            height=350,
            xaxis_title="Maintenance Days",
            yaxis_title="",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("Maintenance by Asset Type")

    maintenance_table = (
        data
        .groupby(
            "Asset_Type",
            as_index=False
        )
        .agg(
            Records=("Record_ID", "count"),
            Maintenance_Days=(
                "Maintenance_Days",
                "sum"
            ),
            Maintenance_Cost_INR=(
                "Maintenance_Cost_INR",
                "sum"
            )
        )
        .sort_values(
            "Maintenance_Cost_INR",
            ascending=False
        )
    )

    st.dataframe(
        maintenance_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INVENTORY TAB
# ============================================================

with tab_inventory:

    st.subheader("Inventory Readiness")

    st.markdown(
        '<div class="description">'
        'Monitor inventory availability and identify items that have fallen '
        'below their defined reorder thresholds.'
        '</div>',
        unsafe_allow_html=True
    )

    inventory_records = len(data)

    adequate = int(
        (data["Stock_Status"] == "Adequate").sum()
    )

    low = int(
        (data["Stock_Status"] == "Low Stock").sum()
    )

    adequate_rate = (
        adequate / inventory_records * 100
        if inventory_records
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Inventory Records",
            f"{inventory_records:,}"
        )

    with c2:
        st.metric(
            "Low Stock",
            f"{low:,}"
        )

    with c3:
        st.metric(
            "Adequate Stock",
            f"{adequate_rate:.1f}%"
        )

    st.markdown("---")

    left, right = st.columns([1, 1.5])

    with left:

        stock_chart = pd.DataFrame({
            "Status": [
                "Adequate",
                "Low Stock"
            ],
            "Records": [
                adequate,
                low
            ]
        })

        fig = px.pie(
            stock_chart,
            names="Status",
            values="Records",
            hole=0.62
        )

        fig.update_layout(
            height=330,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        inventory_summary = (
            data
            .groupby(
                "Inventory_Item",
                as_index=False
            )
            .agg(
                Current_Stock=(
                    "Inventory_Stock",
                    "mean"
                ),
                Reorder_Level=(
                    "Reorder_Level",
                    "mean"
                )
            )
        )

        inventory_summary["Stock_Gap"] = (
            inventory_summary["Current_Stock"]
            - inventory_summary["Reorder_Level"]
        )

        inventory_summary = (
            inventory_summary
            .sort_values("Stock_Gap")
            .head(10)
        )

        fig = px.bar(
            inventory_summary,
            x="Stock_Gap",
            y="Inventory_Item",
            orientation="h"
        )

        fig.add_vline(
            x=0,
            line_width=1
        )

        fig.update_layout(
            height=330,
            xaxis_title="Stock vs Reorder Level",
            yaxis_title="",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("Items Requiring Attention")

    low_stock_table = data[
        data["Stock_Status"] == "Low Stock"
    ][
        [
            "Inventory_Item",
            "Inventory_Stock",
            "Reorder_Level",
            "Location",
            "Asset_Type"
        ]
    ].sort_values(
        "Inventory_Stock"
    )

    if len(low_stock_table) > 0:

        st.dataframe(
            low_stock_table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No inventory items are currently below the reorder level."
        )


# ============================================================
# ASSET RECORDS
# ============================================================

if page == "Asset Records":

    st.subheader("Asset Records")

    st.markdown(
        '<div class="description">'
        'Search and review the underlying asset, maintenance and inventory records '
        'used throughout the dashboard.'
        '</div>',
        unsafe_allow_html=True
    )

    search = st.text_input(
        "Search Asset ID or Record ID",
        placeholder="Example: AST-1023 or REC-0123"
    )

    records = data.copy()

    if search:

        query = search.strip().lower()

        records = records[
            records["Asset_ID"]
            .str.lower()
            .str.contains(
                query,
                na=False
            )
            |
            records["Record_ID"]
            .str.lower()
            .str.contains(
                query,
                na=False
            )
        ]

    columns = [
        "Record_ID",
        "Asset_ID",
        "Asset_Type",
        "Unit",
        "Location",
        "Status",
        "Maintenance_Type",
        "Maintenance_Date",
        "Maintenance_Days",
        "Maintenance_Cost_INR",
        "Inventory_Item",
        "Inventory_Stock",
        "Reorder_Level"
    ]

    columns = [
        column
        for column in columns
        if column in records.columns
    ]

    st.dataframe(
        records[columns],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"{len(records):,} records displayed"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Asset Operations Analytics • Maintenance & Inventory Management"
)