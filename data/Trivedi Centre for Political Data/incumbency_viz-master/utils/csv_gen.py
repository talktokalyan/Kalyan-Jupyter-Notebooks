import pandas as pd
import numpy as np
import json 
import os

ASSEMBLIES_PATH = "../incumbency/assets/assemblies.json"
OUT_FILES_FOLDER = "../incumbency/data"
TCPD_DATA_PATH = "/Users/shivam/Desktop/tcpd-data"

ASSEMBLIES = json.loads(open(ASSEMBLIES_PATH, 'r').read())
VALID_STATES = list(set([i['State_Name'] for i in ASSEMBLIES]))
election_type_to_assembly_type = {"VS" : "AE", "LS" : "GE"}
COLUMN_TYPE_INTEGERS = ['Year', 'Votes', 'Position', 'Margin', 'Age', 'Terms']
COLUMN_TYPE_FLOATS = ['Vote_Share_Percentage', 'Margin_Percentage']
BOOL_MAP_TMP = ['Incumbent', 'Turncoat']

def NOTA_indices(df):
    """
    This function takes a DataFrame and returns the index value of rows that belong to 'NOTA' candidate
    """

    filter_cand_nota = (
        df["Candidate"].str.strip().str.lower().isin(["nota", "none of the above"])
    )
    filter_party_nota = df["Party"].str.strip().str.lower() == "nota"

    filter_nota_rows = filter_cand_nota | filter_party_nota
    return filter_nota_rows

def downcast_to_int(df):
    """
        This is to create a diff-able version of the data files, to check the correctness of this script
    """
    tmp_df = df.copy()
    for column in COLUMN_TYPE_INTEGERS:
        if column in df.columns:
            tmp_df[column] = tmp_df[column].astype('Int64')

    for column in COLUMN_TYPE_FLOATS:
        if(column in tmp_df.columns):
            tmp_df[column] = tmp_df[column].astype(float).round(decimals = 2)
            float_to_int_rows = (np.modf(tmp_df[column])[0] == 0) # & (tmp_df[column] != "")
            
            # Note - this will not work if there are any np.inf values in the column
            # Below two lines are to debug in case we find inf values somewhere..
            # inf_rows = tmp_df[tmp_df[column].isin([np.inf, -np.inf])]
            # print(column)
            # print(inf_rows[TCPD_PRIMARY_KEY + ['Vote_Share_Percentage', 'ENOP', 'Votes', 'Valid_Votes']].to_markdown())


            tmp_df.loc[float_to_int_rows, column] = tmp_df.loc[float_to_int_rows, column].round(decimals = 0).astype("Int64").astype(str)
            tmp_df.loc[~float_to_int_rows, column] = tmp_df.loc[~float_to_int_rows, column].fillna("").astype(str)

    return tmp_df

def validate_assembly(tar_assembly):
    tar_state = tar_assembly['State_Name']
    election_type = election_type_to_assembly_type[tar_assembly['Assembly']]

    def print_debug_info():
        print(f"[DEBUG INFO] election_type: {election_type}, tar_state: {tar_state}")

    # 1. Validate election_type and tar_state
    # 1. a. Validate election_type
    if(election_type not in election_type_to_assembly_type.values()):
        print_debug_info()
        raise ValueError("election_type validation failed - invalid value passed")

    # 1. b. Validate tar_state (only required if election_type is AE)
    if(election_type == 'AE' and not (tar_state in VALID_STATES)):
        print_debug_info()
        raise ValueError("tar_state validation failed - invalid value passed")
    
    # Validation passed
    return (election_type, tar_state)

