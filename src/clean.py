import pandas as pd
import numpy as np
import csv

countries_data = "/Users/paulacadena/Git-Hub/CAPP30239-IP/data/country-coord.csv"
stock_data = "/Users/paulacadena/Git-Hub/CAPP30239-IP/data/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx"
estimates_data = "/Users/paulacadena/Git-Hub/CAPP30239-IP/data/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx"


def clean_total_stock():
    """
    Cleans and transforms migration stock data from wide to long format.

    The function performs the following steps:
    1. Reads the migration stock data from an Excel file (sheet "Table 1") while skipping initial rows.
    2. Replaces placeholder values (e.g., "..") with NaN for proper data handling.
    3. Renames columns for better readability and consistency.
    4. Filters the data to retain rows where both the destination and origin are countries, using a reference CSV file.
    5. Keeps only the necessary columns for analysis.
    6. Transforms the data from wide format (with years as columns) to long format (with years as rows).
    7. Converts the 'Migration' column to numeric, coercing invalid values to NaN.

    Returns:
        pd.DataFrame: A cleaned and transformed DataFrame containing the migration stock data.
                      The output includes the columns 'Destination', 'Destination code', 'Origin',
                      'Origin code', 'Year', and 'Migration'.
    """
    # Data frame
    total_stock = pd.read_excel(stock_data, sheet_name="Table 1", skiprows=10, header=0)
    total_stock = total_stock.iloc[:, 1:]

    # Correctly name missing values
    total_stock.replace("..", np.nan, inplace=True)

    # Rename columns
    total_stock.rename(
        columns={
            "Region, development group, country or area of destination": "Destination",
            "Location code of destination": "Destination code",
            "Region, development group, country or area of origin": "Origin",
            "Location code of origin": "Origin code",
        },
        inplace=True,
    )

    # Keep only countries for destination and origin (original data frame has aggregations)
    countries = pd.read_csv(countries_data)
    # 1. Destination
    total_stock["M1"] = total_stock["Destination code"].isin(countries["Numeric code"])
    # 2. Origin
    total_stock["M2"] = total_stock["Origin code"].isin(countries["Numeric code"]) | (
        total_stock["Origin code"] == 2003
    )
    # 3. Keep only if both are countries
    total_stock = total_stock[total_stock["M1"] & total_stock["M2"]].copy()

    # Keep only neccesary columns
    total_stock = total_stock[
        [
            "Destination",
            "Destination code",
            "Origin",
            "Origin code",
            1990,
            1995,
            2000,
            2005,
            2010,
            2015,
            2020,
        ]
    ]

    # Transform from wide to long
    year_columns = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    total_stock = pd.melt(
        total_stock,
        id_vars=[col for col in total_stock.columns if col not in year_columns],
        value_vars=year_columns,
        var_name="Year",
        value_name="Migration",
    )

    # Change Value column to numeric
    total_stock["Migration"] = pd.to_numeric(total_stock["Migration"], errors="coerce")

    return total_stock


def clean_estimates():
    """
    Cleans and filters migration rate estimates for specific subregions.

    The function performs the following steps:
    1. Reads migration estimates data from an Excel file (sheet "Estimates") while skipping initial rows.
    2. Replaces placeholder values (e.g., "..") with NaN for proper data handling.
    3. Filters the data to retain only rows corresponding to specified subregion codes.
    4. Keeps only necessary columns for analysis and renames them for clarity.

    Returns:
        pd.DataFrame: A cleaned DataFrame containing net migration rate estimates by subregion and year.
                      The output includes the columns 'Subregion', 'Year', and 'Net Migration Rate'.
    """
    # Data frame
    estimates = pd.read_excel(
        estimates_data, sheet_name="Estimates", skiprows=16, header=0
    )

    # Correctly name missing values
    estimates.replace("..", np.nan, inplace=True)

    # Keep only subregions
    subregion_codes = [1834, 1833, 1831, 1832, 1830, 1835, 1836, 1829]
    estimates = estimates[estimates["Location code"].isin(subregion_codes)]

    # Keep only neccesary columns and rename them
    estimates = estimates[
        [
            "Region, subregion, country or area *",
            "Year",
            "Net Migration Rate (per 1,000 population)",
        ]
    ]

    estimates.rename(
        columns={
            "Region, subregion, country or area *": "Subregion",
            "Net Migration Rate (per 1,000 population)": "Net Migration Rate",
        },
        inplace=True,
    )
    return estimates


