from django.shortcuts import render
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import csv
import pandas as pd
from collections import Counter
import folium
import os


def get_page_source(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_source = str(soup)
        return page_source

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def save_to_file(page_source, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(page_source)
            
        print(f"Page source saved to {filename}")

    except Exception as e:
        print(f"Error saving to file: {e}")

def get_companyName(file_content):
    
    pattern = r'"companyName":"([^"]+)"'

    matches = re.findall(pattern, file_content)
    return matches

def get_Location(file_content):
    
    pattern = r'"location":\[\{"id":\d+,"name":"([^"]+)"\}\]'

    matches = re.findall(pattern, file_content)
    return matches

def get_language(file_content):
    
    pattern = r'"mandatoryTags":\[\{"id":\d+,"name":"([^"]+)"'

    matches = re.findall(pattern, file_content)
    
    return matches

def get_positionTitle(file_content):
    pattern = r'"title":"(.*?)"'
    new_match = []
    
    matches = re.findall(pattern, file_content)
    for match in matches:
        print(match)
        nm = match.split(" - ")
        if len(nm)>1:
            # print(nm[-2])
            new_match.append(nm[-2])
        else:
            new_match.append("null")
    return new_match

def get_experience(file_content):
    pattern = r'\((\d+-\d+) yrs\)'
    matches = re.findall(pattern, file_content)
    return matches

def get_allMandatorySkills(file_content):
    pattern = r'"title":"(.*?)".*?"mandatoryTags":\[(.*?)\]'
    
    skill_list = []
    
    matches = re.findall(pattern, file_content, re.DOTALL)
    for name in matches:
        mandatory_tags_part = name[1]
        skills = re.findall(r'"name":"(.*?)"', mandatory_tags_part)
        skill_list.append(skills)
    
    return skill_list
    
def get_Date(file_content):
    pattern = r'"createdTimeMs":(\d+)'
    timestamps = re.findall(pattern, file_content)
    matches = timestamps
    
    final_date = []
    # matches = [datetime.utcfromtimestamp(int(ts) / 1000.0) for ts in timestamps]
    for timestamp in matches:
        full_date = datetime.utcfromtimestamp(int(timestamp) / 1000.0)
        date = full_date.date()
        formatted_date = date.strftime("%d-%m-%Y")
        # print(formatted_date)
        final_date.append(formatted_date)
        
    return final_date

def write_CSV(list,csv_path):
    header_row = ["Comapay","Position", "Primary Skill", "Location", "Experience","Other Skills","Date"]
    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header_row)

        for row in list:
            csv_writer.writerow(row)
    print("Data has been written to"+str(csv_path))
    
#-------------------------------------------------------------------------------------------

def scrapTo_csv(page_source):

        
    main_list = list(zip(
        get_companyName(page_source),
        get_positionTitle(page_source),
        get_language(page_source),
        get_Location(page_source),
        get_experience(page_source),
        get_allMandatorySkills(page_source),
        get_Date(page_source)
        ))
    
    write_CSV(main_list,"file.csv")
    

# with open(file_path, 'r') as file:
#     page_source = file.read()

#_________________________________________________________________________________________________

def home(request):
    
    # os.remove("file.csv")
    # os.remove("page_source.txt")
    # try:
    #     df.drop(axis=0, inplace=True)
    # except:
    #     pass
    
    return render(request, 'base.html')




def add(request):
    #Getting the variable
    a = request.GET['n1']
    url = (get_page_source("https://www.hirist.com/search/"+a+"-p"+str(1)+".html"))
    save_to_file(url, "pagesource.txt")
    
    
    for i in range(2,20):
    
        source = (get_page_source("https://www.hirist.com/search/"+a+"-p"+str(i)+".html"))
        
        if "title" in source:
            try:
                with open("pagesource.txt", 'a', encoding='utf-8') as file:
                    file.write(source)
                    
                print("Page source saved to pagesource.txt again")

            except Exception as e:
                print(f"Error saving to file: {e}")
    
    with open("pagesource.txt", 'r') as file:
        page_source = file.read()
    
    
        
    

    # url = "https://www.hirist.com/search/"+str(a)+".html"
    scrapTo_csv(page_source)

#Graph1--------------------------------------------------------------

    x_axis = []
    y_axis = []
    df = pd.read_csv("file.csv")
    
    column_list = df["Primary Skill"].tolist()
    counted_elements = Counter(column_list)
    
    for element,count in counted_elements.items():
        print(element," : ",count)
        x_axis.append(element)
        y_axis.append(count)
        
    if a in x_axis:
        pos = x_axis.index(a)
        print(a," is on ", pos)
        x_axis.pop(pos)
        y_axis.pop(pos)
    else:
        pass
        print(a," is not")
    
    
    print(x_axis)
    print(y_axis)
        
    
    fig = px.bar(
        x=x_axis,
        y=y_axis,
        title="Secondary Skills",
        labels={'x': 'Skills', 'y': 'Number of Jobs'}
    )
#Graph2--------------------------------------------------------------
    dates = []
    x_axis = []
    y_axis = []


    column_list = df["Date"].tolist()

    for i in column_list:
        print(i)
        
        i = datetime.strptime(i, "%d-%m-%Y")
        i = i.strftime("%m-%Y")
        
        dates.append(i)

    date_counts = Counter(dates)
    for date, count in date_counts.items():
        print(f"{date}: {count} occurrences")
        x_axis.append(date)
        y_axis.append(count)
        
    print(x_axis)
    print(y_axis)
    
    
    fig2 = px.line(
        x=x_axis,
        y=y_axis,
        title="Jobs Posted by Month",
        labels={'x': 'Jobs', 'y': 'No. of postings'}
    )

    fig.update_layout(
        title={
            'font_size': 24,
            'xanchor': 'center',
            'x': 0.5
            
    })
    
    chart = fig.to_html()
    chart2 = fig2.to_html()
    context = {'chart': chart,'chart2':chart2,'result':a}
    return render(request, 'chart.html', context)


