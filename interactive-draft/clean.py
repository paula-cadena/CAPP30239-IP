import pandas as pd
import numpy as np
import csv

countries_data = "/Users/paulacadena/Git-Hub/CAPP30239-IP//data/country-coord.csv"
def clean_total_stock():
    #Data frame
    total_stock = pd.read_excel("/Users/paulacadena/Git-Hub/CAPP30239-IP/data/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx", 
                                sheet_name="Table 1", skiprows=10, header=0)
    total_stock=total_stock.iloc[:, 1:]

    # Correctly name missing values
    total_stock.replace('..', np.nan, inplace=True)

    #Rename columns
    total_stock.rename(columns={"Region, development group, country or area of destination":"Destination",
                                "Location code of destination":"Destination code",
                                "Region, development group, country or area of origin": "Origin",
                                "Location code of origin":"Origin code"}, inplace =True)

    #Keep only countries for destination and origin (original data frame has aggregations)
    countries = pd.read_csv(countries_data)
    #1. Destination
    total_stock['M1']=total_stock["Destination code"].isin(countries["Numeric code"])
    #2. Origin
    total_stock['M2']=total_stock["Origin code"].isin(countries["Numeric code"]) | (total_stock['Origin code'] == 2003)
    #3. Keep only if both are countries
    total_stock = total_stock[total_stock['M1'] & total_stock['M2']].copy()
    
    #Keep only neccesary columns
    total_stock = total_stock[["Destination","Destination code","Origin",
                               "Origin code",1990,1995,2000,2005,2010,2015,2020]]
    
    #Transform from wide to long
    year_columns = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    total_stock = pd.melt(total_stock,
                          id_vars=[col for col in total_stock.columns if col not in year_columns],
                          value_vars=year_columns,
                          var_name='Year',
                          value_name='Migration')

    # Change Value column to numeric
    total_stock['Migration'] = pd.to_numeric(total_stock['Migration'], errors='coerce')

    return total_stock

def clean_estimates():
    # Data frame
    estimates = pd.read_excel("/Users/paulacadena/Git-Hub/CAPP30239-IP/data/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx", 
                                sheet_name="Estimates", skiprows=16, header=0)

    # Correctly name missing values
    estimates.replace('..', np.nan, inplace=True)

    # Keep only subregions
    subregion_codes = [1834,1833,1831,1832,1830,1835,1836,1829]
    estimates = estimates[estimates['Location code'].isin(subregion_codes)]
    
    # Keep only neccesary columns and rename them
    estimates = estimates[["Region, subregion, country or area *","Year","Net Migration Rate (per 1,000 population)"]]

    estimates.rename(
        columns={
            "Region, subregion, country or area *": "Subregion",
            "Net Migration Rate (per 1,000 population)": "Net Migration Rate"
        }, inplace=True
    )
    return estimates

def countries_dict():
    country_dict = {}
    with open(countries_data, mode='r') as file:
        reader = csv.DictReader(file)
        country_dict = {row['Country']: row['Numeric code'] for row in reader}
    return country_dict