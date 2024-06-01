# Baseline GeoJSON are obtained from
1. HTMediaLabs GitHub
2. 



# Important Info
1. Districts can have multiple Parliamentary Constituencies
2. Parliamentary Constituencies can span across multiple districts
3. Assembly Constituencies DO NOT SPAN across Districts
4. Assembly Constituencies DO NOT SPAN across Parliamentary Constituencies

# State Json
Old: Index(['ST_NM', 'geometry'], dtype='object')
New: Index(['ST_ABB', 'ST_CODE', 'ST_NAME', 'geometry'], dtype='object')

# District Json
Old: Index(['cartodb_id', 'censuscode', 'dt_cen_cd', 'st_cen_cd', 'st_nm', 'district', 'geometry'], dtype='object')
New: Index(['cartodb_id', 'censuscode', 'dt_cen_cd', 'st_cen_cd', 'ST_CODE', 'ST_ABB', 'ST_NAME', 'district', 'geometry'], dtype='object')

# Parliament Json
Old: Index(['ST_NAME', 'PC_NAME', 'ST_CODE', 'PC_CODE', 'Res', 'geometry'], dtype='object')
New: Index(['ST_ABB', 'ST_CODE', 'ST_NAME', 'PC_NAME', 'ST_CD', 'PC_CODE', 'Res', 'geometry'], dtype='object')

# Assembly Json
Old: Index(['ST_CODE', 'ST_NAME', 'DT_CODE', 'DIST_NAME', 'AC_NO', 'AC_NAME', 'PC_NO', 'PC_NAME', 'geometry'], dtype='object')
New: 

# Parliamentary Constituency File
1. Create india_2014_parliament-V2.json by copying data/shapefiles-master/india/parliament/india_2014_parliament.json
2. Edited aforementioned new copy with the following.
    a. 



# District Data
1. Create india_2011_district-V2.json by copying data/shapefiles-master/india/districts/india_2011_district.json
2. Create india_state-V2.json by copying data/shapefiles-master/india/state_ut/india_state.json
3. Correct State and UT Names are as follows
    Andaman and Nicobar Islands
    Andhra Pradesh
    Arunachal Pradesh
    Assam
    Bihar
    Chandigarh
    Chhattisgarh
    Dadra and Nagar Haveli and Daman and Diu
    Delhi
    Goa
    Gujarat
    Haryana
    Himachal Pradesh
    Jammu and Kashmir
    Jharkhand
    Karnataka
    Kerala
    Ladakh
    Lakshadweep
    Madhya Pradesh
    Maharashtra
    Manipur
    Meghalaya
    Mizoram
    Nagaland
    Odisha
    Puducherry
    Punjab
    Rajasthan
    Sikkim
    Tamil Nadu
    Telangana
    Tripura
    Uttar Pradesh
    Uttarakhand
    West Bengal


    



