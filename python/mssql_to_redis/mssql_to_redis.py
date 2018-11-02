# -*- coding:utf-8 -*-

#!/usr/bin/python env

import redis

import pymssql

import time

sql = '''SELECT  a.mebid, a.Mobile, a.MebType, a.ActivitySource  from  meb_Main a left join meb_Type b on a.MebType = b.MebTypeID  WHERE  a.state in(2,4) and b.IsCorpType = 2 order BY mebid  '''
count = 0
class MSSQL:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise(NameError,"没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接        self.conn.close()
        return resList

    def ExecNonQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()class Redis:
    def __init__(self, host, pwd, port, db):
        self.host = host
        self.pwd = pwd
        self.port = port
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise(NameError, "没有设置数据库信息")
        self.conn = redis.Redis(host=self.host, password=self.pwd, port=self.port, db=self.db)
        return self.conn

    def InsertData(self,key,value):
        redisconn = self.__GetConnect()
        redisconn.set(key,value)



ms = MSSQL(host="xxx.xxx.xxx.xxx",user="sa",pwd="xxxxxxxxx",db="center")
#redis_conn = redis.Redis(host="xxx.xxx.xxx.xxx",pwd="xxxxxxxxxxxxxxx",port=63001,db=10)
redis_conn = redis.Redis(host="xxx.xxx.xxx.xxx",password="xxxxxxxxxx",port=63001,db=10)
pipe = redis_conn.pipeline()
reslist = ms.ExecQuery(sql)
start = time.time()for record in reslist:
    count = count + 1    phone = record[1]
    if str(record[3]) == "None":
        activitySource = '{"activitySource":"",'    else:
        activitySource = '{"activitySource":"' + str(record[3]) + '",'    #print activitySource    mebType = '"mebType":' + str(record[2]) + ','    #print  mebType    mebId = '"mebId":' + str(record[0]) + '}'    #print mebId    redis_val = '%s%s%s' % (activitySource, mebType, mebId)
    #print redis_val     result = pipe.set(phone,redis_val)
    export_num = divmod(count, 1000)
    if export_num[1] == 0:
        pipe.execute()
        cost_time = time.time() - start
        print "已经导入: %s 条数据，耗费时间为 %s " % (count, cost_time)print str(count)
pipe.execute()