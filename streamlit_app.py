import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Global Development Insights",
    page_icon="🌍",
    layout="wide"
)


# =========================================================
# COLORS
# =========================================================

PRIMARY_BLUE = "#0072BC"
DARK_BLUE = "#005A8B"
NAVY = "#003B5C"
LIGHT_BLUE = "#EAF6FC"
SKY_BLUE = "#59C3E6"
GRID_COLOR = "#DCEAF2"

COLOR_SEQUENCE = [
    "#0072BC",
    "#59C3E6",
    "#005A8B",
    "#9CDBF0",
    "#003B5C",
    "#2B8CC4",
    "#80D4EE",
    "#146C94",
]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            180deg,
            #F7FBFE 0%,
            #EAF4FA 100%
        );
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        color: #003B5C;
    }

    .dashboard-header {
        padding: 24px 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;

        background: linear-gradient(
            110deg,
            #003B5C,
            #005A8B 42%,
            #0072BC 78%,
            #59C3E6
        );

        box-shadow:
            0 10px 30px rgba(0, 90, 139, 0.20);
    }

    .dashboard-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }

    .dashboard-header p {
        color: #EAF6FC;
        margin: 7px 0 0 0;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #CFE4F0;
        padding: 18px 20px;
        border-radius: 15px;

        box-shadow:
            0 6px 18px rgba(0, 90, 139, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        color: #466879;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #005A8B;
        font-weight: 800;
    }

    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #CFE4F0;
        border-radius: 15px;
        padding: 8px;
        overflow: hidden;

        box-shadow:
            0 5px 18px rgba(0, 90, 139, 0.06);
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 750;
        color: #003B5C;
        margin: 16px 0 8px 0;
    }

    section[data-testid="stSidebar"] {
        background: #005A8B;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {

        background: #FFFFFF !important;
        border-color: #8CC9E8 !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] span {

        color: #003B5C !important;
    }

    section[data-testid="stSidebar"] button {
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] button p {
        color: black !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# COUNTRY DEFINITIONS
# =========================================================

COUNTRIES = {
    "Greece": "GRC",
    "Germany": "DEU",
    "France": "FRA",
    "Italy": "ITA",
    "Spain": "ESP",
    "Portugal": "PRT",
    "Netherlands": "NLD",
    "Belgium": "BEL",
    "Austria": "AUT",
    "Sweden": "SWE",
    "Norway": "NOR",
    "Denmark": "DNK",
    "Finland": "FIN",
    "Ireland": "IRL",
    "Poland": "POL",
    "Romania": "ROU",
    "Bulgaria": "BGR",
    "Türkiye": "TUR",
    "United Kingdom": "GBR",
    "United States": "USA",
    "Canada": "CAN",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Mexico": "MEX",
    "India": "IND",
    "China": "CHN",
    "Japan": "JPN",
    "South Korea": "KOR",
    "Australia": "AUS",
    "South Africa": "ZAF",
    "Egypt": "EGY",
    "Kenya": "KEN",
}


# =========================================================
# INDICATOR DEFINITIONS
# =========================================================

INDICATORS = {
    "GDP": {
        "code": "NY.GDP.MKTP.CD",
        "unit": "currency",
        "description": "Gross domestic product in current US dollars",
    },

    "GDP per capita": {
        "code": "NY.GDP.PCAP.CD",
        "unit": "currency",
        "description": "GDP divided by the country's population",
    },

    "GDP growth": {
        "code": "NY.GDP.MKTP.KD.ZG",
        "unit": "percentage",
        "description": "Annual percentage growth of GDP",
    },

    "Population": {
        "code": "SP.POP.TOTL",
        "unit": "number",
        "description": "Total population",
    },

    "Unemployment": {
        "code": "SL.UEM.TOTL.ZS",
        "unit": "percentage",
        "description": "Unemployment as a percentage of the labour force",
    },

    "Inflation": {
        "code": "FP.CPI.TOTL.ZG",
        "unit": "percentage",
        "description": "Annual percentage change in consumer prices",
    },

    "Life expectancy": {
        "code": "SP.DYN.LE00.IN",
        "unit": "years",
        "description": "Life expectancy at birth",
    },

    "Internet users": {
        "code": "IT.NET.USER.ZS",
        "unit": "percentage",
        "description": "Individuals using the internet",
    },

    "Urban population": {
        "code": "SP.URB.TOTL.IN.ZS",
        "unit": "percentage",
        "description": "Urban population as a percentage of total population",
    },

    "CO₂ emissions per capita": {
        "code": "EN.ATM.CO2E.PC",
        "unit": "decimal",
        "description": "Carbon dioxide emissions in metric tons per person",
    },
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_value(value, unit):
    """
    Format indicator values according to their measurement type.
    """

    if pd.isna(value):
        return "No data"

    if unit == "currency":

        if abs(value) >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:,.2f}T"

        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:,.2f}B"

        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:,.2f}M"

        return f"${value:,.0f}"

    if unit == "percentage":
        return f"{value:,.1f}%"

    if unit == "years":
        return f"{value:,.1f} years"

    if unit == "number":

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:,.2f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:,.2f}M"

        if abs(value) >= 1_000:
            return f"{value / 1_000:,.1f}K"

        return f"{value:,.0f}"

    return f"{value:,.2f}"


