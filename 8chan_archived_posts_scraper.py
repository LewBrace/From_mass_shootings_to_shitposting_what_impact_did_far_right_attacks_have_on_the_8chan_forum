# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 14:29:28 2019

@author: l.brace@exeter.ac.uk
"""

import requests
import csv
import time
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
import datetime
from PIL import Image
from requests_html import HTMLSession
#import nest_asyncio
import time

url = "https://8ch.net/pol/archive/index.html"#"https://8ch.net/pol/index.html"
"""Here, Selenium accesses the Chrome browser driver in incognito mode and 
without actually opening a browser window(headless argument)."""
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=r'C:/FILEPATH_TO_WEBDRIVER/webdrivers/chromedriver.exe', chrome_options=options)
"""Here, Selenium web driver traverses through the DOM of Trip Advisor review 
page and finds all “More” buttons. Then it iterates through all “More” buttons
 and automates their clicking. On the automated clicking of “More” buttons, 
 the reviews which were partially available before becomes fully available."""
driver.get("https://8ch.net/pol/archive/index.html")
more_buttons = driver.find_elements_by_class_name("moreLink")
for x in range(len(more_buttons)):
  if more_buttons[x].is_displayed():
      driver.execute_script("arguments[0].click();", more_buttons[x])
      time.sleep(1)
page_source = driver.page_source

post_line = ['Date_time', 'post_subject', 'author_name', 'poster_id', 'post_number', 'post_body_text', 'omitted', 'replies']
current_dt = datetime.datetime.now()
date = current_dt.strftime("%Y_%m_%d")
time_c = current_dt.strftime("%H")
file_name_string = "attempt_2_8chan_archive_scrape_date_" + date + "_time_" + time_c + ".csv"
with open(file_name_string, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(post_line)
"""let's make soup."""
years = ["2015", "2017", "2018", "2019"]
soup = BeautifulSoup(page_source, 'lxml')
url_for_joining = "https://8ch.net"
post_counter = 1
current_dt = datetime.datetime.now()
date = current_dt.strftime("%Y_%m_%d")
time_c = current_dt.strftime("%H")
test_year = soup.find('div', class_="2019")
for post in test_year.find_all('div', class_="idata"):
    link = post.a.get("href")
    post_url = url_for_joining + str(link)
    # Headers to mimic a browser visit
    headers_2 = {'User-Agent': 'Mozilla/5.0'}
    # Returns a requests.models.Response object
    post_page = requests.get(post_url, headers=headers_2)
    post_soup = BeautifulSoup(post_page.text, 'html.parser')
    print("______________________")
    print("post: ", post_counter)
    date_time = post_soup.time.attrs['datetime']
    print(date_time)
    subject = post_soup.find('span', class_="subject")
    if subject == None:
        subject = "None"
    else:
        subject = post_soup.find('span', class_="subject").text.encode('utf-8')
    author_name = post_soup.find('span', class_="name").text.encode('utf-8')
    poster_id = post_soup.find('span', class_="poster_id").text.encode('utf-8')
    post_id = post_soup.find('a', class_="post_no").attrs['id'].encode('utf-8')
    body_text = post_soup.find('div', class_="body").text.encode('utf-8')
    omitted = post_soup.find('span', class_="omitted")
    if omitted == None:
        ommitted = "None"
    else:
        omitted = post_soup.find('span', class_="omitted").contents[0].encode('utf-8')
    
    ignore_first_reply = True
    replies_thread = post_soup.find_all('div', class_="post reply has-file body-not-empty" or "post reply body-not-empty")#class_="thread")
    #print(replies_thread)
    replies = []
    for reply in replies_thread:#.find_all('div', class_="post reply has-file body-not-empty" or "post reply body-not-empty"):
        if ignore_first_reply == False:
            replies.append(reply.text.encode('utf-8'))
        else:
            ignore_first_reply = False

    post_line = [date_time, subject, author_name, poster_id, post_id, body_text, omitted]
    for write_reply in replies:
        post_line.append(write_reply)
    with open(file_name_string, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(post_line)
    image_counter = 1
#    for tag in post_soup.findAll('img'): 
#        print("Image number: ", image_counter)
#        image_url = tag.get('src')
#        if image_url[:3] == "//i":
#            image_url = "http:" + image_url
#        try:
#            img = Image.open(requests.get(image_url, stream = True).raw)
#            counter_str = str(image_counter)
#            post_str = str(post_id)
#            file_name = "8chan_scrape_date_" + date + "_time_" + time_c + "_" + post_str + "_" + counter_str + ".jpg"
#            img.save(file_name)
#        except:
#            print("Broken URL")
##        counter_str = str(image_counter)
#        post_str = str(post_id)
#        file_name = "8chan_scrape_date_" + date + "_time_" + time_c + "_" + post_str + "_" + counter_str + ".jpg"
#        img.save(file_name)
#        image_counter += 1
    post_counter += 1