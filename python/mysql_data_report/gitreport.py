#!/usr/bin/env python
#-*- coding: utf8 -*-

#-------Author:flashyhl--------#
#-------Date:2016-01-18---------#


import smtplib
import MySQLdb
import xlwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header  
from email import encoders 
import sys
import datetime
import os,time  
import ConfigParser

#--用户当日发的红包
sql_arr0='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
 when userId=10000633 then 'test06'
end
用户当日发的红包,FORMAT(sum(redSumAmount)/100,2)  金额,sum(redNumber)  红包数,sum(redLeadNumber) 一级领的个数,sum(shareLeadNumber) 一级分享的个数,
sum(exRedNumber) 二级总个数, sum(exLeadNumber) 二级领取个数,
CONCAT(FORMAT((sum(shareLeadNumber)/sum(redNumber)*100),2),'%') 一级红包转发率,CONCAT(FORMAT((sum(exLeadNumber)/sum(exRedNumber)*100) ,2),'%') 二级红包领取率
from (
select userId,redNumber,redSumAmount,redLeadNumber,
(select count(id) from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id) shareLeadNumber,
(select sum(redNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exRedNumber,
(select sum(redLeadNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exLeadNumber
from ukardweb.t_extension_redPool t where userId in(10000603,10000635,10000636,10000640,10000645,10000633) 
and redState!=4 and date_format(createTime,'%Y%m%d')  = date_format(date_add(now(), interval -1 day),'%Y%m%d')
) a 
group by userId
order by userId;'''

#--用户累计发的红包
sql_arr1='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
when userId=10000633 then 'test06'
end
用户累计发的红包,FORMAT(sum(redSumAmount)/100,2)  金额,sum(redNumber)  红包数,sum(redLeadNumber) 一级领的个数,sum(shareLeadNumber) 一级分享的个数,
sum(exRedNumber) 二级总个数, sum(exLeadNumber) 二级领取个数,
CONCAT(FORMAT((sum(shareLeadNumber)/sum(redNumber)*100),2),'%') 一级红包转发率,CONCAT(FORMAT((sum(exLeadNumber)/sum(exRedNumber)*100) ,2),'%') 二级红包领取率
from (
select userId,redNumber,redSumAmount,redLeadNumber,
(select count(id) from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id) shareLeadNumber,
(select sum(redNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exRedNumber,
(select sum(redLeadNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exLeadNumber
from ukardweb.t_extension_redPool t where userId in(10000603,10000635,10000636,10000640,10000645,10000633) and redState!=4
) a 
group by userId
order by userId;'''

#--用户当日徒弟数
sql_arr2='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
when userId=10000633 then 'test06'
end
用户当日徒弟数,count(id) as 徒弟数 from (
select id,t1.th_id as userId from 
(select th_id,sd_id from ukardweb.t_teacher_student where th_id in (10000603,10000635,10000636,10000640,10000645,10000633)) t1 left join ukardweb.t_user t   on t.id = t1.sd_id 
where  date_format(regist_time,'%Y%m%d')  = date_format(date_add(now(), interval -1 day),'%Y%m%d')
) a 
group by userId
order by userId;'''

#--用户累计徒弟数
sql_arr3='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
when userId=10000633 then 'test06'
end
用户累计徒弟数,count(id) as 徒弟数 from (
select id,t1.th_id as userId from 
(select th_id,sd_id from ukardweb.t_teacher_student where th_id in (10000603,10000635,10000636,10000640,10000645,10000633)) t1 left join ukardweb.t_user t   on t.id = t1.sd_id 
) a 
group by userId
order by userId;'''

#--用户当日徒弟发出的红包
sql_arr4='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
when userId=10000633 then 'test06'
end
用户当日徒弟发出的红包,FORMAT(sum(redSumAmount)/100,2)  金额,sum(redNumber)  红包数,sum(redLeadNumber) 一级领的个数,sum(shareLeadNumber) 一级分享的个数,
sum(exRedNumber) 二级总个数, sum(exLeadNumber) 二级领取个数,
CONCAT(FORMAT((sum(shareLeadNumber)/sum(redNumber)*100),2),'%') 一级红包转发率,CONCAT(FORMAT((sum(exLeadNumber)/sum(exRedNumber)*100) ,2),'%') 二级红包领取率
from (
select t1.th_id as userId,redNumber,redSumAmount,redLeadNumber,
(select count(id) from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id) shareLeadNumber,
(select sum(redNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exRedNumber,
(select sum(redLeadNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exLeadNumber
from
ukardweb.t_extension_redPool t join
(select id,t1.th_id from 
(select th_id,sd_id from ukardweb.t_teacher_student where th_id in (10000603,10000635,10000636,10000640,10000645,10000633)) t1 left join ukardweb.t_user t   on t.id = t1.sd_id ) t1 on t.userId = t1.id
where redState!=4 and date_format(createTime,'%Y%m%d')  = date_format(date_add(now(), interval -1 day),'%Y%m%d')
) a
group by userId
order by userId;'''

#--用户累计徒弟发出的红包
sql_arr5='''select 
case when userId=10000603 then 'test01'
 when userId=10000636 then 'test02'
 when userId=10000640 then 'test03'
 when userId=10000635 then 'test04'
 when userId=10000645 then 'test05'
when userId=10000633 then 'test06'
end
用户累计徒弟发出的红包,FORMAT(sum(redSumAmount)/100,2) 金额,sum(redNumber)  红包数,sum(redLeadNumber) 一级领的个数,sum(shareLeadNumber) 一级分享的个数,
sum(exRedNumber) 二级总个数, sum(exLeadNumber) 二级领取个数,
CONCAT(FORMAT((sum(shareLeadNumber)/sum(redNumber)*100),2),'%') 一级红包转发率,CONCAT(FORMAT((sum(exLeadNumber)/sum(exRedNumber)*100) ,2),'%') 二级红包领取率
from (
select  t1.th_id as userId,redNumber,redSumAmount,redLeadNumber,
(select count(id) from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id) shareLeadNumber,
(select sum(redNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exRedNumber,
(select sum(redLeadNumber) from ukardweb.t_external_redPool where extensionId in(select id from ukardweb.t_extension_redDetail where redState=5 and redPoolId=t.id)) exLeadNumber
from
ukardweb.t_extension_redPool t join
(select id,t1.th_id from 
(select th_id,sd_id from ukardweb.t_teacher_student where th_id in (10000603,10000635,10000636,10000640,10000645,10000633)) t1 left join ukardweb.t_user t   on t.id = t1.sd_id ) t1 
on t.userId = t1.id
where redState!=4
) a
group by userId
order by userId;'''


#--可提现用户汇总数
sql_arr6='''select count(username) 可提现用户汇总数,sum(commission_residue)/100 可提现金额,sum(okAmount)/100 已提现金额,sum(waitAmount)/100 正在提现金额,sum(closeAmount)/100 提现失败金额 from(
select username,nickname,commission_residue, okAmount,waitAmount,closeAmount from (
select id,username,nickname,commission_residue from ukardweb.t_user where commission_residue+commission_withdraw>0 and id not in(66,77,88)
) t left join (
select user_id,sum(amount) okAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state=1 group by user_id
) t1 on t.id=t1.user_id left join 
(
select user_id,sum(amount) waitAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state in (0,3) group by user_id)
 t2 on t.id=t2.user_id left join (
select user_id,sum(amount) closeAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state=2 group by user_id) t3
on t.id = t3.user_id
) a;'''

#可提现用户明细手机号
sql_arr7='''select username 可提现用户明细手机号,
case when first_login_time is null then '未登录' else '已登录' end 是否登录,
nickname 昵称,commission_residue/100 可提现金额,okAmount/100 已提现金额,waitAmount/100 正在提现金额,closeAmount/100 提现失败金额 from (
select id,username,nickname,commission_residue,first_login_time from ukardweb.t_user where commission_residue+commission_withdraw>0
) t left join (
select user_id,sum(amount) okAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state=1 group by user_id
) t1 on t.id=t1.user_id left join 
(
select user_id,sum(amount) waitAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state in (0,3) group by user_id)
 t2 on t.id=t2.user_id left join (
select user_id,sum(amount) closeAmount from ukardweb.t_user_withdraw where moneyType=9 and w_state=2 group by user_id) t3
on t.id = t3.user_id where id not in(66,77,88);'''

#--用户金额对账报表
sql_arr8='''select a/100 微信红包总金额,b/100 体验金充值发出的红包被领取总额,c/100 微信与余额发出的红包被领总额,d/100 用户消费的红包被领总额,e/100 用户用余额发的大咖红包,
         f/100 用户提现金额,g/100 余额发出的红包总额, h/100 用户账户余额总额,m/100 余额退回,n/100 微信退回,(e+f+h)/100 用户余额总计,(n+b+c+d+m-g)/100 用户领取总额,
((e+f+h)-(n+b+c+d+m-g))/100 差金额 from (
select 1 id, ifnull(sum(redSumAmount)-sum(transFee),0) a  from ukardweb.t_extension_redPool where source!=2 and redState!=4) t join
(
select 1 id, ifnull(sum(amount),0) b  from (
select sum(before_amount) amount from t_user_return_commission t join (
select id from t_extension_redDetail where redType=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where return_state=1
union all 
select sum(amount) amount from t_external_redDetail t join (
select id from t_extension_redDetail where redType=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where redState=3
) a) t1 on t.id =t1.id join
(
select 1 id, ifnull(sum(amount),0) c  from (
select sum(before_amount) amount from t_user_return_commission t join (
select id from t_extension_redDetail where redType!=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where return_state=1
union all 
select sum(amount) amount from t_external_redDetail t join (
select id from t_extension_redDetail where redType!=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where redState=3
union all 
select sum(amount) amount from t_internal_redDetail t join (
select id from t_extension_redDetail where redType!=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where redState=3
union all 
select sum(redAmount) amount from t_returnCash_redpool t join (
select id from t_extension_redDetail where redType!=26 and redState in (3,4,5)) t1 on t.extensionId = t1.id where redState=3
) a) t2 on t.id =t2.id join
(
select 1 id, ifnull(sum(amount),0) d  from (
select sum(before_amount) amount from t_user_return_commission where tran_id!=-1 and return_state=1
union all 
select sum(amount) amount from t_external_redDetail where busiId is not null and redState=3
union all 
select sum(amount) amount from t_internal_redDetail where busiId is not null and redState=3
union all 
select sum(redAmount) amount from t_returnCash_redpool where busiId is not null and redState=3
) a) t3 on t.id =t3.id join
(
select 1 id, ifnull(-sum(experienceAmount),0) e  from (
select userid,sum(experienceAmount) experienceAmount from t_experience_detail where experienceType=1 group by userid 
) a where a.experienceAmount<0) t4 on t.id =t4.id join
(
select 1 id, ifnull(sum(amount),0) f  from ukardweb.t_user_withdraw  where w_state in (0,1,3) and moneyType=9 ) t5 on t.id =t5.id join
(
select 1 id, ifnull(sum(redSumAmount),0)  g  from ukardweb.t_extension_redPool where  redType!=26 and source=2 and redState!=4) t6 on t.id =t6.id join
(
select 1 id, ifnull(sum(commission_residue),0) h  from t_user ) t7 on t.id =t7.id join
(
select 1 id, ifnull(sum(refundAmount),0) m  from t_extension_redPool where auditStatus=1 and redType=21 and source=2) t8 on t.id =t8.id join
(
select 1 id, ifnull(sum(refundAmount),0) n  from t_extension_redPool where auditStatus=1 and redType=21 and source=1) t9 on t.id =t9.id;'''

#--体验金金额对账报表
sql_arr9='''select a/100 体验金发出总额,b/100 体验金被回收总额,c/100 未发的体验金总额,d/100 用户发的体验金总额,(a-(b+c+d))/100 差金额 from  (
select 1 id, ifnull(sum(experienceAmount),0) a  from t_experience_detail where experienceType=0 and experienceAmount>0) t join 
(
select 1 id, ifnull(sum(experienceAmount),0) b  from t_experience_detail where experienceType=5) t1 on t.id =t1.id join
(
select 1 id, ifnull(sum(experienceAmount),0) c from t_user ) t2 on t.id = t2.id join
(
select 1 id, ifnull(-sum(experienceAmount),0) d  from t_experience_detail where experienceType=0 and experienceAmount<0) t3 on t.id = t3.id;'''

#--大咖充值金额对账报表
sql_arr10='''select a/100 充值金额发出总额,b/100 用户发的充值总额,c/100 充值金被回收总额,d/100 用户用余额发的大咖红包,e/100 未发的充值总额,((a+d)-(b+c+e))/100 差金额 from (
select 1 id, ifnull(sum(experienceAmount) ,0) a  from t_experience_detail where experienceType=1 and experienceAmount>0) t join 
(
select 1 id, ifnull(-sum(experienceAmount),0) b from t_experience_detail where experienceType=1 and experienceAmount<0) t1 on t.id =t1.id join
(
select 1 id,ifnull(sum(experienceAmount),0) c  from t_experience_detail where experienceType=6) t2 on t.id = t2.id join
(
select 1 id,ifnull(-sum(experienceAmount),0) d  from (
select userid,sum(experienceAmount) experienceAmount from t_experience_detail where experienceType=1 group by userid 
) a where a.experienceAmount<0) t3 on t.id = t3.id join
(
select 1 id,ifnull(sum(rechargeAmount),0) e  from t_user ) t4 on t.id = t4.id;'''

#--点击H5页面总数
sql_arr11='''select sum(a) H5页面打开总次数 from (
select sum(openCount) a  from t_extension_redPool
union all
select sum(openCount) a from t_external_redPool
) b;'''

reload(sys)
sys.setdefaultencoding('utf-8')

host="xxx.xxx.xxx.xxx"
user="xxxxxx"
password="xxxxxxx"
db="xxxxxxx"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

mail_useremail = 'report@mowin.com'
tmpmailto = 'test01@mowin.com,test02@mowin.com'

mail_host = '127.0.0.1'
#mail_sub ='report_'+str(yesterday)
mail_sub ='销售统计报表('+str(yesterday)+')'
mail_pass = ''

inifile = os.getcwd() + '/config/click.ini'

def read_config(config_file_path, field, key):   
    cf = ConfigParser.ConfigParser()  
    try:  
        cf.read(config_file_path)  
        result = cf.get(field, key)  
    except:  
        sys.exit(1)  
    return result  
  
def write_config(config_file_path, field, key, value):  
    cf = ConfigParser.ConfigParser()  
    try:  
        cf.read(config_file_path)  
        cf.set(field, key, value)  
        cf.write(open(config_file_path,'w'))  
    except:  
        sys.exit(1)
    return True



import_excel = '/tmp/销售统计报表('+str(yesterday)+').xls'
attrname='Sales Report('+str(yesterday)+').xls'
haveattr = True
attrpath = import_excel
format = 'plain'

mail_user = mail_useremail.split('@')[0]
mail_postfix = mail_useremail.split('@')[1]

conn=MySQLdb.connect(host=host,user=user,passwd=password,db=db,charset="utf8")
cursor=conn.cursor()

wb = xlwt.Workbook(encoding = 'utf-8')

for sql in range(12):
  sqln=sql
  exe_sql='sql_arr'+str(sqln)
  sql_cur = cursor.execute(eval(exe_sql))
  sql_rowsize=cursor.rowcount
  sql_col = cursor.description
  col_num=int(len(sql_col))
  ws = wb.add_sheet(sql_col[0][0],cell_overwrite_ok = True)
  for head in range(col_num):
    #ws.write(0,head,sql_col[head][0],f_style)
    ws.write(0,head,sql_col[head][0])
  sql_row=1
  if sql_rowsize != 0:
    sql_results=cursor.fetchall()
    for row in sql_results:
       for context in range(col_num):
          row_con=str(row[context])
          if sql != 11:
            if row_con !='None':
              ws.write(sql_row,context,row_con)
            else:
              ws.write(sql_row,context,"")
          else:
              read_click=read_config(inifile,'yesterday_info','click_num')
              day_total=int(row_con)-int(read_click)
              if day_total != 0:
                ws.write(sql_row,context,str(day_total))
              else:
                ws.write(sql_row,context,"")
              write_click = write_config(inifile,'yesterday_info','click_num',row_con)
       sql_row=sql_row+1
  else:
    for context in range(col_num):
       ws.write(sql_row,context,"")
conn.close()
content="Sender"
wb.save(import_excel)

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
  #print msg['To']
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
    content="你好，管理员！"+'\n'+'\n'+"    这是查询到的"+str(yesterday)+"的红包销售统计报表！"+'\n'
    content=content+"详情见附件，请查阅！"+'\n'
    if send_mail(mailto, mail_sub, content, haveattr, attrpath, attrname):
      print "Success"
    else:
      print "Failed"


