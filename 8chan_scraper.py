# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 14:29:28 2019

@author: l.brace@exeter.ac.uk
"""

import requests
import csv
import time
from bs4 import BeautifulSoup
import datetime
from PIL import Image

url = "https://8ch.net/pol/index.html#all"
# Headers to mimic a browser visit
headers = {'User-Agent': 'Mozilla/5.0'}
# Returns a requests.models.Response object
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')
#domains = soup.find_all("thread", class_="name")#postcontrols")
"""What did we just do? We called the ‘find_all’ 
method on the soup object, which looks into itself 
for all the anchor tags with the parameters passed 
in as the second argument. We only passed in one 
restraint (class has to be ‘domain’), but we can 
couple this with many other things, or even just 
use an id.

NOTE: We use ‘class_=‘ because 'class' is a keyword 
reserved by Python for defining classes and such.
If you wanted to pass in more than one parameter, 
all you have to do is make the second parameter 
a dictionary of the arguments you want to include:
soup.find_all("span", {"class": "domain", "height", "100px"})"""
post_line = ['Date_time', 'post_subject', 'author_name', 'poster_id', 'post_number', 'post_body_text', 'omitted', 'replies']
current_dt = datetime.datetime.now()
date = current_dt.strftime("%Y_%m_%d")
time_c = current_dt.strftime("%H")
file_name_string = "8chan_live_posts_scrape_date_" + date + "_time_" + time_c + ".csv"
with open(file_name_string, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(post_line)
attrs = {'class': 'thread', 'data-board': 'pol'}
post_counter = 1
page_index = 1
while (post_counter <= 5000):
    for post in soup.find_all('div', attrs=attrs):
        print("______________________")
        print("post: ", post_counter)
        date_time = post.time.attrs['datetime']
        subject = post.find('span', class_="subject")
        if subject == None:
            subject = "None"
        else:
            subject = post.find('span', class_="subject").text.encode('utf-8')
        print("subject", subject)
        author_name = post.find('span', class_="name").text.encode('utf-8')
        poster_id = post.find('span', class_="poster_id").text.encode('utf-8')
        post_id = post.find('a', class_="post_no").attrs['id'].encode('utf-8')
        body_text = post.find('div', class_="body").text.encode('utf-8')
        omitted = post.find('span', class_="omitted")
        if omitted == None:
            ommitted = "None"
        else:
            omitted = post.find('span', class_="omitted").contents[0].encode('utf-8')
        ignore_first_reply = True
        replies_thread = post.find_all('div', class_="post reply has-file body-not-empty" or "post reply body-not-empty")#class_="thread")
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
    #    post_line = [date_time, subject, author_name, poster_id, post_id, body_text, omitted]
    #    current_dt = datetime.datetime.now()
    #    date = current_dt.strftime("%Y_%m_%d")
    #    time_c = current_dt.strftime("%H")
    #    file_name_string = "8chan_scrape_date_" + date + "_time_" + time_c + ".csv"
    #    with open(file_name_string, 'a') as f:
    #        writer = csv.writer(f)
    #        writer.writerow(post_line)
        image_counter = 1
        number_of_files_in_original_post = len(post.find_all('div', class_="file multifile"))
        if number_of_files_in_original_post == 0:
            number_of_main_post_images = 1
        else:
            number_of_main_post_images = len(post.find_all('div', class_="file multifile"))
        for tag in post.findAll('img'): 
          #  print("_____", tag)
          #  print("Image number: ", image_counter)
            image_url = tag.get('src')
            name_url = str(image_url[39:-4])
            if image_url[:3] == "//i":
                image_url = "http:" + image_url
            try:
                img = Image.open(requests.get(image_url, stream = True).raw)
            except:
                pass#print("Broken URL")
            counter_str = str(image_counter)
            post_str = str(post_id)
            if image_counter <= number_of_main_post_images:
                file_name = "8chan_scrape_date_" + date + "_time_" + time_c + "_" + "post_number_main_post_image_" + post_str + "_" + counter_str+ "_" + name_url + ".jpg"
            else:
                file_name = "8chan_scrape_date_" + date + "_time_" + time_c + "_" + "post_number_reply_image_" + post_str + "_" + counter_str + "_" + name_url + ".jpg"
            img.save(file_name)
            image_counter += 1
        post_counter += 1
    next_button = soup.find("div", class_="pages")#.contents[3]
    next_page_link = next_button.select("a")[page_index].attrs['href']
    print(next_page_link)
    next_page_link_2 = 'http://8ch.net' + next_page_link
    page_index += 1
    time.sleep(2)
    page = requests.get(next_page_link_2, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
print("FINISHED")