def create_assembly_data(tar_assembly):

    election_type, tar_state = validate_assembly(tar_assembly)

    keep_columns = [
        # Key for row
        "Assembly_No", "Poll_No", "Position", "State_Name", "Constituency_Name",
        "Year", "Constituency_Type", 

        # Candidate information for target election
        "Candidate", "pid", "Party", "Sex", "Candidate_Type",
        "Votes", "Vote_Share_Percentage", "Margin", "Margin_Percentage",
         
         # Candidate information for previous elections & political trajectory
        "Last_Party", "Contested", "No_Terms", 
        "Turncoat", "Incumbent", 
    ]
    optional_columns = ['Age', 'Alliance']

    # 2. Load relevant data file
    file_path_base = os.path.join(TCPD_DATA_PATH, election_type, "Data")
    if(election_type == 'AE'):
        file_path_base = os.path.join(file_path_base, tar_state)

    file_path = os.path.join(file_path_base, "derived", "mastersheet.csv")
    tar_df = pd.read_csv(file_path, low_memory=False)

    # 3. Subset on relevant data
    # 3. a. Keep only required columns
    optional_columns_available = [i for i in optional_columns if(i in tar_df.columns)]
    keep_columns += optional_columns_available
    tar_df = tar_df[keep_columns].copy()

    # 3. b. Remove NOTA rows
    NOTA_rows = NOTA_indices(tar_df)
    tar_df = tar_df[~NOTA_rows].copy()

    # Pre 4. Create auxillary winners column
    tar_df['aux_winner'] = tar_df['Position'] == 1

    # 4. Loop over all assemblies
    for i_assembly in tar_df['Assembly_No'].unique():
        tmp_df = tar_df[tar_df['Assembly_No'] <= i_assembly]
        winning_parties = tmp_df[tmp_df['aux_winner']]['Party'].unique()

        # 4. a. Keep only those PIDs which contested in this assembly (keep their rows from previous assemblies as well though)
        i_assembly_contestants = tmp_df[tmp_df['Assembly_No'] == i_assembly]['pid'].unique()
        tmp_df = tmp_df[tmp_df['pid'].isin(i_assembly_contestants)]

        # 4. b. Add variables:
        # 4. b. i. Terms (# of assemblies where this PID held Position == 1 in some (general or bye) election)
        terms_by_pid = (
            tmp_df[tmp_df['Position'] == 1]
            .drop_duplicates(subset = ['pid', 'Assembly_No'])
            .pivot_table(index = 'pid', values = 'Assembly_No', aggfunc = lambda x: len(x.unique()))
            .reset_index()
        )

        terms_by_pid.columns = ['pid', 'Terms']
        tmp_df = tmp_df.merge(
            terms_by_pid,
            how = 'left',
            on = 'pid',
            validate = 'm:1'
        )
        
        # 4. b. ii. Terms_Contested (# of assemblies where this PID contested)
        terms_contested_by_pid = (
            tmp_df
            .drop_duplicates(subset = ['pid', 'Assembly_No'])
            .pivot_table(index = 'pid', values = 'Assembly_No', aggfunc = lambda x: len(x.unique()))
            .reset_index()
        )

        terms_contested_by_pid.columns = ['pid', 'Terms_Contested']
        tmp_df = tmp_df.merge(
            terms_contested_by_pid,
            how = 'left',
            on = 'pid',
            validate = 'm:1',
            indicator = True
        )

        if(tmp_df['_merge'].value_counts()['both'] != len(tmp_df)):
            raise ValueError("terms_by_pid merge failed - some rows left unmerged")

        tmp_df = tmp_df.drop('_merge', axis = 'columns')

        # 4. c. Add variable: 'Contested'
        tmp_df['Contested'] = tmp_df['Contested'].astype("Int64")
        contested_by_pid = tmp_df.pivot_table(index = 'pid', values = 'Contested', aggfunc = 'max').to_dict()['Contested']
        tmp_df['Contested'] = tmp_df['pid'].map(contested_by_pid).astype("Int64")

        # 4. d. Deal with Dummy Positions
        dummy_indices = tmp_df['Position'] < 1
        tmp_df.loc[dummy_indices, 'Position'] = pd.NA

        OUT_FILE_PATH = os.path.join(OUT_FILES_FOLDER, f"{tar_assembly['File_Prefix']}-incumbency-{i_assembly}.csv")
        print(f"[GENERATED] ({election_type}) Assembly #{i_assembly} data for {tar_state}")

        # Temporary re-arrangement
        # out_cols = ["pid", "Assembly_No", "Poll_No", "Year", "Candidate","Candidate_Type", "State_Name", "Constituency_Name","Constituency_Type", "Party","Last_Party","Votes", "Sex", "Position", "Contested", "Turncoat", "Incumbent", "Vote_Share_Percentage", "Margin", "Margin_Percentage"]
        out_cols = "pid,Assembly_No,Poll_No,Year,Candidate,Candidate_Type,State_Name,Constituency_Name,Constituency_Type,Party,Last_Party,Votes,Sex,Position,Contested,Turncoat,Incumbent,Vote_Share_Percentage,Margin,Margin_Percentage,Age,Alliance,Terms,Terms_Contested".split(",")
        out_cols = [i for i in out_cols if(i in tmp_df.columns)]
        tmp_df = tmp_df[out_cols]
        tmp_df = tmp_df.sort_values(by = ['pid', 'Assembly_No', 'Year'])
        tmp_df = downcast_to_int(tmp_df)
        for column in BOOL_MAP_TMP:
            if(column in tmp_df.columns):
                tmp_df[column] = tmp_df[column].fillna("").astype("str").str.upper()

        tmp_df['Constituency_Name'] = tmp_df['Constituency_Name'].astype("str").str.strip()
        tmp_df.to_csv(OUT_FILE_PATH, index = False)

def create_party_file(tar_assembly):
    election_type, tar_state = validate_assembly(tar_assembly)

    # 2. Load relevant data file
    file_path_base = os.path.join(TCPD_DATA_PATH, election_type, "Data")
    if(election_type == 'AE'):
        file_path_base = os.path.join(file_path_base, tar_state)

    file_path = os.path.join(file_path_base, "derived", "lokdhaba", f"{election_type}_party_statistics.csv")
    tar_df = pd.read_csv(file_path, low_memory=False)
    tar_df = tar_df[['Party', 'Expanded_Party_Name']].dropna().drop_duplicates()
    OUT_FILE_PATH = os.path.join(OUT_FILES_FOLDER, f"{tar_assembly['File_Prefix']}-party-expanded.csv")
    tar_df.to_csv(OUT_FILE_PATH, index = False)


def main():
    for v_assembly in ASSEMBLIES:
        print("-" * 80)
        tar_el_type = election_type_to_assembly_type[v_assembly['Assembly']]
        tar_state = v_assembly['State_Name']
        print(f"[GENERATING ASSEMBLY DATA] ({tar_el_type}) {tar_state}")
        create_assembly_data(v_assembly)
        print(f"[GENERATING PARTY DATA] ({tar_el_type}) {tar_state}")
        create_party_file(v_assembly)

    
if __name__ == '__main__':
    main()