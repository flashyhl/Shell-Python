#!/usr/bin/env python
#-*- coding: utf8 -*-

#-------Author:flashyhl--------#
#-------Date:2015-05-28---------#


import smtplib
import MySQLdb
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

host="xxx.xxx.xxx.xxx"
user="xxxxxxx"
password="xxxxxx"
db="xxxxxxx"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

con_start= """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
</head>
<body bgcolor="bbffff">
<h2>App running error information</h2>
<table border="1"  cellspacing="0" bgcolor="d9ffff" bordercolor="00ff00">
<tr>
  <td><font color="red"><b>AppVersion</b></font></td>
  <td><font color="red"><b>Model</b></font></td>
  <td><font color="red"><b>SystemVersion</b></font></td>
  <td><font color="red"><b>UserId</b></font></td>
  <td><font color="red"><b>ExceptionContent</b></font></td>
  <td><font color="red"><b>CreateTime</b></font></td>
</tr>"""

con_end = """</tr>
</table>
</body>
</html>"""


#today='2015-05-29'
#yesterday='2015-05-28'


errlog="/tmp/app_"+str(yesterday)+"_error_log.html"


mail_useremail = 'alter@mowin.com'
tmpmailto = 'test01@mowin.com,test02@mowin.com'
mail_host = '127.0.0.1'
mail_sub = '邮件报警'
mail_pass = ''

attrname = "app_"+str(yesterday)+"_error_log.html"
haveattr = True
attrpath = errlog
format = 'plain'

mail_user = mail_useremail.split('@')[0]
mail_postfix = mail_useremail.split('@')[1]


def write_file(filename, wstr, mode):
  if mode == 0:
    w_file = open(filename, "w")
    w_file.write(wstr)
    w_file.close
  elif mode == 1:
    w_file = open(filename, "a")
    w_file.write('\n')
    w_file.write(wstr)
  w_file.close


conn=MySQLdb.connect(host=host,user=user,passwd=password,db=db,charset="utf8")
cursor=conn.cursor()
log_sql="select appVersion,model,systemVersion,userId,exceptionContent,createTime from t_app_exception_log where createTime >= '"+str(yesterday)+" 00:00:00' and createTime <= '"+str(today)+" 00:00:00'"
log_cur=cursor.execute(log_sql)
log_rowsize=cursor.rowcount

content=""
if log_rowsize != 0:
   content="yes"
   write_file(errlog,con_start,0)
   errlog_results=cursor.fetchall()
   for row in errlog_results:
     appVersion=str(row[0])
     model=str(row[1])
     systemVersion=str(row[2])
     userId=str(row[3])
     exceptionContent=str(row[4])
     createTime=str(row[5])
     info="<tr>"+'\n'+"   <td>"+appVersion+"</td>"+'\n'+"   <td>"+model+"</td>"+'\n'+"   <td>"+systemVersion+"</td>"+'\n'+"   <td>"+userId+"</td>"+'\n'+"   <td>"+exceptionContent+"</td>"+'\n'+"   <td>"+createTime+"</td>"+'\n'+"</tr>"
     write_file(errlog,info,1)
   write_file(errlog,con_end,1)  
conn.close()
 
if ',' in tmpmailto:
  mailto = tmpmailto.split(',')
else:
  mailto = [tmpmailto,]
  
def send_mail(to_list, sub, content, haveattr, attrpath, attrname):
  me = mail_user + "<" + mail_user+"@"+mail_postfix +">"
  
  # 判断是否有附件
  if (haveattr):
    if (not attrpath):
      print 'Error : no input file of attachments'
      return False
     # 有附件则创建一个带附件的实例
    msg = MIMEMultipart()
 
    # 构造附件
    att = MIMEText(open(attrpath, 'rb').read(),'base64', 'utf8')
    att["Content-Type"] = 'application/octest-stream'
    att["Content-Disposition"] = 'attachment;filename="'+ attrname +'"'
    msg.attach(att)
    msg.attach(MIMEText(content,format,'utf-8'))
    if isinstance(content,unicode):
      content = str(content)
    #msg = MIMEText(content,format,'utf-8')
    #msg["Accept-Language"]="zh-CN"
    #msg["Accept-Charset"]="ISO-8859-1,utf-8"

  else:
    # 无责创建一个文本的实例
    if isinstance(content,unicode):
      content = str(content)
    msg = MIMEText(content,format,'utf-8')
    msg["Accept-Language"]="zh-CN"
    msg["Accept-Charset"]="ISO-8859-1,utf-8"
    
  # 邮件头
  msg['Subject'] = unicode(sub)
  msg['From'] = me
  msg['To'] = ";".join(to_list)
  try:
    # 发送邮件
    s = smtplib.SMTP()
    s.connect(mail_host)
    if (mail_host != '127.0.0.1'):
      s.login(mail_user, mail_pass)
    #print to_list
    s.sendmail(me, to_list, msg.as_string())
    s.close()
    return True
  except Exception, e:
    print str(e)
    return False

if __name__ == '__main__':
  if len(content) <> 0:
    content="你好，管理员！"+'\n'+"       在"+str(yesterday)+"查询到了APP在运行当中出现在 t_app_exception_log 这张数据表中有 "+str(log_rowsize)+" 条错误异常记录，请检查你的配置！"+'\n'
    content=content+"附件是App运行错误信息，请查阅！"+'\n'
    if send_mail(mailto, mail_sub, content, haveattr, attrpath, attrname):
      print "Success"
    else:
      print "Failed"


