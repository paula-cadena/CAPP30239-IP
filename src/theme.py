import altair as alt

def custom_theme():
    return {
        "config": {
            "title": {
                "fontSize": 20,          # Size of plot titles
                "font": "Montserrat",    # Font for titles (matches CSS)
                "anchor": "start",       # Align title to the start
                "color": "#002E2C"       # Header color
            },
            "axis": {
                "labelFontSize": 12,     # Size of axis labels
                "titleFontSize": 14,     # Size of axis titles
                "labelFont": "Montserrat", # Font for axis labels
                "titleFont": "Montserrat", # Font for axis titles
                "labelColor": "#035E7B",   # Axis label color
                "titleColor": "#035E7B"    # Axis title color
            },
            "legend": {
                "labelFontSize": 12,      # Size of legend labels
                "titleFontSize": 14,      # Size of legend title
                "labelFont": "Montserrat", # Font for legend labels
                "titleFont": "Montserrat", # Font for legend title
                "labelColor": "#035E7B",   # Legend label color
                "titleColor": "#035E7B"    # Legend title color
            },
            "view": {
                "width": 600,             # Default chart width
                "height": 400,            # Default chart height
                "background": "#FFF9FB"   # Match background color
            },
            "range": {
                "category": [
                    "#c9e4caff", "#87bba2ff", "#55828bff", "#3b6064ff", 
                    "#364958ff", "#dc965aff", "#632b30ff", "#bc9cb0ff",
                    "#1c1c1cff", "#e4572eff"
                ],                        # New custom palette
                "diverging": [
                    "#e4572eff", "#dc965aff", "#87bba2ff", "#55828bff", 
                    "#3b6064ff", "#1c1c1cff"
                ],                        # Diverging scheme
                "heatmap": [
                    "#1c1c1cff", "#364958ff", "#3b6064ff", "#55828bff",
                    "#87bba2ff", "#c9e4caff"
                ],                        # Heatmap gradient
                "ordinal": [
                    "#632b30ff", "#bc9cb0ff", "#87bba2ff", "#e4572eff"
                ]                         # Ordinal scheme
            },

            "background": "#FFF9FB",      # Set overall background color
        }
    }

alt.themes.register("custom_theme", custom_theme)
alt.themes.enable("custom_theme")
