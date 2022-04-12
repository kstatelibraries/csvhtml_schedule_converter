#!/usr/bin/env python3
#################################
#     CSV to HTML Converter     #
#  ---------------------------  #
#  Creates an HTML file from    #
#  a supplied CSV for Records   #
#  retention schedule website   #
#                               #
#  Feb 2022 - Greg G            #
#################################

#############
## IMPORTS ##
#############

# Pandas for document / table processing
# os for path testing
# numpy for array manipulations
# html for html escape chars and string cleaning
# math for null value checks
import pandas as pd
import os
import numpy as np
import html
import math
#

def convert_csvhtml(kstatefile, statefile, regentsfile, outputfile):

    ###############
    ## VARIABLES ##
    ###############

    # vars to hold error code and reason to return on failure, where 0 means no errors and 1 means an error was encountered
    errorcode = 0
    error_reason = "Program completed successfully"

    # string array to hold column names from csvs (to avoid inconsistant column naming in CSV)
    colnames = ["Agency Code","Agency","Subagency1","Subagency2","Subagency3","Subagency4","Title","SeriesID","Description","Status","Approved","Retention","Disposition","Retrictions","Comments","Authority","KAR #","Format","Last Survey"]
    
    # string array to contain each line of generated HTML to be written to output file from CSV files
    htmltext = []

    # *** NOTE *** #
    # * each section of the final html file is broken out into 'blocks' of string arrays with one string per line of html to be written
    # * each 'block' is appended to the final htmltext array, then that final array is written to the file as a single write operation
    # * this is broken out this way to improve readability and contain each section of the final file more neatly for editing and troubleshooting within this script
    #

    # string array to hold opening lines of html for the output file
    startblock = [ "<!DOCTYPE html>"
                    ,"<html lang=\"en\">"
                    ,"<head>"
                    ,"<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">"
                    ,"<title>Official Document Schedules</title>"
                    ,"</head>"]

    # string array to contain style block lines for HTML file
    styleblock = ["<style>.outerrow {width:100%; border-top: 1px dimgray solid;padding-top:15px;padding-bottom:15px;margin-top:15px;display:block;}"
                ,".tablecolumn {width:100%;display:block;clear:both;margin-bottom:1px;min-height:25px;}"
                ," .topouterrow, .Agency, .AgencyCode, .Subagency1, .Subagency2, .Subagency3, .Subagency4, .Approved, .Authority, .Format, .LastSurvey, .KAR {display:none;}"
                ," .label {float: left;display:block;width:20%;}"
                ," .content {float:right;display:block;width:78%;}"
                ,"#searchdiv button {padding:10px;background-color:#4f1d85; margin-right:20px; color:white; font-size:14px;font-weight:bold;cursor:pointer;margin-bottom:5px;}"
                ,"#searchdiv button:hover, #searchdiv button:active, #searchdiv button:visited {background-color:#663596;}"
                ,"#searchdiv button#resetbutton {background-color:lightgray;color:black;}"
                ,"#searchdiv button#resetbutton:hover, #searchdiv button:active, #searchdiv button:visited {background-color:dimgray;}"
                ,".microclear {width:100%;height:1px;clear:both;}"
                ,"input#searchinput {font-size:16px;margin-right:10px;border: 2px black solid;padding:4px;}"
                ,".clearfix:after {"
                ,"   content: \" \";"
                ,"   visibility: hidden;"
                ,"   display: block;"
                ,"   height: 0;"
                ,"   clear: both;"
                ,"}"
                ,".is-hidden { display: none; }"
                ,"</style>"
                ]
    
    # string array to contain the script block lines for HTML file
    scriptblock = ["<script type=\"text/javascript\">"
                ,"<![CDATA["
                # script to toggle hiding sections of the schedule by state, regent, kstate. Change button color/text to indicate that its hidden
                ,"\tfunction toggle_visibility(id,btn) {"
                ,"\t\tvar d = document.getElementById(id);"
                ,"\t\tvar b = document.getElementById(btn);"
                ,"\t\t"
                ,"\t\tif(d.style.display == \"none\"){"
                ,"\t\t\td.style.display = \"block\";"
                ,"\t\t\tb.style.backgroundColor = \"#4f1d85\";"
                ,"\t\t\tb.style.color = \"#efefef\";"
                ,"\t\t\tb.style.textDecoration = \"none\";"
                ,"\t\t}"
                ,"\t\telse{"
                ,"\t\t\td.style.display = \"none\";"
                ,"\t\t\tb.style.backgroundColor = \"dimgray\";"
                ,"\t\t\tb.style.textDecoration = \"line-through\";"
                ,"\t\t\tb.style.color = \"white\";"
                ,"\t\t}"
                ,"\t}"
                # function to allow searching schedules by keywords contained in any of the fields for each, hide all non-matching schedule items
                ,"\tfunction liveSearch() {"
                ,"\t\tvar timer;"
                ,"\t\tlet search_query = document.getElementById(\"searchinput\").value;"
                ,"\t\t"
                ,"\t\tlet rows = document.getElementsByClassName(\"outerrow\");"
                ,"\t\tfor (i = 0; i < rows.length; i++) {"
                ,"\t\t\tif (rows[i].innerText.toLowerCase().includes(search_query.toLowerCase())) {"
                ,"\t\t\t\trows[i].classList.remove(\"is-hidden\");"
                ,"  \t\t\t  } "
                ,"\t\t\telse {"
                ,"\t \t\t\trows[i].classList.add(\"is-hidden\");"
                ,"\t\t\t}"
                ,"\t\t}"
                ,"\t}"
                # only enable search after page loads to prevent problems. Use timed delay to prevent excessive search queries
                ,"\twindow.onload = function() {"
                ,"\t\tlet typingTimer;\t\t"
                ,"\t\tlet typeInterval = 100;"
                ,"\t\tlet searchInput = document.getElementById(\"searchinput\");"
                ,"\t\tdocument.getElementById(\"searchinput\").value = \"\";"
                ,"\t\tsearchInput.addEventListener('keyup', () => {"
                ,"\t\t\tclearTimeout(typingTimer);"
                ,"\t\t\ttypingTimer = setTimeout(liveSearch, typeInterval);"
                ,"\t\t});"
                ,"\t}"
                # clear search bar contents
                ,"\tfunction resetSearch() "
                ,"\t{"
                ,"\t\tdocument.getElementById(\"searchinput\").value = \"\";"
                ,"\t\tliveSearch()"
                ,"\t}"
                ,"]]>"
                ,"</script>"
                ]
    # string array to contain the search bar div with its buttons
    searchblock = ["\t<div id=\"searchdiv\">"
                ,"\t<input type=\"search\" id=\"searchinput\" alt=\"Filter the schedules on this page by keyword\" placeholder=\"Search keyword..\"/>"
                ,"\t<button id=\"resetbutton\" alt=\"click here to reset all of the schedules\" onclick =\"resetSearch()\">Reset Search</button>"
                ,"\t<button id=\"kstatebutton\" alt=\"click here to hide the k-state schedules\" onclick=\"toggle_visibility('kstate','kstatebutton');\">K-State Schedules</button>"
                ,"\t<button id=\"statebutton\" alt=\"click here to hide the kansas state schedules\" onclick=\"toggle_visibility('state','statebutton');\">State General Schedules</button>"
                ,"\t<button id=\"regentbutton\" alt=\"click here to hide the regents schedules \" onclick=\"toggle_visibility('regents','regentbutton');\">Regent Schedules</button>"
                ,"\t<button id=\"exportbutton\" alt=\"click here to export all of the selected schedules\">Export Selected Schedules</button>"
                ,"</div>"
                ]

    # string array to contain all html generated for schedules for kstate, regents, and state from csvs
    scheduleblock = []
    ##

    ##################
    ## PROCESS CSVs ##
    ################## 
             
    # test to make sure csv paths provided are valid
    if not os.path.exists(kstatefile) or not os.path.exists(statefile) or not os.path.exists(regentsfile):
        errorcode = 1
        error_reason = "File path(s) provided are not valid"
        return errorcode, error_reason

    # load contents of each csv file into dataframes, use column name list, skip header row
    kstatedata = pd.read_csv(kstatefile, names=colnames, skiprows = 1)
    statedata = pd.read_csv(statefile, names=colnames, skiprows = 1)
    regentsdata = pd.read_csv(regentsfile, names=colnames, skiprows = 1)

    ### Function to loop through contents of each csv files dataframe
    def csvloop(csvdata,headername,idname):
        
        # array to hold return results
        results = []

        # open id div and header
        results.append("<div id=\""+idname+"\">")
        results.append("<h1>"+headername+"</h1>")

        # loop through all csv rows, create html lines for each as strings in array
        for r, row in csvdata.iterrows():

            # open outterow div
            results.append("<div class=\"outerrow\">")

            # create one div per column, fill with label and content spans
            for c in range(len(colnames)):
                keyword = colnames[c]
                results.append("<div class='clearfix tablecolumn " + keyword.replace(" ","") + "'>")
                results.append("\t<span class='label'>"+ keyword +"</span>")
                if str(row[keyword]) == "nan":
                    results.append('')
                else:
                    results.append("\t<span class='content'>"+ html.escape(str(row[keyword])) +"</span>")
                results.append("</div>")
            #
            # close outerrow
            results.append("</div>")
        #
        # Close id div
        results.append("</div>")

        # return string array of html lines
        return results
        #
    ###

    # process each csv's dataframe using the csvloop function, pass in text for Header section of HTML, pass in id for section div id, append results to the scheduleblock html list
    scheduleblock = np.append(scheduleblock, csvloop(kstatedata,"K-State Schedules","kstate"))
    scheduleblock = np.append(scheduleblock, csvloop(statedata,"State Schedules","state"))
    scheduleblock = np.append(scheduleblock, csvloop(regentsdata,"Regents Schedules","regents"))
    #
    
    ######################
    ## CREATE HTML FILE ##
    ######################

    # append first lines to output html
    #htmltext = np.append(htmltext,startblock)
    # append style to output html
    htmltext = np.append(htmltext,styleblock)
    # append script
    htmltext = np.append(htmltext,scriptblock)
    # append search to final html
    htmltext = np.append(htmltext,searchblock)
    # append generated schedule data    
    htmltext = np.append(htmltext,scheduleblock)

    # write final HTML string array to output file, one line per string
    with open(outputfile,'w',encoding='utf-8') as file:
        np.savetxt(file, htmltext, delimiter="\n", fmt='%s')
    
    # return any error codes and reasons
    error_reason = "No Errors, Completed Successfully"
    return errorcode, error_reason
#