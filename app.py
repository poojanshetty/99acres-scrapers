"""Interactive dashboard for the 99acres Bengaluru properties dataset.

Run with: streamlit run app.py
"""

from __future__ import annotations

import re

import pandas as pd
import plotly.express as px
import streamlit as st

from main import cleaned_dataset_file


st.set_page_config(page_title="Bengaluru Property Analytics", page_icon="🏠", layout="wide")


def format_price(lakhs: float) -> str:
    """Show a price in both commonly used Indian real-estate units."""
    return f"₹{lakhs:,.1f} Lakhs / ₹{lakhs / 100:,.2f} Cr"


@st.cache_data(show_spinner=False)
def read_properties(uploaded_file=None) -> pd.DataFrame:
    """Read a cleaned export, or the Kaggle file cached by the notebook."""
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
    else:
        # Prefer the final dataset created in the notebook, including ratings.
        local_csv = "notebooks/bengaluru_properties_cleaned_with_ratings.csv"
        try:
            data = pd.read_csv(local_csv)
        except FileNotFoundError:
            # main.py owns the Kaggle download/cache logic.
            data = pd.read_excel(cleaned_dataset_file())

    return clean_properties(data)


def clean_properties(data: pd.DataFrame) -> pd.DataFrame:
    """Normalise both the notebook's cleaned export and raw scraped data."""
    data = data.copy()
    data.columns = [str(column).strip().lower() for column in data.columns]

    if "price" in data and "price_lakhs" not in data:
        price = data["price"].astype(str).str.replace(",", "", regex=False)
        values = pd.to_numeric(price.str.extract(r"([\d.]+)")[0], errors="coerce")
        data["price_lakhs"] = values.where(~price.str.contains("Cr", case=False, na=False), values * 100)
    if "area" in data and "area_sqft" not in data:
        data["area_sqft"] = pd.to_numeric(
            data["area"].astype(str).str.replace(",", "", regex=False).str.extract(r"([\d.]+)")[0],
            errors="coerce",
        )
    if "bhk" in data:
        data["bhk"] = pd.to_numeric(data["bhk"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    if "name" in data:
        # Raw names carry a rating on a separate line; a missing match stays null.
        if "ratings" not in data:
            data["ratings"] = pd.to_numeric(
                data["name"].astype(str).str.extract(r"\n\s*(\d(?:\.\d+)?)\s*$")[0], errors="coerce"
            )
        else:
            data["ratings"] = pd.to_numeric(data["ratings"], errors="coerce")
        data["name"] = data["name"].astype(str).str.replace(r"\n\s*\d(?:\.\d+)?\s*$", "", regex=True).str.strip()
    required = ["name", "location", "price_lakhs", "area_sqft", "bhk"]
    for column in required:
        if column not in data:
            data[column] = pd.NA
    data["price_lakhs"] = pd.to_numeric(data["price_lakhs"], errors="coerce")
    data["area_sqft"] = pd.to_numeric(data["area_sqft"], errors="coerce")
    data["bhk"] = pd.to_numeric(data["bhk"], errors="coerce")
    return data.dropna(subset=["name", "location", "price_lakhs", "area_sqft", "bhk"])


st.title("🏠 Bengaluru Property Analytics Dashboard")
st.caption("Analyse 99acres listings by location, budget, size, BHK configuration, and value.")

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

data = read_properties(uploaded_file)
if data.empty:
    st.info("Upload the cleaned 99acres Excel/CSV file to start exploring listings.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search name or location")
    locations = sorted(data["location"].dropna().unique())
    selected_locations = st.multiselect("Location", locations)
    bhk_options = sorted(data["bhk"].dropna().astype(int).unique())
    selected_bhk = st.multiselect("BHK", bhk_options)

    price_min, price_max = map(float, (data["price_lakhs"].min(), data["price_lakhs"].max()))
    price_range = st.slider("Budget (₹ lakhs)", price_min, price_max, (price_min, price_max))
    sort_option = st.selectbox(
        "Sort listings",
        ["Price: low to high", "Area: low to high", "Price: high to low", "Area: high to low"],
    )

filtered = data.copy()
if search:
    pattern = re.escape(search)
    filtered = filtered[filtered["name"].str.contains(pattern, case=False, na=False) | filtered["location"].str.contains(pattern, case=False, na=False)]
if selected_locations:
    filtered = filtered[filtered["location"].isin(selected_locations)]
if selected_bhk:
    filtered = filtered[filtered["bhk"].isin(selected_bhk)]
filtered = filtered[filtered["price_lakhs"].between(*price_range)]
filtered["price_per_sqft"] = (filtered["price_lakhs"] * 100_000 / filtered["area_sqft"]).round()

sort_columns = {
    "Price: low to high": ("price_lakhs", True),
    "Area: low to high": ("area_sqft", True),
    "Price: high to low": ("price_lakhs", False),
    "Area: high to low": ("area_sqft", False),
}
sort_column, sort_ascending = sort_columns[sort_option]
filtered = filtered.sort_values(sort_column, ascending=sort_ascending)

left, middle, right = st.columns(3)
left.metric("Listings", f"{len(filtered):,}")
median_price = filtered["price_lakhs"].median()
middle.metric("Median price", f"₹{median_price:,.1f} Lakhs" if len(filtered) else "—")
if len(filtered):
    middle.caption(f"≈ ₹{median_price / 100:,.2f} Cr")
right.metric("Median area", f"{filtered['area_sqft'].median():,.0f} sqft" if len(filtered) else "—")

if filtered.empty:
    st.warning("No listings match these filters. Try widening the budget or clearing a filter.")
    st.stop()

st.subheader("Market insights")
location_market = (
    filtered.groupby("location", as_index=False)
    .agg(
        listings=("name", "size"),
        median_price_lakhs=("price_lakhs", "median"),
        median_price_per_sqft=("price_per_sqft", "median"),
    )
)
top_location = location_market.loc[location_market["listings"].idxmax()]
largest_listing = filtered.loc[filtered["area_sqft"].idxmax()]
lowest_listing = filtered.loc[filtered["price_lakhs"].idxmin()]

# A value score compares a listing with the typical price per sqft in its location.
# Locations with fewer than five visible listings are excluded from this benchmark.
benchmarks = location_market[location_market["listings"] >= 5]
value_listings = filtered.merge(
    benchmarks[["location", "median_price_per_sqft"]], on="location", how="inner"
)
if not value_listings.empty:
    value_listings["value_score"] = (
        value_listings["median_price_per_sqft"] / value_listings["price_per_sqft"] * 100
    )
    best_value_listing = value_listings.loc[value_listings["value_score"].idxmax()]

insight_one, insight_two, insight_three, insight_four = st.columns(4)
insight_one.metric("Top location", top_location["location"].title())
insight_one.caption(f"{int(top_location['listings'])} listings in this view")
insight_two.metric("Lowest-price listing", format_price(lowest_listing["price_lakhs"]))
insight_two.caption(f"{lowest_listing['name']} · {lowest_listing['location']}")
insight_three.metric("Largest listing", f"{largest_listing['area_sqft']:,.0f} sqft")
insight_three.caption(f"{largest_listing['name']} · {format_price(largest_listing['price_lakhs'])}")
if not value_listings.empty:
    insight_four.metric("Best local value", f"{best_value_listing['value_score']:.0f} score")
    insight_four.caption(f"{best_value_listing['name']} · ₹{best_value_listing['price_per_sqft']:,.0f}/sqft")
else:
    insight_four.metric("Best local value", "Need 5+ listings")
    insight_four.caption("Widen the filters to compare a location benchmark.")

with st.expander("How is the local value score calculated?"):
    st.write(
        "The score compares a property's price per sqft with the median price per sqft "
        "for the same location. A score above 100 means the listing is less expensive "
        "than the local median. It is a comparison tool, not a valuation or investment recommendation."
    )

chart_left, chart_right = st.columns(2)
with chart_left:
    by_bhk = filtered.groupby("bhk", as_index=False).agg(listings=("name", "size"), median_price=("price_lakhs", "median"))
    fig = px.bar(by_bhk, x="bhk", y="listings", color="median_price", color_continuous_scale="Teal", title="Listings by BHK")
    fig.update_layout(xaxis_title="BHK", yaxis_title="Listings", coloraxis_colorbar_title="Median ₹L")
    st.plotly_chart(fig, use_container_width=True)
with chart_right:
    top_locations = filtered["location"].value_counts().head(10).sort_values()
    fig = px.bar(top_locations, orientation="h", title="Most represented locations")
    fig.update_layout(xaxis_title="Listings", yaxis_title=None, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    filtered,
    x="area_sqft",
    y="price_lakhs",
    color="bhk",
    size="price_lakhs",
    hover_name="name",
    hover_data={"location": True, "price_per_sqft": ":,.0f", "area_sqft": ":,.0f", "price_lakhs": ".1f"},
    title="Price vs. area",
    labels={"area_sqft": "Area (sqft)", "price_lakhs": "Price (₹ lakhs)", "bhk": "BHK"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Listings")
table_columns = ["name", "location", "price", "area_sqft", "bhk", "price_per_sqft"]
table_data = filtered.assign(price=filtered["price_lakhs"].map(format_price))
st.dataframe(
    table_data[table_columns].rename(
        columns={
            "price": "price",
            "area_sqft": "area (sqft)",
            "price_per_sqft": "price / sqft (₹)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
st.download_button(
    "Download filtered listings as CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    "filtered_99acres_listings.csv",
    "text/csv",
)