def axis_format(unit):
    """
    Return Plotly axis formatting settings.
    """

    if unit == "currency":
        return {
            "tickprefix": "$",
            "tickformat": "~s"
        }

    if unit == "percentage":
        return {
            "ticksuffix": "%",
            "tickformat": ",.1f"
        }

    if unit == "years":
        return {
            "ticksuffix": " years",
            "tickformat": ",.1f"
        }

    if unit == "number":
        return {
            "tickformat": "~s"
        }

    return {
        "tickformat": ",.2f"
    }


def style_chart(fig, title, height=420, legend=False):
    """
    Apply a consistent design to every Plotly chart.
    """

    top_margin = 108 if legend else 80

    fig.update_layout(
        title={
            "text": title,
            "x": 0.02,
            "y": 0.96,
            "xanchor": "left",
            "yanchor": "top",
            "font": {
                "size": 18,
                "color": NAVY,
            },
        },

        height=height,

        margin={
            "l": 18,
            "r": 18,
            "t": top_margin,
            "b": 25,
        },

        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",

        font={
            "color": "#365B6D"
        },

        hoverlabel={
            "bgcolor": "white",
            "font_size": 13,
        },
    )

    if legend:
        fig.update_layout(
            legend={
                "orientation": "h",
                "x": 0.02,
                "xanchor": "left",
                "y": 1.02,
                "yanchor": "bottom",
                "title_text": "",
                "font": {
                    "size": 12
                },
            }
        )

    return fig

# =========================================================
# WORLD BANK API CONNECTION
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_world_bank_data(
    country_codes,
    indicator_code,
    start_year,
    end_year
):
    """
    Retrieve data directly from the World Bank API.

    The result is cached for one hour so the app does not
    repeatedly make the same API request.
    """

    countries_for_url = ";".join(country_codes)

    url = (
        "https://api.worldbank.org/v2/"
        f"country/{countries_for_url}/"
        f"indicator/{indicator_code}"
    )

    parameters = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 20000,
    }

    try:

        response = requests.get(
            url,
            params=parameters,
            timeout=30
        )

        response.raise_for_status()

        response_data = response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The World Bank API took too long to respond. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "The application could not connect to the "
            "World Bank API. Check the internet connection."
        )

    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"The World Bank API returned an error: {error}"
        )

    except ValueError:
        raise RuntimeError(
            "The World Bank API returned an invalid response."
        )

    if (
        not isinstance(response_data, list)
        or len(response_data) < 2
        or response_data[1] is None
    ):
        return pd.DataFrame()

    records = []

    for item in response_data[1]:
    country_information = item.get("country", {})

        records.append(
            {
                "Country": country_information.get("value"),
                "Country_Code": item.get("countryiso3code"),
                "Year": item.get("date"),
                "Value": item.get("value"),
                "Indicator": item.get(
                    "indicator", {}
                ).get("value"),
            }
        )

    dataframe = pd.DataFrame(records)

    if dataframe.empty:
        return dataframe

    dataframe["Year"] = pd.to_numeric(
        dataframe["Year"],
        errors="coerce"
    )

    dataframe["Value"] = pd.to_numeric(
        dataframe["Value"],
        errors="coerce"
    )

    dataframe = dataframe.dropna(
        subset=["Year", "Value"]
    )

    dataframe["Year"] = dataframe["Year"].astype(int)

    return dataframe.sort_values(
        ["Country", "Year"]
    )

