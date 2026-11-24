import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(page_title="Global Development Insights", page_icon="🌍", layout="wide")

PRIMARY_BLUE = "#0072BC"
DARK_BLUE = "#005A8B"
NAVY = "#003B5C"
SKY_BLUE = "#59C3E6"
GRID_COLOR = "#DCEAF2"
COLOR_SEQUENCE = ["#0072BC", "#59C3E6", "#005A8B", "#9CDBF0", "#003B5C", "#2B8CC4", "#80D4EE", "#146C94"]

st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#F7FBFE 0%,#EAF4FA 100%);}
.block-container {padding-top:1.4rem;padding-bottom:2rem;max-width:1450px;}
h1,h2,h3 {color:#003B5C;}
.dashboard-header {padding:24px 28px;border-radius:18px;color:white;margin-bottom:20px;background:linear-gradient(110deg,#003B5C,#005A8B 42%,#0072BC 78%,#59C3E6);box-shadow:0 10px 30px rgba(0,90,139,.20);}
.dashboard-header h1 {color:white;margin:0;font-size:2rem;}
.dashboard-header p {color:#EAF6FC;margin:7px 0 0;}
div[data-testid="stMetric"] {background:#FFF;border:1px solid #CFE4F0;padding:18px 20px;border-radius:15px;box-shadow:0 6px 18px rgba(0,90,139,.08);}
div[data-testid="stMetricLabel"] {color:#466879;font-weight:600;}
div[data-testid="stMetricValue"] {color:#005A8B;font-weight:800;}
div[data-testid="stPlotlyChart"] {background:#FFF;border:1px solid #CFE4F0;border-radius:15px;padding:8px;overflow:hidden;box-shadow:0 5px 18px rgba(0,90,139,.06);}
.section-title {font-size:1.15rem;font-weight:750;color:#003B5C;margin:16px 0 8px;}
.indicator-help {background:#FFF;border-left:5px solid #0072BC;padding:10px 14px;border-radius:0 10px 10px 0;color:#365B6D;margin:5px 0 15px;}
section[data-testid="stSidebar"] {background:#005A8B;}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p {color:#FFF !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {background:#FFF !important;border-color:#8CC9E8 !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] span {color:#003B5C !important;}
section[data-testid="stSidebar"] button {border-radius:10px;}
section[data-testid="stSidebar"] button p {color:black !important;}
/* Top indicator navigator */
/* Indicator navigation buttons */
div[data-testid="stSegmentedControl"] {
    background: transparent;
    border: none;
    padding: 4px 0 12px 0;
    box-shadow: none;
}

/* Individual buttons */
div[data-testid="stSegmentedControl"] button {
    border-radius: 20px !important;
    padding: 8px 18px !important;
    min-height: 42px;
    font-weight: 600;
    border: 1px solid #D2D8DE !important;
    background-color: #FFFFFF !important;
    color: #333333 !important;
    box-shadow: 0 2px 6px rgba(0, 59, 92, 0.10);
    transition: all 0.2s ease;
}

/* Button text */
div[data-testid="stSegmentedControl"] button p {
    color: #333333 !important;
}

/* Selected button */
div[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
    background-color: #0072BC !important;
    border-color: #0072BC !important;
    color: #FFFFFF !important;
}

/* Selected button text */
div[data-testid="stSegmentedControl"] button[aria-pressed="true"] p {
    color: #FFFFFF !important;
}

/* Hover */
div[data-testid="stSegmentedControl"] button:hover {
    border-color: #0072BC !important;
    background-color: #EAF6FC !important;
}

/* Selected button hover */
div[data-testid="stSegmentedControl"] button[aria-pressed="true"]:hover {
    background-color: #005A8B !important;
    border-color: #005A8B !important;
}
</style>
""", unsafe_allow_html=True)

COUNTRIES = {
    "Greece":"GRC","Germany":"DEU","France":"FRA","Italy":"ITA","Spain":"ESP","Portugal":"PRT",
    "Netherlands":"NLD","Belgium":"BEL","Austria":"AUT","Sweden":"SWE","Norway":"NOR","Denmark":"DNK",
    "Finland":"FIN","Ireland":"IRL","Poland":"POL","Romania":"ROU","Bulgaria":"BGR","Türkiye":"TUR",
    "United Kingdom":"GBR","United States":"USA","Canada":"CAN","Brazil":"BRA","Argentina":"ARG","Mexico":"MEX",
    "India":"IND","China":"CHN","Japan":"JPN","South Korea":"KOR","Australia":"AUS","South Africa":"ZAF",
    "Egypt":"EGY","Kenya":"KEN"
}

INDICATORS = {
    "GDP":{"code":"NY.GDP.MKTP.CD","unit":"currency","description":"Gross domestic product in current US dollars"},
    "GDP per capita":{"code":"NY.GDP.PCAP.CD","unit":"currency","description":"GDP divided by the country's population"},
    "GDP growth":{"code":"NY.GDP.MKTP.KD.ZG","unit":"percentage","description":"Annual percentage growth of GDP"},
    "Population":{"code":"SP.POP.TOTL","unit":"number","description":"Total population"},
    "Unemployment":{"code":"SL.UEM.TOTL.ZS","unit":"percentage","description":"Unemployment as a percentage of the labour force"},
    "Inflation":{"code":"FP.CPI.TOTL.ZG","unit":"percentage","description":"Annual percentage change in consumer prices"},
    "Life expectancy":{"code":"SP.DYN.LE00.IN","unit":"years","description":"Life expectancy at birth"},
    "Internet users":{"code":"IT.NET.USER.ZS","unit":"percentage","description":"Individuals using the internet as a percentage of population"},
    "Urban population":{"code":"SP.URB.TOTL.IN.ZS","unit":"percentage","description":"Urban population as a percentage of total population"},
    "CO₂ emissions per capita":{"code":"EN.ATM.CO2E.PC","unit":"decimal","description":"Carbon dioxide emissions in metric tons per person"}
}

INDICATOR_ICONS = {
    "GDP":"💰 GDP", "GDP per capita":"👤 GDP per capita", "GDP growth":"📈 GDP growth",
    "Population":"👥 Population", "Unemployment":"💼 Unemployment", "Inflation":"🛒 Inflation",
    "Life expectancy":"❤️ Life expectancy", "Internet users":"🌐 Internet users",
    "Urban population":"🏙️ Urban population", "CO₂ emissions per capita":"🌿 CO₂ per capita"
}
LABEL_TO_INDICATOR = {label: name for name, label in INDICATOR_ICONS.items()}


def format_value(value, unit):
    if pd.isna(value): return "No data"
    if unit == "currency":
        if abs(value) >= 1e12: return f"${value/1e12:,.2f}T"
        if abs(value) >= 1e9: return f"${value/1e9:,.2f}B"
        if abs(value) >= 1e6: return f"${value/1e6:,.2f}M"
        return f"${value:,.0f}"
    if unit == "percentage": return f"{value:,.1f}%"
    if unit == "years": return f"{value:,.1f} years"
    if unit == "number":
        if abs(value) >= 1e9: return f"{value/1e9:,.2f}B"
        if abs(value) >= 1e6: return f"{value/1e6:,.2f}M"
        if abs(value) >= 1e3: return f"{value/1e3:,.1f}K"
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def axis_format(unit):
    if unit == "currency": return {"tickprefix":"$","tickformat":"~s"}
    if unit == "percentage": return {"ticksuffix":"%","tickformat":",.1f"}
    if unit == "years": return {"ticksuffix":" years","tickformat":",.1f"}
    if unit == "number": return {"tickformat":"~s"}
    return {"tickformat":",.2f"}


def style_chart(fig, title, height=420, legend=False):
    fig.update_layout(
        title=dict(text=title,x=.02,y=.96,xanchor="left",yanchor="top",font=dict(size=18,color=NAVY)),
        height=height,margin=dict(l=18,r=18,t=108 if legend else 80,b=25),plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#365B6D"),hoverlabel=dict(bgcolor="white",font_size=13)
    )
    if legend:
        fig.update_layout(legend=dict(orientation="h",x=.02,xanchor="left",y=1.02,yanchor="bottom",title_text="",font=dict(size=12)))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def get_world_bank_data(country_codes, indicator_code, start_year, end_year):
    url = f"https://api.worldbank.org/v2/country/{';'.join(country_codes)}/indicator/{indicator_code}"
    params = {"format":"json","date":f"{start_year}:{end_year}","per_page":20000}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.Timeout as e:
        raise RuntimeError("The World Bank API took too long to respond. Please try again.") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError("The application could not connect to the World Bank API.") from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"The World Bank API returned an HTTP error: {e}") from e
    except ValueError as e:
        raise RuntimeError("The World Bank API returned an invalid response.") from e

    if not isinstance(response_data, list) or len(response_data) < 2 or response_data[1] is None:
        return pd.DataFrame()
    records = []
    for item in response_data[1]:
        country_information = item.get("country", {})
        records.append({
            "Country":country_information.get("value"), "Country_Code":item.get("countryiso3code"),
            "Year":item.get("date"), "Value":item.get("value"),
            "Indicator":item.get("indicator", {}).get("value")
        })
    data = pd.DataFrame(records)
    if data.empty: return data
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
    data = data.dropna(subset=["Year","Value"])
    data["Year"] = data["Year"].astype(int)
    return data.sort_values(["Country","Year"])


st.markdown("""<div class="dashboard-header"><h1>🌍 Global Development Insights</h1><p>Explore indicators retrieved directly from the World Bank Indicators API</p></div>""", unsafe_allow_html=True)

current_year = datetime.now().year
DEFAULT_COUNTRIES = ["Greece","Germany","France","Italy","Spain"]


def reset_filters():
    st.session_state["selected_countries"] = DEFAULT_COUNTRIES
    st.session_state["selected_years"] = (2000, current_year)
    st.session_state["indicator_navigator"] = INDICATOR_ICONS["GDP per capita"]


with st.sidebar:
    st.header("Dashboard Filters")
    st.button("↻ Clear all filters", use_container_width=True, on_click=reset_filters)
    st.caption("Choose countries and a period. Select the indicator from the navigator on the main page.")
    selected_countries = st.multiselect("Countries", list(COUNTRIES.keys()), default=DEFAULT_COUNTRIES, key="selected_countries")
    selected_years = st.slider("Year range", min_value=1990, max_value=current_year, value=(2000,current_year), step=1, key="selected_years")
    st.divider()
    st.caption("Data is retrieved directly from the World Bank API and cached for one hour.")

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()
if len(selected_countries) > 10:
    st.warning("Please select no more than 10 countries so the charts remain readable.")
    st.stop()

# Indicator page navigator, placed directly above the cards.
st.markdown('<div class="section-title">Development indicator</div>', unsafe_allow_html=True)
selected_label = st.segmented_control(
    "Development indicator navigator",
    options=list(LABEL_TO_INDICATOR.keys()),
    default=INDICATOR_ICONS["GDP per capita"],
    selection_mode="single",
    key="indicator_navigator",
    label_visibility="collapsed"
)
if selected_label is None:
    selected_label = INDICATOR_ICONS["GDP per capita"]
selected_indicator = LABEL_TO_INDICATOR[selected_label]
indicator_information = INDICATORS[selected_indicator]
st.markdown(f'<div class="indicator-help"><b>{selected_indicator}</b>: {indicator_information["description"]}</div>', unsafe_allow_html=True)

indicator_code = indicator_information["code"]
indicator_unit = indicator_information["unit"]
start_year, end_year = selected_years
selected_country_codes = [COUNTRIES[c] for c in selected_countries]

with st.spinner(f"Retrieving {selected_indicator.lower()} data from the World Bank API..."):
    try:
        df = get_world_bank_data(selected_country_codes, indicator_code, start_year, end_year)
    except RuntimeError as error:
        st.error(str(error))
        st.info("Wait a moment and refresh the page. The public API may occasionally respond slowly.")
        st.stop()

if df.empty:
    st.warning("The World Bank API did not return data for this combination of countries, indicator and years.")
    st.stop()

latest_values = df.sort_values("Year").groupby(["Country","Country_Code"], as_index=False).tail(1).sort_values("Value",ascending=False)

st.markdown('<div class="section-title">Latest available values</div>', unsafe_allow_html=True)
card_columns = st.columns(min(len(latest_values),5))
for index, (_, row) in enumerate(latest_values.head(5).iterrows()):
    with card_columns[index]:
        st.metric(label=f"{row['Country']} · {row['Year']}", value=format_value(row["Value"], indicator_unit))
if len(latest_values) > 5:
    st.caption("The cards show five countries. All selected countries remain visible in the charts.")

st.markdown('<div class="section-title">Historical trend</div>', unsafe_allow_html=True)
fig_trend = px.line(df,x="Year",y="Value",color="Country",markers=True,color_discrete_sequence=COLOR_SEQUENCE,hover_data={"Country_Code":False,"Indicator":False})
style_chart(fig_trend,f"{selected_indicator} over time",470,True)
fig_trend.update_traces(line=dict(width=3),marker=dict(size=7),hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:,.2f}<extra></extra>")
y_axis_settings = axis_format(indicator_unit)
fig_trend.update_yaxes(title=selected_indicator,gridcolor=GRID_COLOR,zerolinecolor=GRID_COLOR,**y_axis_settings)
fig_trend.update_xaxes(title="Year",dtick=2,gridcolor=GRID_COLOR)
st.plotly_chart(fig_trend,use_container_width=True)

st.markdown('<div class="section-title">Latest country comparison</div>', unsafe_allow_html=True)
left_column,right_column = st.columns([1,1.25])
with left_column:
    bar_data = latest_values.sort_values("Value",ascending=True)
    fig_bar = px.bar(bar_data,x="Value",y="Country",orientation="h",color="Value",color_continuous_scale=["#D9F0FA","#59C3E6","#0072BC","#005A8B"],text_auto=".3s",hover_data={"Year":True,"Country_Code":False})
    style_chart(fig_bar,f"Latest {selected_indicator.lower()}",470,False)
    fig_bar.update_layout(coloraxis_showscale=False)
    fig_bar.update_xaxes(title=selected_indicator,gridcolor=GRID_COLOR,**y_axis_settings)
    fig_bar.update_yaxes(title="")
    st.plotly_chart(fig_bar,use_container_width=True)
with right_column:
    fig_map = px.choropleth(latest_values,locations="Country_Code",color="Value",hover_name="Country",hover_data={"Year":True,"Country_Code":False,"Value":":,.2f"},color_continuous_scale=["#D9F0FA","#80D4EE","#0072BC","#003B5C"],projection="natural earth")
    style_chart(fig_map,f"Geographic view: {selected_indicator}",470,False)
    fig_map.update_geos(showframe=False,showcoastlines=True,coastlinecolor="#B8CDD8",showland=True,landcolor="#F2F6F8",showocean=True,oceancolor="#EAF6FC",showcountries=True,countrycolor="white")
    fig_map.update_layout(coloraxis_colorbar=dict(title=selected_indicator,thickness=14,len=.65))
    st.plotly_chart(fig_map,use_container_width=True)

with st.expander("View and download the API data"):
    table_data = df[["Country","Country_Code","Year","Indicator","Value"]].sort_values(["Year","Country"],ascending=[False,True])
    st.dataframe(table_data,use_container_width=True,hide_index=True,column_config={"Country_Code":st.column_config.TextColumn("Country code"),"Value":st.column_config.NumberColumn(selected_indicator,format="%.2f")})
    csv_data = table_data.to_csv(index=False).encode("utf-8")
    file_name = selected_indicator.lower().replace(" ","_").replace("₂","2") + "_world_bank_data.csv"
    st.download_button("Download selected data as CSV",data=csv_data,file_name=file_name,mime="text/csv")

st.caption(f"Showing {len(df):,} observations for {len(selected_countries)} selected countries. Data source: World Bank Indicators API.")
