import altair as alt
import pandas as pd
from vega_datasets import data
alt.data_transformers.enable('vegafusion')
from clean import clean_total_stock, clean_estimates

def migration_flow(selected_year=2020):
    total_stock = clean_total_stock()
    total_stock.drop(total_stock[total_stock['Origin code'] == 2003].index, inplace=True)

    countries = pd.read_csv("/Users/paulacadena/Git-Hub/CAPP30239-IP/data/country-coord.csv")
    countries.rename(columns={"Latitude (average)":"latitude", "Longitude (average)":"longitude"}, inplace=True)

    source = alt.topo_feature(data.world_110m.url, 'countries')

    select_country = alt.selection_point(
        on="pointerover", nearest=True, fields=["Destination code"], empty=False
    )

    lookup_data = alt.LookupData(
        countries, key="Numeric code", fields=["Country", "latitude", "longitude"]
    )

    total_stock_filtered = total_stock[total_stock['Year'] == selected_year]

    total_stock_aggregated = total_stock_filtered.groupby('Destination code', as_index=False).agg(
        Migrants=('Migration', 'sum')
    )

    background = alt.Chart(source).mark_geoshape(
        stroke="white"
    ).encode(
        color=alt.Color(
            'Migrants:Q',
            #scale=alt.Scale(scheme='blues'),
            legend=alt.Legend(title='Total Immigrants')
        )
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(total_stock_aggregated, key="Destination code", fields=["Migrants"])
    ).properties(
        width=1350,
        height=900
    ).project('equalEarth')

    connections = alt.Chart(total_stock_filtered).mark_rule(opacity=0.1).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        latitude2="lat2:Q",
        longitude2="lon2:Q"
    ).transform_lookup(
        lookup="Destination code",
        from_=lookup_data
    ).transform_lookup(
        lookup="Origin code",
        from_=lookup_data,
        as_=["Country", "lat2", "lon2"]
    ).transform_filter(
        select_country
    )

    points = alt.Chart(total_stock_filtered).mark_circle(size=0).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        order=alt.Order("Immigrants:Q").sort("descending"),
        tooltip=[alt.Tooltip("Country:N"), alt.Tooltip("Immigrants:Q", format=",")]
    ).transform_aggregate(
        Immigrants="sum(Migration)",
        groupby=["Destination code"]
    ).transform_lookup(
        lookup="Destination code",
        from_=lookup_data
    ).add_params(
        select_country
    ).interactive()

    return (background + connections + points).to_dict(format="vega")

def migration_rate():
    estimates = clean_estimates()
    selection = alt.selection_point(fields=['Subregion'], bind='legend')

    base = alt.Chart(estimates).encode(
        x=alt.X('Year:O', axis=alt.Axis(title="Year")),
        y=alt.Y('Net Migration Rate:Q', axis=alt.Axis(title="Net Migration Rate (per 1,000 population)")),
        color=alt.Color('Subregion:N', legend=alt.Legend(title="Subregion"))
    )

    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).properties(
        width=600
    )

    lines = base.mark_line().encode(
        size=alt.condition(~selection, alt.value(1), alt.value(3))
    ).add_params(selection)

    return (points + lines).to_dict(format="vega")
