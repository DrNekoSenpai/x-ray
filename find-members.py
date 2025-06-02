#!/usr/bin/env python3
"""
Script:    find_cwl_not_in_xray.py
Purpose:   Compare CWL responses against X-ray members and list CWL respondents
           whose In-Game Name does not appear in the X-ray members list.
Dependencies: pandas, openpyxl
Usage:     python find_cwl_not_in_xray.py
"""

import pandas as pd

def load_data(xray_path: str, cwl_path: str):
    """
    Load the two Excel files into pandas DataFrames.

    Args:
        xray_path (str): Path to xray-members.xlsx
        cwl_path  (str): Path to cwl-responses.xlsx

    Returns:
        xray_df (pd.DataFrame): DataFrame of X-ray members
        cwl_df  (pd.DataFrame): DataFrame of CWL responses
    """
    # Read the X-ray members workbook
    xray_df = pd.read_excel(xray_path, engine="openpyxl")
    
    # Read the CWL responses workbook
    cwl_df = pd.read_excel(cwl_path, engine="openpyxl")
    
    return xray_df, cwl_df

def find_missing_members(xray_df: pd.DataFrame, cwl_df: pd.DataFrame):
    """
    Identify CWL "In-Game Name" entries that are NOT present in X-ray "Name".

    Matching is done case-insensitively on the 'Name' column from X-ray members
    and the 'In-Game Name' column from CWL responses.

    Args:
        xray_df (pd.DataFrame): DataFrame of X-ray members (must have column 'Name')
        cwl_df  (pd.DataFrame): DataFrame of CWL responses (must have column 'In-Game Name')

    Returns:
        missing_names (set of str): Set of CWL In-Game Names not found in X-ray members
    """

    valid_xray = xray_df[
        xray_df["Clan"].notna() &
        xray_df["Clan"].astype(str).str.strip().ne("")
    ]

    xray_names = (
        valid_xray["Name"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )
    
    cwl_names = (
        cwl_df["In-Game Name"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
    )
    
    # Convert to Python sets for fast membership testing
    xray_name_set = set(xray_names)
    cwl_name_set  = set(cwl_names)
    
    # Find all CWL names that are not in X-ray member names
    missing_names = {name for name in cwl_name_set if name not in xray_name_set}
    
    return missing_names

def main():
    # --- CONFIGURE FILE PATHS HERE ---
    xray_path = "xray-members.xlsx"
    cwl_path  = "./inputs/cwl-responses.xlsx"
    # ---------------------------------
    
    # Load data
    try:
        xray_df, cwl_df = load_data(xray_path, cwl_path)
    except Exception as e:
        print(f"Error: Could not read one of the Excel files.\n{e}")
        return
    
    # Check that required columns exist
    if "Name" not in xray_df.columns:
        print("Error: 'Name' column not found in xray-members.xlsx")
        return
    if "In-Game Name" not in cwl_df.columns:
        print("Error: 'In-Game Name' column not found in cwl-responses.xlsx")
        return
    
    # Find CWL respondents not present in X-ray members
    missing = find_missing_members(xray_df, cwl_df)
    
    # Output the results
    if missing:
        print("CWL In-Game Names not found among X-ray members (case-insensitive):")
        for idx, name in enumerate(sorted(missing), 1):
            print(f"{idx}. {name}")
    else:
        print("All CWL In-Game Names are present in the X-ray members list.")
    
    # Optionally, save to a CSV for record-keeping
    # Uncomment below lines if you want to export the missing names to a file.
    # missing_df = pd.DataFrame({"Missing In-Game Name": sorted(missing)})
    # missing_df.to_csv("cwl_not_in_xray.csv", index=False)
    # print("Exported missing names to cwl_not_in_xray.csv")

if __name__ == "__main__":
    main()
