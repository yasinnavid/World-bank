import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(page_title="Global Development Insights", page_icon="🌍", layout="wide")

NAVY = "#003B5C"
BLUE = "#0072BC"
DARK_BLUE = "#005A8B"
SKY = "#59C3E6"
GRID = "#DCEAF2"
COLORS = [BLUE, SKY, DARK_BLUE, "#9CDBF0", NAVY, "#2B8CC4", "#80D4EE", "#146C94"]

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
.indicator-help {background:#FFF;border-left:5px solid #0072BC;padding:10px 14px;border-radius:0 10px 10px 0;color:#365B6D;margin:8px 0 15px;}
section[data-testid="stSidebar"] {background:#005A8B;}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p {color:#FFF !important;}
section[data-testid="stSidebar"] button {border-radius:10px;}
section[data-testid="stSidebar"] button p {color:#111 !important;}

/* INDICATOR NAVIGATION: actual st.button widgets, not segmented controls */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    border-radius:20px !important;
    min-height:44px !important;
    padding:8px 14px !important;
    border:1px solid #CCD5DD !important;
    background:#FFFFFF !important;
    color:#30343B !important;
    box-shadow:0 2px 7px rgba(0,59,92,.10) !important;
    font-weight:600 !important;
    transition:background .15s ease,border-color .15s ease,color .15s ease !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button p {color:#30343B !important;font-weight:600 !important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {
    border-color:#0072BC !important;
    background:#EAF6FC !important;
    color:#003B5C !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover p {color:#003B5C !important;}
</style>
""", unsafe_allow_html=True)

COUNTRIES = {
    "Greece":"GRC","Germany":"DEU","France":"FRA","Italy":"ITA","Spain":"ESP","Portugal":"PRT",
    "Netherlands":"NLD","Belgium":"BEL","Austria":"AUT","Sweden":"SWE","Norway":"NOR","Denmark":"DNK",
    "Finland":"FIN","Ireland":"IRL","Poland":"POL","Romania":"ROU","Bulgaria":"BGR","Türkiye":"TUR",
    "United Kingdom":"GBR","United States":"USA","Canada":"CAN","Brazil":"BRA","Argentina":"ARG","Mexico":"MEX",
    "India":"IND","China":"CHN","Japan":"JPN","South Korea":"KOR","Australia":"AUS","South Africa":"ZAF","Egypt":"EGY","Kenya":"KEN"
}

INDICATORS = {
    "GDP":{"code":"NY.GDP.MKTP.CD","unit":"currency","description":"Gross domestic product in current US dollars","label":"GDP"},
    "GDP per capita":{"code":"NY.GDP.PCAP.CD","unit":"currency","description":"GDP divided by the country's population","label":"GDP per capita"},
    "GDP growth":{"code":"NY.GDP.MKTP.KD.ZG","unit":"percentage","description":"Annual percentage growth of GDP","label":"GDP growth"},
    "Population":{"code":"SP.POP.TOTL","unit":"number","description":"Total population","label":"Population"},
    "Unemployment":{"code":"SL.UEM.TOTL.ZS","unit":"percentage","description":"Unemployment as a percentage of the labour force","label":"Unemployment"},
    "Inflation":{"code":"FP.CPI.TOTL.ZG","unit":"percentage","description":"Annual percentage change in consumer prices","label":"Inflation"},
    "Life expectancy":{"code":"SP.DYN.LE00.IN","unit":"years","description":"Life expectancy at birth","label":"Life expectancy"},
    "Internet users":{"code":"IT.NET.USER.ZS","unit":"percentage","description":"Individuals using the internet as a percentage of population","label":"Internet users"},
    "Urban population":{"code":"SP.URB.TOTL.IN.ZS","unit":"percentage","description":"Urban population as a percentage of total population","label":"Urban population"},
    "CO₂ emissions per capita":{"code":"EN.ATM.CO2E.PC","unit":"decimal","description":"Carbon dioxide emissions in metric tons per person","label":"CO₂ per capita"}
}


def format_value(v, unit):
    if pd.isna(v): return "No data"
    if unit == "currency":
        if abs(v) >= 1e12: return f"${v/1e12:,.2f}T"
        if abs(v) >= 1e9: return f"${v/1e9:,.2f}B"
        if abs(v) >= 1e6: return f"${v/1e6:,.2f}M"
        return f"${v:,.0f}"
    if unit == "percentage": return f"{v:,.1f}%"
    if unit == "years": return f"{v:,.1f} years"
    if unit == "number":
        if abs(v) >= 1e9: return f"{v/1e9:,.2f}B"
        if abs(v) >= 1e6: return f"{v/1e6:,.2f}M"
        if abs(v) >= 1e3: return f"{v/1e3:,.1f}K"
        return f"{v:,.0f}"
    return f"{v:,.2f}"


def axis_format(unit):
    if unit == "currency": return {"tickprefix":"$","tickformat":"~s"}
    if unit == "percentage": return {"ticksuffix":"%","tickformat":",.1f"}
    if unit == "years": return {"ticksuffix":" years","tickformat":",.1f"}
    if unit == "number": return {"tickformat":"~s"}
    return {"tickformat":",.2f"}


def style_chart(fig, title, height=420, legend=False):
    fig.update_layout(title=dict(text=title,x=.02,y=.96,xanchor="left",yanchor="top",font=dict(size=18,color=NAVY)),height=height,
                      margin=dict(l=18,r=18,t=108 if legend else 80,b=25),plot_bgcolor="white",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#365B6D"))
    if legend:
        fig.update_layout(legend=dict(orientation="h",x=.02,xanchor="left",y=1.02,yanchor="bottom",title_text=""))


@st.cache_data(ttl=3600, show_spinner=False)
def get_world_bank_data(country_codes, indicator_code, start_year, end_year):
    url = f"https://api.worldbank.org/v2/country/{';'.join(country_codes)}/indicator/{indicator_code}"
    params = {"format":"json","date":f"{start_year}:{end_year}","per_page":20000}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        raw = r.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not retrieve World Bank data: {e}") from e
    except ValueError as e:
        raise RuntimeError("The World Bank API returned an invalid response.") from e
    if not isinstance(raw,list) or len(raw)<2 or raw[1] is None: return pd.DataFrame()
    records=[]
    for item in raw[1]:
        records.append({"Country":item.get("country",{}).get("value"),"Country_Code":item.get("countryiso3code"),"Year":item.get("date"),"Value":item.get("value"),"Indicator":item.get("indicator",{}).get("value")})
    data=pd.DataFrame(records)
    if data.empty: return data
    data["Year"]=pd.to_numeric(data["Year"],errors="coerce")
    data["Value"]=pd.to_numeric(data["Value"],errors="coerce")
    data=data.dropna(subset=["Year","Value"]); data["Year"]=data["Year"].astype(int)
    return data.sort_values(["Country","Year"])


st.markdown('<div class="dashboard-header"><h1>🌍 Global Development Insights</h1><p>Explore indicators retrieved directly from the World Bank Indicators API</p></div>',unsafe_allow_html=True)
current_year=datetime.now().year
DEFAULT_COUNTRIES=["Greece","Germany","France","Italy","Spain"]

if "current_indicator" not in st.session_state:
    st.session_state.current_indicator="GDP per capita"

def choose_indicator(name):
    st.session_state.current_indicator=name

def reset_filters():
    st.session_state.selected_countries=DEFAULT_COUNTRIES
    st.session_state.selected_years=(2000,current_year)
    st.session_state.current_indicator="GDP per capita"

with st.sidebar:
    st.header("Dashboard Filters")
    st.button("↻ Clear all filters",use_container_width=True,on_click=reset_filters,key="clear_filters")
    st.caption("Choose countries and a period. Use the buttons on the main page to change indicator.")
    selected_countries=st.multiselect("Countries",list(COUNTRIES),default=DEFAULT_COUNTRIES,key="selected_countries")
    selected_years=st.slider("Year range",1990,current_year,(2000,current_year),key="selected_years")
    st.divider(); st.caption("Data is retrieved directly from the World Bank API and cached for one hour.")

if not selected_countries:
    st.warning("Please select at least one country."); st.stop()
if len(selected_countries)>10:
    st.warning("Please select no more than 10 countries."); st.stop()

st.markdown('<div class="section-title">Development indicator</div>',unsafe_allow_html=True)

# Real Streamlit buttons in two rows. The selected button uses type="primary".
names=list(INDICATORS.keys())
for row_names in (names[:5], names[5:]):
    cols=st.columns(len(row_names))
    for col,name in zip(cols,row_names):
        with col:
            active=(st.session_state.current_indicator==name)
            st.button(INDICATORS[name]["label"],key=f"nav_{name}",use_container_width=True,type="primary" if active else "secondary",on_click=choose_indicator,args=(name,))

selected_indicator=st.session_state.current_indicator
info=INDICATORS[selected_indicator]
st.markdown(f'<div class="indicator-help"><b>{selected_indicator}</b>: {info["description"]}</div>',unsafe_allow_html=True)

codes=[COUNTRIES[c] for c in selected_countries]
start_year,end_year=selected_years
with st.spinner(f"Retrieving {selected_indicator.lower()} data from the World Bank API..."):
    try:
        df=get_world_bank_data(codes,info["code"],start_year,end_year)
    except RuntimeError as e:
        st.error(str(e)); st.stop()
if df.empty:
    st.warning("The World Bank API did not return data for this selection."); st.stop()

latest=df.sort_values("Year").groupby(["Country","Country_Code"],as_index=False).tail(1).sort_values("Value",ascending=False)
st.markdown('<div class="section-title">Latest available values</div>',unsafe_allow_html=True)
metric_cols=st.columns(min(len(latest),5))
for i,(_,row) in enumerate(latest.head(5).iterrows()):
    metric_cols[i].metric(f"{row['Country']} · {row['Year']}",format_value(row["Value"],info["unit"]))

st.markdown('<div class="section-title">Historical trend</div>',unsafe_allow_html=True)
fig=px.line(df,x="Year",y="Value",color="Country",markers=True,color_discrete_sequence=COLORS,hover_data={"Country_Code":False,"Indicator":False})
style_chart(fig,f"{selected_indicator} over time",470,True); fig.update_traces(line=dict(width=3),marker=dict(size=7))
yfmt=axis_format(info["unit"]); fig.update_yaxes(title=selected_indicator,gridcolor=GRID,**yfmt); fig.update_xaxes(title="Year",dtick=2,gridcolor=GRID)
st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="section-title">Latest country comparison</div>',unsafe_allow_html=True)
l,r=st.columns([1,1.25])
with l:
    b=latest.sort_values("Value")
    figb=px.bar(b,x="Value",y="Country",orientation="h",color="Value",color_continuous_scale=["#D9F0FA",SKY,BLUE,DARK_BLUE],text_auto=".3s")
    style_chart(figb,f"Latest {selected_indicator.lower()}",470); figb.update_layout(coloraxis_showscale=False); figb.update_xaxes(title=selected_indicator,gridcolor=GRID,**yfmt); figb.update_yaxes(title="")
    st.plotly_chart(figb,use_container_width=True)
with r:
    figm=px.choropleth(latest,locations="Country_Code",color="Value",hover_name="Country",hover_data={"Year":True,"Country_Code":False,"Value":":,.2f"},color_continuous_scale=["#D9F0FA","#80D4EE",BLUE,NAVY],projection="natural earth")
    style_chart(figm,f"Geographic view: {selected_indicator}",470); figm.update_geos(showframe=False,showland=True,landcolor="#F2F6F8",showocean=True,oceancolor="#EAF6FC",showcountries=True,countrycolor="white")
    figm.update_layout(coloraxis_colorbar=dict(title=selected_indicator,thickness=14,len=.65)); st.plotly_chart(figm,use_container_width=True)

with st.expander("View and download the API data"):
    table=df[["Country","Country_Code","Year","Indicator","Value"]].sort_values(["Year","Country"],ascending=[False,True])
    st.dataframe(table,use_container_width=True,hide_index=True)
    st.download_button("Download selected data as CSV",table.to_csv(index=False).encode("utf-8"),file_name=selected_indicator.lower().replace(" ","_").replace("₂","2")+"_world_bank_data.csv",mime="text/csv")

st.caption(f"Showing {len(df):,} observations for {len(selected_countries)} selected countries. Data source: World Bank Indicators API.")
