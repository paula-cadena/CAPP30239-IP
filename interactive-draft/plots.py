import altair as alt
import dash_vega_components as dvc
import pandas as pd
import panel as pn
from vega_datasets import data
alt.data_transformers.enable('vegafusion')
from clean import clean_total_stock, clean_estimates

def migration_flow(selected_year=2020):
    total_stock = clean_total_stock()
    total_stock.drop(total_stock[total_stock['Origin code'] == 2003].index, inplace=True)

    countries = pd.read_csv("/Users/paulacadena/Git-Hub/CAPP30239-IP/data/country-coord.csv")
    countries.rename(columns={"Latitude (average)":"latitude","Longitude (average)":"longitude"}, inplace = True)

    source = alt.topo_feature(data.world_110m.url, 'countries')

    select_country = alt.selection_point(
        on="pointerover", nearest=True, fields=["Destination code"], empty=False
    )

    lookup_data = alt.LookupData(
        countries, key="Numeric code", fields=["Country", "latitude", "longitude"]
    )

    background = alt.Chart(source).mark_geoshape(
        fill="lightgray",
        stroke="white"
    ).properties(
        width=750,
        height=500
    ).project('equalEarth')

    if selected_year:
        total_stock = total_stock[total_stock['Year'] == selected_year]

    connections = alt.Chart(total_stock).mark_rule(opacity=0.1).encode(
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

    points = alt.Chart(total_stock).mark_circle().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        size=alt.Size("Migrants:Q").legend(None).scale(range=[0, 1000]),
        order=alt.Order("Migrants:Q").sort("descending"),
        tooltip=["Country:N", "Migrants:Q"]
    ).transform_aggregate(
        Migrants="sum(Migration)",
        groupby=["Destination code"]
    ).transform_lookup(
        lookup="Destination code",
        from_=lookup_data
    ).add_params(
        select_country
    ).interactive()

    return (background + connections + points).configure_view(stroke=None)

def migration_rate():
    estimates = clean_estimates()
    highlight = alt.selection_point(on='pointerover', fields=['Subregion'], nearest=True)

    base = alt.Chart(estimates).encode(
        x=alt.X('Year:O', axis=alt.Axis(title="Year")),
        y=alt.Y('Net Migration Rate:Q', axis=alt.Axis(title="Net Migration Rate (per 1,000 population)")),
        color=alt.Color('Subregion:N', legend=alt.Legend(title="Subregion"))
    )

    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).add_params(
        highlight
    ).properties(
        width=600
    )

    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(1), alt.value(3))
    )

    return points + lines

dashboard = pn.Row(
    pn.Row(migration_flow(), migration_rate()),
)

dashboard.save("/Users/paulacadena/Git-Hub/CAPP30239-IP/www/index.html", embed=True)