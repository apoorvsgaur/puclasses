import mechanize
import cookielib
from bs4 import BeautifulSoup
import os
import re
import json

#This script will scrape the information from mypurdue.purdue.edu

def return_list_of_all_possible_terms(br):
    list_of_terms = []
    br.select_form(nr=0)
    for control in br.form.controls:
        if control.name == "cat_term_in":
            for item in control.items:
                if item.name != "None":
                    list_of_terms.append(item.name)
    return list_of_terms


#Function data_scrape will use python libraries mechanize and BeautifulSoup to
#get specific details off each class, that will eventually by used to make API calls
def data_scrape():

    #Initializing the headless browser
    br = intialize_browser()

    #Opening mypurdue.purdue.edu - The Course Catalog
    br.open('https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_dyn_ctlg?')

    #Returns list of all possible terms at myPurdue
    list_of_terms = return_list_of_all_possible_terms(br)

    for term in list_of_terms:
        print term
        #br['cat_term_in']=[term]
        #response = br.submit()
    html_source = response.read()
    #print(html_source)
    br.select_form(nr=0)
    course_titles = []
    soup = BeautifulSoup(html_source, 'html.parser')
    select_name = soup.find_all('select', {'name':'sel_subj'})
    #print(select_name)
    for x in select_name:
        course_names = (x.text.split("\n"))
    for x in course_names:
        if(str(x) != '' and str(x) != "Women's And Gender Studies" and str(x) != "CIC Traveling Scholar"):
            course_titles.append(str(x).split("-")[0].strip())
        elif (str(x) == "Women's And Gender Studies"):
            course_titles.append("WGS")
        else:
            course_titles.append("CIC")
    final_list = []
    title = ""
    #print course_titles
    #for x in course_titles:
    #     br.select_form(nr=0)
    item = br.find_control(name="sel_subj", type="select").get("ECE")
    item.selected=True
    response = br.submit()
    html=response.read()
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    #for x in links:
    #     print x
    titles = soup.find_all('td', {'class':'nttitle'})
    for x in titles:
        first_title = x.text
        break
    flash = 0
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        flash += 1
        if ((flash % 2) == 1 and flash > 4):
            value = tds[0].text.encode('utf-8')
            title = value.split("\n")[0]
            if (title == ""):
                break
        if ((flash % 2) == 0 and flash > 5):
            try:
                value = tds[0].text.encode('utf-8').split('campuses:')[0].strip().replace("\xc2\xa0","").split("\n")
            except:
                break
            try:
                value_2 = tds[0].text.encode('utf-8').split('campuses:')[1].split("ECE")[0].strip().replace("\xc2\xa0","").split("\n")
            except:
                break

            # links = tds[0]
            # soup = BeautifulSoup(links, 'html.parser')
            # links = soup.find_all('a')
            # for x in links:
            #     print x
            #print value_2
            Campuses = []
            Learning_Objectives = []
            test_variable = 0
            for x in value:
                data = x.split(":")
                #print data
                if (data[0]=='Credit Hours'):
                    course_description = data[1].split("0")[-1].replace(".","",1).strip()
                    #print course_description
                if ("Credit hours" in data[0]):
                    credit_hours = data[0].strip().split("Credit")[0]
                    #print credit_hours
                if (data[0] == 'Levels'):
                    offered_to = data[1].strip()
                if (data[0] == 'Offered By'):
                    offered_by = data[1].strip()
                if (data[0] == 'Course Attributes'):
                    course_attributes = data[1].strip()
            for x in value_2:
                data = x.split(":")
                if (test_variable == 1):
                    Learning_Objectives.append(data[0])
                if (data[0].strip().split(" ")[0] != '' and data[0].strip() != 'Learning Objectives' and len(data[0].strip().split(" ")) < 4):
                    Campuses.append(data[0].strip())
                elif(data[0].strip() == 'Learning Objectives'):
                    test_variable += 1
            value = title.split("-")[0].strip().split(" ")[-1]
            url = "https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_course_detail?cat_term_in=201610&subj_code_in=ECE&crse_numb_in=" + str(value)
            response = br.open(url)
            #print(response.read())
            class_dict = {}
            class_list = []
            class_dict["Course_Code"] = title
            class_dict["Course_Description"] = course_description
            class_dict["Credit_Hours"] = credit_hours
            class_dict["Levels"] = offered_to
            class_dict["Offered_By"] = offered_by
            class_dict["Course_Attributes"] = course_attributes
            class_dict["Campuses"] = Campuses
            if(len(Learning_Objectives) != 0):
                class_dict["Learning_Objectives"] = Learning_Objectives
            class_list.append(json.dumps(class_dict))
            with open(os.path.dirname(os.path.realpath(__file__))+"/classes/"+title.split("-")[0].strip()+'.json', 'w') as f:
                f.write(str(class_list))
            final_list.append(json.dumps(class_dict))

    with open('total_compile.json', 'w') as f:
        f.write(str(final_list))

def check_dirname_exist():
  path_name = os.path.dirname(os.path.realpath(__file__))
  path_name = path_name + "/classes"
  #print(path_name)

def intialize_browser():
    br = mechanize.Browser()
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', 'Chrome')]
    br.open('https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_dyn_ctlg?')
    return br

data_scrape()
