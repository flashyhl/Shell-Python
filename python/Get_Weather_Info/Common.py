#/usr/bin/python
#-*- coding: UTF-8 -*-
import time,sys
import Db_Conn

reload(sys)
sys.setdefaultencoding('utf8')

# 获取当前时间戳
def TimeStamp():
	nowtime = time.localtime()
	ts = time.mktime(nowtime)
	return ts

def TimeFormat():
	nowtime = time.localtime()
	ts = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
	return ts

def DateFormat():
	nowtime = time.localtime()
	ts = time.strftime('%Y-%m-%d', nowtime)
	return ts

def Query(conn, sqlString):
	cursor = conn.cursor()
	cursor.execute(sqlString)
	returnData = cursor.fetchall()
	cursor.close()
	return returnData

def Dml(conn, sqlString):
	cursor = conn.cursor()
	cursor.execute(sqlString)
	conn.commit()
#	conn.close()


