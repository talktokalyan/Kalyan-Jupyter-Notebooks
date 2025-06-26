Repository for assembly incumbency profile  visualization 

- This runs as a barebones Python HTTP server with all the files living in the incumbency/* child folder. 
- Under assets, csv-gen.R is used to update {st_code}-incumbency-{assembly_number}.csv files for the visualisation. 
- The nginx config on AWS excludes data/* files from caching (this was a bug earlier)

## To do in the future: 
1. Move utility scripts *out* of the set of files that are exposed on the web server (so move assets/csv-gen.R out of the folder) 
2. (Low priority) Replace raw data .csv files with a proper backend 
3. (Important) Fix Karnataka-Mysore bug on PCT (documented on GitLab)
4. (Important) Add script to update {state_code}-pids.csv files
