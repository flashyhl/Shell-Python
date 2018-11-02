#!/usr/bin/python
#-*- coding: UTF-8 -*-

import MySQLdb


class Mydb_Conn:
	def __init__(self):
		self.DB_HOST = '192.168.53.251'
		self.DB_PORT = 3306
		self.DB_USER = 'xxxxxxxx'
		self.DB_PWD = 'xxxxxxxxxxxxx'
		self.DB_NAME = 'xxxxxxxxxx'
		self.DB_CHAR = 'utf8'

		self.conn = self.getConnection()

	def getConnection(self):
		try:
			return MySQLdb.Connect(
				host=self.DB_HOST,
				port=self.DB_PORT,
				user=self.DB_USER,
				passwd=self.DB_PWD,
				db=self.DB_NAME,
				charset=self.DB_CHAR
				)
		except Exception as e:
			print "Connection MySQL Database is Wrong!"


