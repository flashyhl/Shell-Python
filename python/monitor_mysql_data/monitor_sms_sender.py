#!/usr/bin/env python
#-*- coding: utf8 -*-

#-------Author:flashyhl--------#
#-------Date:2015-05-24---------#


import smtplib
import MySQLdb
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

host="xxx.xxx.xxx.xxx"
user="xxxxxx"
password="xxxxxx"
db="xxxxxxx"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

SMS_info={'61':'刷卡后的提示短信','611':'登陆验证码短信','612':'现金提现短信','613':'验证安全问题短信','614':'设置安全问题短信','615':'找回密码短信','616':'系统后台开通商户账号短信','617':'微信验证短信','618':'提交订单短信','619':'商户通知客户短信','711':'商户服务开通通知短信'}

#today='2015-05-14'
#yesterday='2014-05-13'

conn=MySQLdb.connect(host=host,user=user,passwd=password,db=db,charset="utf8")
cursor=conn.cursor()

#sms_sql="select m_type from ta_message WHERE m_type is NOT NULL GROUP BY m_type"
#sms_cur=cursor.execute(sms_sql)
#sms_results=cursor.fetchall()
content=''
#for rows in sms_results:
for m_key in sorted(SMS_info.keys()):
  #sms_type=str(rows[0])
  sms_type=str(m_key)
  sms_log_sql="select count(*) from ta_message where (msg_id is not null) and m_type='"+sms_type+"' and (oper_time >= '"+str(yesterday)+" 00:00:00' and oper_time <= '"+str(today)+" 00:00:00')"
  #print sms_log_sql
  sms_sql_cur=cursor.execute(sms_log_sql)
  sms_records=cursor.fetchone()
  #print sms_records
  for row in sms_records:
    sms_count=row
    #print sms_count
    if sms_count==0:
     content=content+sms_type+" : "+SMS_info[sms_type]+'\n'
    else:
     continue
conn.close()

mail_useremail = 'alert@mowin.com'
tmpmailto = 'test@mowin.com'
mail_host = '127.0.0.1'
mail_sub = '未使用短信类型报警'
mail_pass = ''

attrname = None
haveattr = False
attrpath = None
format = 'plain'

mail_user = mail_useremail.split('@')[0]
mail_postfix = mail_useremail.split('@')[1]
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
    msg.attach(MIMEText(content))
  else:
    # 无则创建一个文本的实例
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
    content="你好，管理员！"+'\n'+"      以下短信类型在"+str(yesterday)+"未查询到任何记录，请检查你的配置！"+'\n'+content
    if send_mail(mailto, mail_sub, content, haveattr, attrpath, attrname):
      print "Success"
    else:
      print "Failed"
