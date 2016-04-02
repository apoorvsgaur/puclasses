import mechanize
import cookielib
from bs4 import BeautifulSoup
import os
import re
import json

#This script will scrape the information from mypurdue.purdue.edu

#Function data_scrape will use python libraries mechanize and BeautifulSoup to
#get specific details off each class, that will eventually by used to make API calls
def data_scrape():

    #Initializing the headless browser
    br = intialize_browser()

    #Opening mypurdue.purdue.edu - The Course Catalog
    br.open('https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_dyn_ctlg?')

    #Returns list of all possible terms at myPurdue
    (br, list_of_terms) = return_list_of_all_possible_terms(br)

    for term in list_of_terms: #Iterating over each term
        br.back()
        br.select_form(nr=0)
        br['cat_term_in'] = [term]
        #Returns list of all school names Eg. ECE, ME
        course_titles = get_school_names(br)
        #print course_titles

        for course_title in course_titles:
            #Returns a list of links of all classes in a department Eg, course_title = ECE, return links for ECE301, ECE302
            links_to_classes_in_a_deparment = return_links_of_all_courses_in_a_department(br, course_title)
            for link in links_to_classes_in_a_deparment:
                full_link = "https://selfservice.mypurdue.purdue.edu/" + str(link)

    # flash = 0
    # for tr in soup.find_all('tr'):
    #     tds = tr.find_all('td')
    #     flash += 1
    #     if ((flash % 2) == 1 and flash > 4):
    #         value = tds[0].text.encode('utf-8')
    #         title = value.split("\n")[0]
    #         if (title == ""):
    #             break
    #     if ((flash % 2) == 0 and flash > 5):
    #         try:
    #             value = tds[0].text.encode('utf-8').split('campuses:')[0].strip().replace("\xc2\xa0","").split("\n")
    #         except:
    #             break
    #         try:
    #             value_2 = tds[0].text.encode('utf-8').split('campuses:')[1].split("ECE")[0].strip().replace("\xc2\xa0","").split("\n")
    #         except:
    #             break
    #
    #         # links = tds[0]
    #         # soup = BeautifulSoup(links, 'html.parser')
    #         # links = soup.find_all('a')
    #         # for x in links:
    #         #     print x
    #         #print value_2
    #         Campuses = []
    #         Learning_Objectives = []
    #         test_variable = 0
    #         for x in value:
    #             data = x.split(":")
    #             #print data
    #             if (data[0]=='Credit Hours'):
    #                 course_description = data[1].split("0")[-1].replace(".","",1).strip()
    #                 #print course_description
    #             if ("Credit hours" in data[0]):
    #                 credit_hours = data[0].strip().split("Credit")[0]
    #                 #print credit_hours
    #             if (data[0] == 'Levels'):
    #                 offered_to = data[1].strip()
    #             if (data[0] == 'Offered By'):
    #                 offered_by = data[1].strip()
    #             if (data[0] == 'Course Attributes'):
    #                 course_attributes = data[1].strip()
    #         for x in value_2:
    #             data = x.split(":")
    #             if (test_variable == 1):
    #                 Learning_Objectives.append(data[0])
    #             if (data[0].strip().split(" ")[0] != '' and data[0].strip() != 'Learning Objectives' and len(data[0].strip().split(" ")) < 4):
    #                 Campuses.append(data[0].strip())
    #             elif(data[0].strip() == 'Learning Objectives'):
    #                 test_variable += 1
    #         value = title.split("-")[0].strip().split(" ")[-1]
    #         url = "https://selfservice.mypurdue.purdue.edu/prod/bwckctlg.p_disp_course_detail?cat_term_in=201610&subj_code_in=ECE&crse_numb_in=" + str(value)
    #         response = br.open(url)
    #         #print(response.read())
    #         class_dict = {}
    #         class_list = []
    #         class_dict["Course_Code"] = title
    #         class_dict["Course_Description"] = course_description
    #         class_dict["Credit_Hours"] = credit_hours
    #         class_dict["Levels"] = offered_to
    #         class_dict["Offered_By"] = offered_by
    #         class_dict["Course_Attributes"] = course_attributes
    #         class_dict["Campuses"] = Campuses
    #         if(len(Learning_Objectives) != 0):
    #             class_dict["Learning_Objectives"] = Learning_Objectives
    #         class_list.append(json.dumps(class_dict))
    #         with open(os.path.dirname(os.path.realpath(__file__))+"/classes/"+title.split("-")[0].strip()+'.json', 'w') as f:
    #             f.write(str(class_list))
    #         final_list.append(json.dumps(class_dict))
    #
    # with open('total_compile.json', 'w') as f:
    #     f.write(str(final_list))

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

def return_list_of_all_possible_terms(br):
    list_of_terms = []
    br.select_form(nr=0)
    for control in br.form.controls:
        if control.name == "cat_term_in":
            for item in control.items:
                if item.name != "None":
                    list_of_terms.append(item.name)
    return (br, list_of_terms)

def get_school_names (br):
    response = br.submit()
    html_source = response.read()
    br.select_form(nr=0)
    soup = BeautifulSoup(html_source, 'html.parser')
    course_titles = []
    school_names_HTML = soup.find_all('select', {'name':'sel_subj'}) #Eg. ECE, ME etc.
    for school_name in school_names_HTML:
        course_names = (school_name.text.split("\n"))
    for course_name in course_names:
        if(str(course_name) != '' and str(course_name) != "Women's And Gender Studies" and str(course_name) != "CIC Traveling Scholar"):
            course_titles.append(str(course_name).split("-")[0].strip())
        elif (str(course_name) == "Women's And Gender Studies"):
            course_titles.append("WGS")
        elif (str(course_name) == "CIC Traveling Scholar"):
            course_titles.append("CIC")
        elif (str(course_name) != ''):
            print str(course_name)
    return course_titles

def return_links_of_all_courses_in_a_department(br, course_title):
    item = br.find_control(name="sel_subj", type="select").get(course_title)
    item.selected=True
    response = br.submit()
    html=response.read()
    soup = BeautifulSoup(html, 'html.parser')
    links_of_the_course_title_page = soup.find_all('a')
    class_titles_of_course_title = soup.find_all('td', {'class':'nttitle'})
    links = []
    for link in links_of_the_course_title_page:
        try:
            if "course_detail" in link['href']:
                links.append(link['href'])
        except:
            pass
    return links
    #for class_title in class_titles_of_course_title:
    #    first_title = x.text
    #    print first_title



data_scrape()
