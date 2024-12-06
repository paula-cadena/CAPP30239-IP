from clean import countries_dict
from plots import migration_flow, migration_rate
import panel as pn
pn.extension('vega')

select = pn.widgets.Select(name='Year', options = [1990,1995,2000,2005,2010,2015,2020])
interactive_flow= pn.bind(migration_flow, selected_year=select)
dict_autocomplete = pn.widgets.AutocompleteInput(name='Search country', options=countries_dict(), case_sensitive = False)
dashboard = pn.Row(
    pn.Column(select, dict_autocomplete, interactive_flow, migration_rate())
)
dashboard.save("/Users/paulacadena/Git-Hub/CAPP30239-IP/www/index.html", embed=True)