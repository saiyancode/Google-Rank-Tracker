from random import choice
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import datetime
from concurrent.futures import ThreadPoolExecutor
import sqlite3 as sql
import time
from selenium import webdriver
import re
from collections import defaultdict
import pymongo
from pymongo import MongoClient
from threading import Thread

# Mongo Settings

client = MongoClient('localhost', 27017)
db = client.google_database
collection = db.test_collection

# Google Location Settings

domain = 'https://www.google.co.uk'

# Speed Settings

threads = 3


unix = int(time.time())
date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d'))
keyword = [line.rstrip('\n') for line in open('keywords.txt')]
keywords = [str.replace(x,' ','+') for x in keyword]
AgentList = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
             "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17",
             "Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:34.0) Gecko/20100101 Firefox/34.0"]

def ranks(i):
	driver = webdriver.Chrome(executable_path='/Users/willcecil/Dropbox/Python/chromedriver')
	#driver = webdriver.PhantomJS(executable_path='/Users/willcecil/Dropbox/Python/phantomjs')
	url = domain + '#q=' + i + '?&num=50'
	driver.get(url)
	time.sleep(5)
	soup = BeautifulSoup(driver.page_source)
	print("Opening this page " + domain+ '#q='+i)

	try:
	    results = soup.findAll('div',attrs={'class':'g'})
	    print(len(results))
	    #print(results)
	    for a,b in enumerate(results):
	    	#print(b)
	    	soup = b
	    	header = soup.find('h3')
	    	result = a + 1
	    	title = header.text
	    	link = soup.find('a')
	    	url = link['href']
	    	url = re.sub(r'/url\?q=', '',str(url)) 
	    	url = re.sub(r'&sa=.*', '',str(url))

	    	#domain = re.search(r"(http|https)://.*/", str(url)).group(0) - Not working


	    	# Extract Score Data using ASIN number to find the span class

	    	description = soup.find('span', attrs={'class':'st'})
	    	description = description.text

	    	result_type = "Standard Serp"


	    	# Test Statements
	    	# print(title)
	    	# print(url)
	    	# print(i)

	    	# Save to dict for multithreading test

	    	data = defaultdict(list)

	    	data['Date'].append(date)
	    	data['Unix'].append(unix)
	    	data['Keyword'].append(i)
	    	data['Title'].append(title)
	    	data['Description'].append(description)
	    	data['Rank'].append(result)
	    	data['Type'].append(result_type)
	    	data['URL'].append(url)
	    	#data['Domain'].append(domain)

	    	db.collection.insert(data)

	except Exception as e:
	    print(e)
	driver.quit()

futures = []
with ThreadPoolExecutor(max_workers=threads) as ex:
    for keyword in keywords:
        futures.append(ex.submit(ranks,keyword))
