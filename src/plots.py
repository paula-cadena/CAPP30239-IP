import altair as alt
import pandas as pd
from vega_datasets import data

alt.data_transformers.enable("vegafusion")
from clean import clean_total_stock, clean_estimates, clean_region_stock
from theme import custom_theme

alt.themes.register("custom_theme", custom_theme)
alt.themes.enable("custom_theme")


def migration_flow(selected_year=1990):
    """
    Generates an interactive Altair visualization for migration flow in a selected year.

    This function creates:
    - A world map showing total immigrants for each destination country.
    - Connection lines indicating migration flows from origin to destination countries.
    - A bar chart highlighting the top 5 origin countries for a selected destination country.

    Args:
        selected_year (int): The year to filter migration data. Defaults to 1990.

    Returns:
        dict: The Altair chart specification in Vega format.

    """
    # Load data and filter for map
    total_stock = clean_total_stock()
    total_stock.drop(
        total_stock[total_stock["Origin code"] == 2003].index, inplace=True
    )
    countries = pd.read_csv(
        "/Users/paulacadena/Git-Hub/CAPP30239-IP/data/country-coord.csv"
    )
    countries.rename(
        columns={"Latitude (average)": "latitude", "Longitude (average)": "longitude"},
        inplace=True,
    )

    source = alt.topo_feature(data.world_110m.url, "countries")

    select_country = alt.selection_point(
        on="pointerover", nearest=True, fields=["Destination code"], empty=False
    )

    lookup_data = alt.LookupData(
        countries, key="Numeric code", fields=["Country", "latitude", "longitude"]
    )

    total_stock_filtered = total_stock[total_stock["Year"] == selected_year]

    total_stock_aggregated = total_stock_filtered.groupby(
        "Destination code", as_index=False
    ).agg(Migrants=("Migration", "sum"))

    # Background map
    background = (
        alt.Chart(source)
        .mark_geoshape(stroke="white")
        .encode(
            color=alt.Color("Migrants:Q", legend=alt.Legend(title="Total Immigrants"))
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                total_stock_aggregated, key="Destination code", fields=["Migrants"]
            ),
        )
        .properties(width=800, height=450)
        .project("equalEarth")
    )

    # Lines that connect destination to origin
    connections = (
        alt.Chart(total_stock_filtered)
        .mark_rule(opacity=0.4, color="#aa4a52")
        .encode(
            latitude="latitude:Q",
            longitude="longitude:Q",
            latitude2="lat2:Q",
            longitude2="lon2:Q",
        )
        .transform_lookup(lookup="Destination code", from_=lookup_data)
        .transform_lookup(
            lookup="Origin code", from_=lookup_data, as_=["Country", "lat2", "lon2"]
        )
        .transform_filter(select_country)
    )
    # Points to center the connections
    points = (
        alt.Chart(total_stock_filtered)
        .mark_circle(size=0)
        .encode(
            latitude="latitude:Q",
            longitude="longitude:Q",
            order=alt.Order("Immigrants:Q").sort("descending"),
            tooltip=[alt.Tooltip("Country:N"), alt.Tooltip("Immigrants:Q", format=",")],
        )
        .transform_aggregate(Immigrants="sum(Migration)", groupby=["Destination code"])
        .transform_lookup(lookup="Destination code", from_=lookup_data)
        .add_params(select_country)
        .interactive()
    )

    # Additional filter for bars chart
    top_countries = (
        total_stock_filtered.groupby(["Origin code", "Destination code"])
        .agg(Immigrants=("Migration", "sum"))
        .reset_index()
    )

    top_countries_aggregated = (
        top_countries.groupby("Destination code")
        .apply(lambda x: x.nlargest(5, "Immigrants"))
        .reset_index(drop=True)
    )

    top_countries_aggregated = top_countries_aggregated.merge(
        countries[["Numeric code", "Country"]],
        left_on="Origin code",
        right_on="Numeric code",
        how="left",
    )

    # Bars chart with top 5 origin countries by destination
    bars = (
        alt.Chart(top_countries_aggregated)
        .mark_bar()
        .encode(
            x=alt.X("Immigrants:Q", title="Total Immigrants"),
            y=alt.Y("Country:N", title="Origin Country", axis=alt.Axis(labelLimit=150)),
            color=alt.Color("Country:N", legend=None),
        )
        .transform_filter(select_country)
        .properties(width=500, height=350)
    )

    return (background + connections + points | bars).to_dict(format="vega")


def migration_rate(selected_year=1990):
    """
    Generates an interactive visualization for migration rates and immigration data by subregion.

    This function creates:
    - A line chart showing the net migration rate over time for different subregions.
    - A bar chart displaying immigration values for a selected subregion in a specific year.

    Args:
        selected_year (int): The year to filter immigration data for the bar chart. Defaults to 1990.

    Returns:
        dict: The Altair chart specification in Vega format.

    """
    # Load and filter data
    estimates = clean_estimates()
    region_stock = clean_region_stock()
    region_stock = region_stock[region_stock["Year"] == selected_year]

    selection = alt.selection_point(fields=["Subregion"], bind="legend")

    # Base chart for migration rate over time
    base = alt.Chart(estimates).encode(
        x=alt.X("Year:O", axis=alt.Axis(title="Year", tickCount=14)),
        y=alt.Y(
            "Net Migration Rate:Q",
            axis=alt.Axis(title="Net Migration Rate (per 1,000 population)"),
        ),
        color=alt.Color("Subregion:N", legend=alt.Legend(title="Subregion")),
    )
    # Overlay points on lines for better interactivity
    points = (
        base.mark_circle()
        .encode(opacity=alt.value(0))
        .properties(width=660, height=350)
    )
    # Line chart for migration rates
    lines = (
        base.mark_line()
        .encode(size=alt.condition(~selection, alt.value(1), alt.value(3)))
        .add_params(selection)
    )

    # Bar chart for migration data by subregion
    bars = (
        alt.Chart(region_stock)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", axis=alt.Axis(title="Immigration", tickCount=5)),
            y=alt.Y("source:N", axis=alt.Axis(title="Destination Subregion")),
            color=alt.Color("Subregion:N"),
        )
        .transform_filter(selection)
        .properties(width=340, height=350)
    )
    return (points + lines | bars).to_dict(format="vega")
