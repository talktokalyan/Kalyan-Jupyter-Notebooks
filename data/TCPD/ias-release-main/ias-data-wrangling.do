*------------------------------------------------------------
* Set your working directory to where the CSV files are
*------------------------------------------------------------
cd "/Users/kalyan/Library/CloudStorage/OneDrive-Personal/Kalyan/KK-Python/Kalyan-Jupyter-Notebooks/data/TCPD/ias-release-main"

*------------------------------------------------------------
* STEP 1: Import education.csv and reshape to wide
*------------------------------------------------------------
import delimited ias-education.csv, clear

drop source

foreach v of varlist cadre qualification subject category_of_subject division {
    replace `v' = trim(`v')
}
bys id reference_value: gen sno = _n

bys id reference_value: gen number = _N

drop if number==2 & qualification=="N.A."

drop number

bys id reference_value: gen number = _N

drop if sno ==2

reshape wide qualification subject category_of_subject division, i(id cadre name) j(reference_value)

save education_wide.dta, replace

*------------------------------------------------------------
* STEP 2: Import experience.csv and reshape to wide
*------------------------------------------------------------
import delimited ias-experience.csv, clear

/* 211 records with missing reference_value are dropped */
drop if mi(reference_value)

/* Remove duplicate records */
drop if id == "MT007500" & cadre == "Manipur" | id == "MT011411" & cadre == "Manipur" 
drop if name=="Dr. Bimal Kanti Chakraborty" & id =="MT011514"

bysort id reference_value: gen num_rec = _N
bysort id reference_value: gen obsorder = _n
keep if num_rec == 1 | (num_rec == 2 & obsorder == 2)

drop num_rec obsorder reference_value

gen st_date =  date(start_date, "YMD")
drop if mi(st_date)

gen en_date =  date(end_date, "YMD")

/* Missing Data is hypothetically ended in Dec 2021 , date when TCPD data was built */
replace en_date = td(31dec2021) if missing(en_date) & !mi(st_date)

* Format it to show as a readable date
format en_date %td
* Generate Service days duration
gen serv_days =  en_date - st_date

* Order within ID by longest duration
gsort id -serv_days
by id: gen rank = _n

* keep only top 2
keep if rank <= 2


bys id: egen max_serv_days = max(serv_days)

drop start_date end_date source
format *date* %td

reshape wide designation level office organisation field_of_experience category_of_experience st_date en_date serv_days , i(id cadre name max_serv_days) j(rank)

save experience_wide.dta, replace

*------------------------------------------------------------
* STEP 3: Import profile.csv and merge with the reshaped data
*------------------------------------------------------------
import delimited ias-profile.csv, clear

/* Keep only latest observations that repeat (based on id) and unique id that appear only once */

bysort id: gen num_rec = _N
bysort id: gen obsorder = _n

keep if num_rec == 1 | (num_rec == 2 & obsorder == 2)

merge 1:1 id using education_wide.dta
gen merge_step1 =_merge
drop _merge
merge 1:1 id using experience_wide.dta

* Save the final merged file
save ias-master-merged.dta, replace
