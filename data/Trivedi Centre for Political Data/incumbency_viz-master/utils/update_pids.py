# This script updates two things:
# 1. {state_code}-pids.csv files in assets/*
# 2. data/assemblies.json

import pandas as pd
import os
import json


ASSEMBLIES_PATH = "../incumbency/assets/assemblies.json"
PID_FILES_FOLDER = "../incumbency/data"
TCPD_DATA_PATH = "/Users/shivam/Desktop/tcpd-data"

assemblies = json.loads(open(ASSEMBLIES_PATH, 'r').read())

GE_values = {
    "Min" : -1,
    "Max" : -1
}

def get_PID_img_df(primary_df):
    output_df = pd.DataFrame()
    all_empty_images = (sum(primary_df['Candidate_Image_Link'].isna()) == len(primary_df))

    if(all_empty_images):
        output_df = pd.DataFrame({
            'pid' : [],
            'link' : []
        })

    else:
        output_df = primary_df[['pid', 'Candidate_Image_Link']].drop_duplicates().dropna()
        output_df = output_df.drop_duplicates(subset = 'pid')
        output_df.columns = ['pid', 'link']

    return output_df

def main():
    GE_updated = False
    for idx, i in enumerate(assemblies):

        # For Vidhan Sabha
        if(i['Assembly'] == 'VS'):
            primary_file_path = os.path.join(TCPD_DATA_PATH, "AE", "Data", i['State_Name'], "primary", "candidates_electoral_info.csv")
            state_df = pd.read_csv(primary_file_path, low_memory=False)
            if('Candidate_Image_Link' not in state_df.columns):
                state_df['Candidate_Image_Link'] = pd.NA

            # The max(1, ...) exists because some states also have Assembly_No = 0 rows
            # These were added to calculate incumbency correctly for states that were formed out of other states
            # We plan to eventually re-do this, but until then...
            assemblies[idx]['Min_Assembly'] = max(1, int(state_df['Assembly_No'].min()))
            assemblies[idx]['Max_Assembly'] = int(state_df['Assembly_No'].max())

            output_df = get_PID_img_df(state_df)

            output_file_name = f"{i['File_Prefix']}-pids.csv"
            output_file_path = os.path.join(PID_FILES_FOLDER, output_file_name)
            output_df.to_csv(output_file_path, index = False)
                
            print(f"[DONE] Updated PIDs for state: {i['State_Name']}")

        elif(i['Assembly'] == 'LS'):

            primary_file_path = os.path.join(TCPD_DATA_PATH, "GE", "Data", "primary", "candidates_electoral_info.csv")
            GE_df = pd.read_csv(primary_file_path, low_memory=False)
            if('Candidate_Image_Link' not in GE_df.columns):
                GE_df['Candidate_Image_Link'] = pd.NA

            if(i['State_Name'] == 'All_States'):
                state_assembly = GE_df.copy()

            else:
                state_assembly = GE_df[GE_df['State_Name'] == i['State_Name']].copy()
            
            print(f"[LS UPDATE] State: {i['State_Name']}")

            assemblies[idx]['Min_Assembly'] = max(1, int(state_assembly['Assembly_No'].min()))
            assemblies[idx]['Max_Assembly'] = int(state_assembly['Assembly_No'].max())

            # If GE PIDs updated, no need to do it again...
            if(GE_updated):
                continue
        
            output_df = get_PID_img_df(GE_df)

            output_file_name = f"{i['File_Prefix']}-pids.csv"
            output_file_path = os.path.join(PID_FILES_FOLDER, output_file_name)
            output_df.to_csv(output_file_path, index = False)

            print("[DONE] Updated GE PIDs for all states!")
            GE_updated = True


    with open(ASSEMBLIES_PATH, 'w') as file:
        json.dump(assemblies, file, indent = 4)
        print(f"[UPDATED] {ASSEMBLIES_PATH}")

if __name__ == '__main__':
    main()