
library(data.table)

library(jsonlite)
library(readr)
library(dplyr)

assemblies = fromJSON("~/github/incumbency/assets/assemblies.json")
tcpd_git_link = "~/github/tcpd_data/data/"

ge.states = fread(paste0(tcpd_git_link,"state_codes.csv"))
ms = fread(paste0(tcpd_git_link,'GE/Data/derived/mastersheet.csv'))
states = ms[Poll_No ==0,list(Min_Assembly = min(.SD$Assembly_No), Max_Assembly= max(.SD$Assembly_No)),by="State_Name"]

states$State_Name[which(!states$State_Name %in% ge.states$State_Name)]

ge.states$State_Name[which(!ge.states$State_Name %in% states$State_Name)]

ge.states$State_Name[which(ge.states$State_Name=="Dadra_Nagar_&_Haveli")] = "Dadra_&_Nagar_Haveli"

states = left_join(states,ge.states, by ="State_Name")
states$ST_NAME[which(states$State_Name=="Goa,_Daman_&_Diu")] = "GDD"
states$ST_NAME[which(states$State_Name=="Madras")] = "MD"
states$ST_NAME[which(states$State_Name=="Telangana")] = "TG"
states$ST_NAME[which(states$State_Name=="Bihar")] = "BH"

states$Assembly = "LS"
states$State_Code = states$ST_NAME
states$File_Prefix = "ge"
states$Name = paste(gsub("_"," ",states$State_Name),"Lok Sabha")
states = subset(states, select = names(assemblies))
new.assemblies = rbind(assemblies,states)

write(toJSON(new.assemblies),file = "~/github/incumbency/assets/updated.assemblies.json")

