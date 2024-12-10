from clean import countries_dict
from plots import migration_flow, migration_rate
import panel as pn

pn.extension("vega")

# Plots Country Page + Widgets
select = pn.widgets.Select(
    name="Year", options=[1990, 1995, 2000, 2005, 2010, 2015, 2020]
)
interactive_flow = pn.bind(migration_flow, selected_year=select)

plots_country = pn.Column(select, interactive_flow)

plots_country.save(
    "/Users/paulacadena/Git-Hub/CAPP30239-IP/www/plots_country.html", embed=True
)

# Plots Region Page + Widgets

interactive_plot = pn.bind(migration_rate, selected_year=select)
select_row = pn.Row(pn.Spacer(width=800), select, sizing_mode="stretch_width")
plots_region = pn.Column(select_row, interactive_plot)

plots_region.save(
    "/Users/paulacadena/Git-Hub/CAPP30239-IP/www/plots_region.html", embed=True
)