def clean_region_stock():
    """
    Cleans and transforms regional migration stock data from wide to long format.

    The function performs the following steps:
    1. Reads migration stock data from an Excel file (sheet "Table 1") while skipping initial rows.
    2. Replaces placeholder values (e.g., "..") with NaN for proper data handling.
    3. Renames columns for consistency and readability.
    4. Filters the data to include only rows where both destination and origin are specified subregions.
    5. Keeps only the necessary columns for analysis.
    6. Transforms the data from wide format (with years as columns) to long format (with years as rows).
    7. Performs additional transformations to standardize subregion names and ensures numeric consistency for migration values.

    Returns:
        pd.DataFrame: A cleaned and transformed DataFrame containing the regional migration stock data.
                      The output includes the columns 'Subregion', 'source', 'Year', and 'value'.
    """
    # Data frame
    total_stock = pd.read_excel(stock_data, sheet_name="Table 1", skiprows=10, header=0)
    # Correctly name missing values
    total_stock.replace("..", np.nan, inplace=True)
    # Rename columns
    total_stock.rename(
        columns={
            "Region, development group, country or area of destination": "Subregion",
            "Location code of destination": "Destination code",
            "Region, development group, country or area of origin": "source",
            "Location code of origin": "Origin code",
        },
        inplace=True,
    )
    # Keep only subregions
    subregion_codes = [947, 921, 927, 1834, 1833, 1831, 1832, 1830, 1835, 1836, 1829]
    region_stock = total_stock[
        total_stock["Destination code"].isin(subregion_codes)
        & total_stock["Origin code"].isin(subregion_codes)
    ]
    region_stock = region_stock[
        ["Subregion", "source", 1990, 1995, 2000, 2005, 2010, 2015, 2020]
    ]
    # Transform from wide to long
    year_columns = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    region_stock = pd.melt(
        region_stock,
        id_vars=[col for col in region_stock.columns if col not in year_columns],
        value_vars=year_columns,
        var_name="Year",
        value_name="value",
    )
    # Transformations to unify with estimates
    region_stock["Subregion"] = region_stock["Subregion"].str.strip()
    region_stock["Subregion"] = region_stock["Subregion"].replace(
        {"Australia and New Zealand": "Australia/New Zealand"}
    )
    region_stock["value"] = pd.to_numeric(region_stock["value"], errors="coerce")

    return region_stock


def clean_sex_stock():
    """
    Cleans and transforms migration stock data by sex from wide to long format.

    The function performs the following steps:
    1. Reads migration stock data from an Excel file (sheet "Table 1") while skipping initial rows.
    2. Replaces placeholder values (e.g., "..") with NaN for proper data handling.
    3. Renames columns for consistency and readability.
    4. Filters the data to include only rows where both destination and origin are countries.
    5. Transforms the data into a long format, separating the migration data by year and sex.
    6. Extracts and standardizes the year and sex information from column names.

    Returns:
        pd.DataFrame: A cleaned and transformed DataFrame containing the migration stock data by sex.
                      The output includes the columns 'Destination', 'Destination code', 'Origin',
                      'Origin code', 'Year', 'Sex', and 'Migration'.
    """
    # Data frame
    total_stock = pd.read_excel(stock_data, sheet_name="Table 1", skiprows=10, header=0)
    # Correctly name missing values
    total_stock.replace("..", np.nan, inplace=True)
    # Rename columns
    total_stock.rename(
        columns={
            "Region, development group, country or area of destination": "Destination",
            "Location code of destination": "Destination code",
            "Region, development group, country or area of origin": "Origin",
            "Location code of origin": "Origin code",
        },
        inplace=True,
    )
    # Keep only countries for destination and origin (original data frame has aggregations)
    countries = pd.read_csv(countries_data)
    # 1. Destination
    total_stock["M1"] = total_stock["Destination code"].isin(countries["Numeric code"])
    # 2. Origin
    total_stock["M2"] = total_stock["Origin code"].isin(countries["Numeric code"]) | (
        total_stock["Origin code"] == 2003
    )
    # 3. Keep only if both are countries
    total_stock = total_stock[total_stock["M1"] & total_stock["M2"]].copy()
    # Transform from wide to long
    sex_stock = total_stock[
        [
            "Destination",
            "Destination code",
            "Origin",
            "Origin code",
            "1990.1",
            "1995.1",
            "2000.1",
            "2005.1",
            "2010.1",
            "2015.1",
            "2020.1",
            "1990.2",
            "1995.2",
            "2000.2",
            "2005.2",
            "2010.2",
            "2015.2",
            "2020.2",
        ]
    ]

    sex_stock_long = pd.melt(
        sex_stock,
        id_vars=["Destination", "Destination code", "Origin", "Origin code"],
        var_name="Year_Sex",
        value_name="Migration",
    )
    # Transformations to identify sex and year based on the previous column
    sex_stock_long["Year"] = sex_stock_long["Year_Sex"].str[:-2].astype(int)
    sex_stock_long["Sex"] = sex_stock_long["Year_Sex"].str[-1]
    sex_stock_long["Sex"] = sex_stock_long["Sex"].replace({"1": "Male", "2": "Female"})
    sex_stock_long = sex_stock_long.drop("Year_Sex", axis=1)

    return sex_stock_long


def countries_dict():
    """
    Creates a dictionary mapping country names to their numeric codes.

    This function reads a CSV file containing country names and their corresponding numeric codes,
    and returns a dictionary where the keys are country names and the values are their numeric codes.

    Returns:
        dict: A dictionary with country names as keys and numeric codes as values.
    """
    country_dict = {}
    with open(countries_data, mode="r") as file:
        reader = csv.DictReader(file)
        country_dict = {row["Country"]: row["Numeric code"] for row in reader}
    return country_dict
