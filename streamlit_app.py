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
.stApp {background: linear-gradient(180deg,#F7FBFE 0%,#EAF4FA 100%);}
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
section[data-testid="stSidebar"] {background:#005A8B;}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p {color:#FFF !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {background:#FFF !important;border-color:#8CC9E8 !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] span {color:#003B5C !important;}
section[data-testid="stSidebar"] button {border-radius:10px;}
section[data-testid="stSidebar"] button p {color:black !important;}
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

# Approximate coordinates of national capitals. These are used only to position
# selected countries on the real tile-based map.
CAPITALS = {
    "GRC": (37.9838, 23.7275, "Athens"), "DEU": (52.5200, 13.4050, "Berlin"),
    "FRA": (48.8566, 2.3522, "Paris"), "ITA": (41.9028, 12.4964, "Rome"),
    "ESP": (40.4168, -3.7038, "Madrid"), "PRT": (38.7223, -9.1393, "Lisbon"),
    "NLD": (52.3676, 4.9041, "Amsterdam"), "BEL": (50.8503, 4.3517, "Brussels"),
    "AUT": (48.2082, 16.3738, "Vienna"), "SWE": (59.3293, 18.0686, "Stockholm"),
    "NOR": (59.9139, 10.7522, "Oslo"), "DNK": (55.6761, 12.5683, "Copenhagen"),
    "FIN": (60.1699, 24.9384, "Helsinki"), "IRL": (53.3498, -6.2603, "Dublin"),
    "POL": (52.2297, 21.0122, "Warsaw"), "ROU": (44.4268, 26.1025, "Bucharest"),
    "BGR": (42.6977, 23.3219, "Sofia"), "TUR": (39.9334, 32.8597, "Ankara"),
    "GBR": (51.5074, -0.1278, "London"), "USA": (38.9072, -77.0369, "Washington, D.C."),
    "CAN": (45.4215, -75.6972, "Ottawa"), "BRA": (-15.7939, -47.8828, "Brasilia"),
    "ARG": (-34.6037, -58.3816, "Buenos Aires"), "MEX": (19.4326, -99.1332, "Mexico City"),
    "IND": (28.6139, 77.2090, "New Delhi"), "CHN": (39.9042, 116.4074, "Beijing"),
    "JPN": (35.6762, 139.6503, "Tokyo"), "KOR": (37.5665, 126.9780, "Seoul"),
    "AUS": (-35.2809, 149.1300, "Canberra"), "ZAF": (-25.7479, 28.2293, "Pretoria"),
    "EGY": (30.0444, 31.2357, "Cairo"), "KEN": (-1.2921, 36.8219, "Nairobi")
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
    "CO₂ emissions per capita":{"code":"EN.ATM.CO2E.PC","unit":"decimal","description":"Carbon dioxide emissions in metric tons per person"},
}

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
            "Country": country_information.get("value"),
            "Country_Code": item.get("countryiso3code"),
            "Year": item.get("date"),
            "Value": item.get("value"),
            "Indicator": item.get("indicator", {}).get("value"),
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
    st.session_state["selected_indicator"] = "GDP per capita"
    st.session_state["selected_years"] = (2000, current_year)

with st.sidebar:
    st.header("Dashboard Filters")
    st.button("↻ Clear all filters", use_container_width=True, on_click=reset_filters)
    st.caption("Choose countries, an indicator and a period.")
    selected_countries = st.multiselect("Countries", list(COUNTRIES.keys()), default=DEFAULT_COUNTRIES, key="selected_countries")
    selected_indicator = st.selectbox("Development indicator", list(INDICATORS.keys()), index=list(INDICATORS.keys()).index("GDP per capita"), key="selected_indicator")
    selected_years = st.slider("Year range", min_value=1990, max_value=current_year, value=(2000,current_year), step=1, key="selected_years")
    st.divider()
    st.markdown("### Selected indicator")
    st.write(INDICATORS[selected_indicator]["description"])
    st.caption("Data is retrieved from the World Bank API and cached for one hour.")

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()
if len(selected_countries) > 10:
    st.warning("Please select no more than 10 countries so the charts remain readable.")
    st.stop()

indicator_information = INDICATORS[selected_indicator]
indicator_code = indicator_information["code"]
indicator_unit = indicator_information["unit"]
start_year, end_year = selected_years
selected_country_codes = [COUNTRIES[c] for c in selected_countries]

with st.spinner("Retrieving data from the World Bank API..."):
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
    map_data = latest_values.copy()
    map_data["Latitude"] = map_data["Country_Code"].map(lambda code: CAPITALS.get(code, (None,None,None))[0])
    map_data["Longitude"] = map_data["Country_Code"].map(lambda code: CAPITALS.get(code, (None,None,None))[1])
    map_data["Capital"] = map_data["Country_Code"].map(lambda code: CAPITALS.get(code, (None,None,None))[2])
    map_data = map_data.dropna(subset=["Latitude","Longitude"])

    # Use a square-root marker size so very large indicators such as GDP or population
    # do not make smaller countries practically invisible.
    positive_values = map_data["Value"].clip(lower=0)
    max_value = positive_values.max()
    if max_value > 0:
        map_data["Marker_Size"] = 10 + 24 * (positive_values / max_value) ** 0.5
    else:
        map_data["Marker_Size"] = 16

    fig_map = px.scatter_map(
        map_data,
        lat="Latitude",
        lon="Longitude",
        color="Value",
        size="Marker_Size",
        size_max=30,
        hover_name="Country",
        hover_data={
            "Capital": True,
            "Year": True,
            "Value": ":,.2f",
            "Marker_Size": False,
            "Latitude": False,
            "Longitude": False,
        },
        color_continuous_scale=["#80D4EE","#0072BC","#003B5C"],
        map_style="open-street-map",
        zoom=0.6,
    )
    fig_map.update_traces(marker=dict(opacity=0.88))
    fig_map.update_layout(
        title=dict(text=f"Geographic view: {selected_indicator}",x=.02,y=.97,xanchor="left",yanchor="top",font=dict(size=18,color=NAVY)),
        height=470,
        margin=dict(l=8,r=8,t=65,b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title=selected_indicator,thickness=12,len=.60),
    )
    st.plotly_chart(fig_map,use_container_width=True)

with st.expander("View and download the API data"):
    table_data = df[["Country","Country_Code","Year","Indicator","Value"]].sort_values(["Year","Country"],ascending=[False,True])
    st.dataframe(table_data,use_container_width=True,hide_index=True,column_config={"Country_Code":st.column_config.TextColumn("Country code"),"Value":st.column_config.NumberColumn(selected_indicator,format="%.2f")})
    csv_data = table_data.to_csv(index=False).encode("utf-8")
    file_name = selected_indicator.lower().replace(" ","_").replace("₂","2") + "_world_bank_data.csv"
    st.download_button("Download selected data as CSV",data=csv_data,file_name=file_name,mime="text/csv")

st.caption(f"Showing {len(df):,} observations for {len(selected_countries)} selected countries. Data source: World Bank Indicators API.")
