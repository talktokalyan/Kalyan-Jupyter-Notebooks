# this script generates the csv files (pids.csv and rows.csv) needed by the incumbency visualization

# Update (16/Nov/2022 - SGw) - this script only generates {state-code}-assembly-{assembly_no}.csv files
# A separate script needs to be created for updating {state-code}-pids.csv

library(data.table)

library(jsonlite)
library(readr)
library(dplyr)
args = commandArgs(TRUE)
assemblies = fromJSON("../incumbency/assets/assemblies.json")
tcpd_git_link = "/Users/shivam/Desktop/tcpd-data/"

cols_to_get = c("Assembly_No", "Poll_No", "Year", "Candidate","Candidate_Type", "State_Name", "Constituency_Name","Constituency_Type", "Party","Last_Party", "pid", "Votes", "Sex", "Position", "Contested", "No_Terms", "Turncoat", "Incumbent", "Vote_Share_Percentage", "Margin", "Margin_Percentage")


createPartyExpanded = function(partyFile, outFilePre){
  party_data = fread(partyFile, na="")
  expanded.party.names = unique(subset(party_data,!is.na(Expanded_Party_Name),select=c("Party","Expanded_Party_Name")))
  fwrite(expanded.party.names,paste0("../incumbency/data/",outFilePre,"-party-expanded.csv"))
}

createAssemblyData = function(filePath, cols_to_get, outFilePre){
  data = fread(filePath, na="")

  if("Age" %in% names(data)){
    cols_to_get = c(cols_to_get,"Age")
  }
  if("Alliance" %in% names(data)){
    cols_to_get = c(cols_to_get,"Alliance")
  }
  #dt <- dt[dt$No_Mandates > 0]
  data <- data[Party != 'NOTA' , ]
  data = subset(data, select = cols_to_get)

  # filter dt down to only rows whose pid is present in this assembly
  for (assembly in min(data$Assembly_No):max(data$Assembly_No)) {
    print (paste('Generating data for assembly# ', assembly))

    dt = data[Assembly_No <= assembly] # filter out all rows after this assembly

    # get pids of everyone who has a line in this assembly...
    # ... but drop INDs and non-winning-parties parties unless their Position is < 3 to avoid the long tail of insignificant cands

    party_seat_count = dt[Assembly_No == assembly & Position == 1, .(count = .N), by='Party']
    winning_parties = party_seat_count$Party # only winning parties will have an entry in this table
    this_assembly_pids = unique(dt[Assembly_No == assembly ]$pid)
    #& ((Position < 2 & Party =='IND') | (Party != 'IND'))
    print (paste("winning parties = ", winning_parties))

    dt = dt[pid %in% this_assembly_pids]
    # only keep those rows with a pid in this assembly

    terms_served_by_pid = dt[Position == 1, .(Terms=length(unique(Assembly_No))), by=c('pid')]
    dt = merge (dt, terms_served_by_pid, by=c('pid'), all.x=TRUE)

    # fix the #mandates and contested to be whatever it is up to the current assembly
    # otherwise rows for the same pid will have different values in these columns
    dt[, No_Terms:=max(No_Terms), by=c('pid')]
    dt[, Contested:=max(Contested), by=c('pid')]



    terms_contested_by_pid = dt[, .(Terms_Contested=length(unique(Assembly_No))), by=c('pid')]
    dt = merge (dt, terms_contested_by_pid, by=c('pid'), all.x = TRUE)
    dt$Position[which(dt$Position < 0 )] = NA
    dt$No_Terms= NULL
    fwrite(dt, file=paste0('../incumbency/data/',outFilePre,'-incumbency-',assembly,'.csv'))
  }


}



if (length(args) > 0)  {
  sts = which(assemblies$State_Code %in% args)
  print(paste("Generating data for following state assemblies :",paste(assemblies$State_Name[sts],collapse = ", ")))
  #stop ("Please provide 2 arguments:  Root directory of the  state name and the path to Vidhan Sabha number file.")
}else if(length(args)==0){
  sts = c(1:nrow(assemblies))
  print("No Arguments given, generating data for all assemblies")
}


for(i in sts){
  state = assemblies[i,]
  assembly = state$State_Name

  outFilePre = state$File_Prefix
  if(assembly == "All_States"){
    filePath <- paste0(tcpd_git_link,'GE/Data/derived/mastersheet.csv')
    partyFile <- paste0(tcpd_git_link,'GE/Data/derived/lokdhaba/ge_party_statistics.csv')

  }else{
    filePath <- paste0(tcpd_git_link,'AE/Data/',assembly,'/derived/mastersheet.csv')
    partyFile <- paste0(tcpd_git_link,'AE/Data/',assembly,'/derived/lokdhaba/ae_party_statistics.csv')
  }

  if(file.exists(filePath))
  {
    createPartyExpanded(partyFile, outFilePre)
    createAssemblyData(filePath, cols_to_get, outFilePre)
  }
  else{
    print("Skipping")
    print(state)
  }
}


######### update pids function, to update later
# read the pics table from both LS and PRS and assign the link in the last row to that pid
# = fread('~/github/tcpd_data/data/AE/oct_19_working/maharashtra_candidates_pictures.csv',na="")
#source("~/github/tcpd_data/data/GE/scripts/helper.R")
#pics = normalizePartyAbb(pics,"party_list")
#pics = fread("~/github/tcpd_data/data/AE/oct_19_working/JH_AE19_working_mastersheet.csv",stringsAsFactors = F,na="") %>% subset(Party!="NOTA" & !is.na(picture_link),select=c("pid","picture_link")) %>% unique()
#names(pics)[which(names(pics)=="picture_link")]=="link"
#fwrite(pics,"../jh-pids.csv")
#curr.data = subset(data,Assembly_No ==4)

#mrg = left_join(pics,curr_data[,c("State_Name","Constituency_Name","Candidate","Party","Position","pid")],by=c("state_list"= "State_Name","constituency_list"="Constituency_Name","name_list"="Candidate","party_list"="Party"))
#dt = data.table(mrg)
#pics_affidavit   = dt[, .(link=.SD[nrow(.SD)]$picture_link_list), by=.(pid)]
#pics_ls = fread ('~/github/tcpd_data/data/GE/GE_19_working/pictures_with_pids.csv');
#pics_ls = pics_ls[, .(link=.SD[nrow(.SD)]$link), by=.(pid)]

#pics_prs = fread ('~/github/tcpd_data/data/GE/GE_19_working/pictures_with_pids_prs.csv');
#pics_prs = pics_prs[, .(link=.SD[nrow(.SD)]$link), by=.(pid)]

# pics_merged = merge(pics_prs, pics_ls, by=c('pid'), all.x=TRUE, all.y=TRUE)
#
# # the link is preferably PRS (link.x), but if its NA, use the LS link
# pics_merged$link = ''
# for (i in 1:nrow(pics_merged)) {
#   if (is.na(pics_merged[i]$link.x)) {
#     pics_merged[i]$link = pics_merged[i]$link.y;
#   } else {
#     pics_merged[i]$link = pics_merged[i]$link.x;
#   }
# }

#fwrite(pics_affidavit, file='../mh-pids.csv')