# =========================================================
# APP HEADER
# =========================================================

st.markdown(
    """
    <div class="dashboard-header">

        <h1>🌍 Global Development Insights</h1>

        <p>
            Explore economic, social and environmental
            indicators retrieved directly from the
            World Bank Indicators API
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DEFAULT VALUES AND FILTER RESET
# =========================================================

current_year = datetime.now().year

DEFAULT_COUNTRIES = [
    "Greece",
    "Germany",
    "France",
    "Italy",
    "Spain",
]


def reset_filters():

    st.session_state["selected_countries"] = DEFAULT_COUNTRIES
    st.session_state["selected_indicator"] = "GDP per capita"
    st.session_state["selected_years"] = (2000, current_year)

# =========================================================
# SIDEBAR FILTERS
# =========================================================

with st.sidebar:

    st.header("Dashboard Filters")

    st.button(
        "↻ Clear all filters",
        use_container_width=True,
        on_click=reset_filters
    )

    st.caption(
        "Choose countries, an indicator and a period."
    )

    selected_countries = st.multiselect(
        "Countries",
        options=list(COUNTRIES.keys()),
        default=DEFAULT_COUNTRIES,
        key="selected_countries"
    )

    selected_indicator = st.selectbox(
        "Development indicator",
        options=list(INDICATORS.keys()),
        index=list(INDICATORS.keys()).index(
            "GDP per capita"
        ),
        key="selected_indicator"
    )

    selected_years = st.slider(
        "Year range",
        min_value=1990,
        max_value=current_year,
        value=(2000, current_year),
        step=1,
        key="selected_years"
    )

    st.divider()

    indicator_description = INDICATORS[
        selected_indicator
    ]["description"]

    st.markdown("### Selected indicator")

    st.write(indicator_description)

    st.caption(
        "Data is retrieved from the World Bank API "
        "and cached for one hour."
    )

# =========================================================
# VALIDATE FILTERS
# =========================================================

if not selected_countries:

    st.warning(
        "Please select at least one country."
    )

    st.stop()


# Limit the number of selected countries for readability

if len(selected_countries) > 10:

    st.warning(
        "Please select no more than 10 countries "
        "so that the charts remain readable."
    )

    st.stop()


indicator_information = INDICATORS[
    selected_indicator
]

indicator_code = indicator_information["code"]
indicator_unit = indicator_information["unit"]

start_year, end_year = selected_years

selected_country_codes = [
    COUNTRIES[country]
    for country in selected_countries
]


# =========================================================
# LOAD DATA
# =========================================================

with st.spinner(
    "Retrieving data from the World Bank API..."
):

    try:

        df = get_world_bank_data(
            country_codes=selected_country_codes,
            indicator_code=indicator_code,
            start_year=start_year,
            end_year=end_year
        )

    except RuntimeError as error:

        st.error(str(error))

        st.info(
            "Wait a moment and refresh the page. "
            "The public API may occasionally respond slowly."
        )

        st.stop()


if df.empty:

    st.warning(
        "The World Bank API did not return data for "
        "this combination of countries, indicator and years."
    )

    st.stop()

# =========================================================
# LATEST AVAILABLE VALUES
# =========================================================

latest_values = (
    df.sort_values("Year")
    .groupby(
        ["Country", "Country_Code"],
        as_index=False
    )
    .tail(1)
    .sort_values("Value", ascending=False)
)


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">'
    'Latest available values'
    '</div>',
    unsafe_allow_html=True
)


card_columns = st.columns(
    min(len(latest_values), 5)
)


for index, (_, row) in enumerate(
    latest_values.head(5).iterrows()
):

    with card_columnsst.metric(
            label=f"{row['Country']} · {row['Year']}",
            value=format_value(
                row["Value"],
                indicator_unit
            )
        )


if len(latest_values) > 5:

    st.caption(
        "The cards show the first five selected countries. "
        "All selected countries remain visible in the charts."
    )

# =========================================================
# TIME-SERIES CHART
# =========================================================

st.markdown(
    '<div class="section-title">'
    'Historical trend'
    '</div>',
    unsafe_allow_html=True
)


fig_trend = px.line(
    df,
    x="Year",
    y="Value",
    color="Country",
    markers=True,
    color_discrete_sequence=COLOR_SEQUENCE,
    hover_data={
        "Country_Code": False,
        "Indicator": False,
    }
)


style_chart(
    fig_trend,
    title=f"{selected_indicator} over time",
    height=470,
    legend=True
)


fig_trend.update_traces(
    line={
        "width": 3
    },

    marker={
        "size": 7
    },

    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Year: %{x}<br>"
        "Value: %{y:,.2f}"
        "<extra></extra>"
    )
)


y_axis_settings = axis_format(
    indicator_unit
)


fig_trend.update_yaxes(
    title=selected_indicator,
    gridcolor=GRID_COLOR,
    zerolinecolor=GRID_COLOR,
    **y_axis_settings
)


fig_trend.update_xaxes(
    title="Year",
    dtick=2,
    gridcolor=GRID_COLOR
)


st.plotly_chart(
    fig_trend,
    use_container_width=True
)

# =========================================================
# COUNTRY COMPARISON AND WORLD MAP
# =========================================================

st.markdown(
    '<div class="section-title">'
    'Latest country comparison'
    '</div>',
    unsafe_allow_html=True
)


left_column, right_column = st.columns(
    [1, 1.25]
)


# ---------------------------------------------------------
# BAR CHART
# ---------------------------------------------------------

with left_column:

    bar_data = latest_values.sort_values(
        "Value",
        ascending=True
    )

    fig_bar = px.bar(
        bar_data,
        x="Value",
        y="Country",
        orientation="h",
        color="Value",
        color_continuous_scale=[
            "#D9F0FA",
            "#59C3E6",
            "#0072BC",
            "#005A8B"
        ],
        text_auto=".3s",
        hover_data={
            "Year": True,
            "Country_Code": False,
        }
    )

    style_chart(
        fig_bar,
        title=f"Latest {selected_indicator.lower()}",
        height=470,
        legend=False
    )

    fig_bar.update_layout(
        coloraxis_showscale=False
    )

    fig_bar.update_xaxes(
        title=selected_indicator,
        gridcolor=GRID_COLOR,
        **y_axis_settings
    )

    fig_bar.update_yaxes(
        title=""
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )


# ---------------------------------------------------------
# WORLD MAP
# ---------------------------------------------------------

with right_column:

    fig_map = px.choropleth(
        latest_values,
        locations="Country_Code",
        color="Value",
        hover_name="Country",
        hover_data={
            "Year": True,
            "Country_Code": False,
            "Value": ":,.2f",
        },
        color_continuous_scale=[
            "#D9F0FA",
            "#80D4EE",
            "#0072BC",
            "#003B5C"
        ],
        projection="natural earth"
    )

    style_chart(
        fig_map,
        title=f"Geographic view: {selected_indicator}",
        height=470,
        legend=False
    )

    fig_map.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#B8CDD8",
        showland=True,
        landcolor="#F2F6F8",
        showocean=True,
        oceancolor="#EAF6FC",
        showcountries=True,
        countrycolor="white",
    )

    fig_map.update_layout(
        coloraxis_colorbar={
            "title": selected_indicator,
            "thickness": 14,
            "len": 0.65,
        }
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

# =========================================================
# DATA TABLE AND DOWNLOAD
# =========================================================

with st.expander(
    "View and download the API data"
):

    table_data = df[
        [
            "Country",
            "Country_Code",
            "Year",
            "Indicator",
            "Value"
        ]
    ].sort_values(
        ["Year", "Country"],
        ascending=[False, True]
    )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,

        column_config={
            "Country_Code": st.column_config.TextColumn(
                "Country code"
            ),

            "Value": st.column_config.NumberColumn(
                selected_indicator,
                format="%.2f"
            ),
        }
    )

    csv_data = table_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download selected data as CSV",
        data=csv_data,
        file_name=(
            selected_indicator
            .lower()
            .replace(" ", "_")
            .replace("₂", "2")
            + "_world_bank_data.csv"
        ),
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.caption(
    f"Showing {len(df):,} observations for "
    f"{len(selected_countries)} selected countries. "
    "Data source: World Bank Indicators API."
)
