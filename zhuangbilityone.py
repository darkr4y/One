#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'darkray'

import requests
from bs4 import BeautifulSoup
import web
import sqlite3
import time
import sys
import os
import random
import json


reload(sys)
sys.setdefaultencoding("utf-8")

url = 'http://wufazhuce.com/'
dbname = 'oh-my-one.db'

def initDB():
	isDbinited = os.path.exists(dbname)
	if isDbinited:
		return
	cx = sqlite3.connect(dbname)
	cu=cx.cursor()
	cu.execute("create table one (id integer primary key,url varchar(255) UNIQUE,vol varchar(10) UNIQUE,date varchar(20) ,content text NULL)")
	cx.close()



def DbQueryLatestId():
	#查询数据库最新id
	cx = sqlite3.connect(dbname)
	cu=cx.cursor()
	cu.execute("select * from one order by id desc limit 1") 
	rs = cu.fetchone()
	cx.close()
	return rs[1][rs[1].rfind('/') + 1:]

def getOne(one_url):
	#
	rq = requests.get(one_url)
	html = rq.text
	status = rq.status_code
	#print one_url,status,
	if status == 200:
		soup_main = BeautifulSoup(html,"html.parser")
		div = soup_main.find_all("div", {"class": "one-titulo"})
		one_title = div[0].text.strip()
		div = soup_main.find_all("div", {"class": "one-cita"})
		one_content = div[0].text.strip()
		dom = soup_main.find_all("p", {"class": "dom"})
		may = soup_main.find_all("p", {"class": "may"})
		one_date = dom[0].text.strip() + " @ " + may[0].text.strip()
		#print one_url,one_title,one_content,one_date
		return one_url,one_title,one_content,one_date
	return None

def getOneAll(base_url , latest_id):
	db_latest_id = DbQueryLatestId()
	xstart = 1
	if db_latest_id < latest_id:
		xstart = int(db_latest_id) + 1
	elif db_latest_id == latest_id:
		print "All new :)"
		return
	else:
		print "Its joke :("
		return

	#判断不存在则从id=1开始抓取
	for i in range (xstart,int(latest_id) + 1):
		target_url = base_url + str(i)
		if getOne(target_url) is None:
			continue
		iurl,ititle,icontent,idate = getOne(target_url)
		cu.execute("insert into one(url,vol,content,date) values ('%s','%s','%s','%s')" % (iurl,ititle,icontent,idate))
		cx.commit()
		print "Insert OK: " + iurl
	
	cx.close()


def getHomePage(url):
	html = requests.get(url).text
	soup_main = BeautifulSoup(html,"html.parser")
	
	#最新文字id
	div = soup_main.find_all("div", {"class": "fp-one-cita"})
	text_url = div[0].a.attrs["href"]
	id = text_url[text_url.rfind('/') + 1:]
	url_base = text_url[:text_url.rfind('/') + 1]
	
	getOneAll(url_base, id)
	

def dbQueryOne(id):
	cx = sqlite3.connect(dbname)
	cu=cx.cursor()
	cu.execute("select * from one where id = %d" % int(id)) 
	rs = cu.fetchone()
	if rs is None:
		return None
	return rs[0],rs[1],rs[2],rs[3],rs[4]
		
web_urls = (
	'/', 'hello',
	'/json', 'hello_json'
)

def notfound():  
	return web.notfound("WTF :(") 
	
app = web.application(web_urls, globals())
app.notfound = notfound

'''
{"result": {
	"id":  1,
	"url":  "https://api.example.com/zoos",
	"title": "List of zoos",
	"date": 2 Feb 2015,
	"content":  "application/vnd.yourformat+json"
}}
'''
class hello_json:        
	def GET(self):
		id = int(DbQueryLatestId())
		rand_id = random.uniform(1, id)
		oid,iurl,vol,date,myone = dbQueryOne(rand_id)
		data = {'result':{'id':oid,'url':iurl,'title':vol,'date':date,'content':myone}}
		return json.dumps(data)

class hello:        
	def GET(self):
		id = int(DbQueryLatestId())
		rand_id = random.uniform(1, id)
		oid,iurl,vol,date,myone = dbQueryOne(rand_id)
		return "\r\n [%s] %s \r\n ---> %s" % (vol,date,myone)




if __name__ == "__main__":
	initDB()
	getHomePage(url)
	app.run()


