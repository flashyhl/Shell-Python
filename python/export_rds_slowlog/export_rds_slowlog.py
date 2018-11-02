#!/usr/bin/env python
#coding=utf-8

import datetime
import sys, os
import json
import smtplib
import xlwt, xlrd
import ConfigParser
from xlutils.copy import copy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from aliyunsdkcore import client
from aliyunsdkrds.request.v20140815 import DescribeSlowLogsRequest


reload(sys)
sys.setdefaultencoding('utf-8')

SQLServer_list = ['ReportTime', 'SlowLogId', 'SQLServerTotalExecutionCounts', 'SQLServerTotalExecutionTimes', 'TotalLogicalReadCounts', 'TotalPhysicalReadCounts', 'SQLText']
MySQL_list = ['CreateTime', 'SlowLogId', 'SQLId', 'ReturnTotalRowCounts', 'TotalLockTimes', 'MaxExecutionTime', 'MySQLTotalExecutionTimes', 'ReturnMaxRowCount', 'MySQLTotalExecutionCounts', 'DBName', 'ParseTotalRowCounts', u'MaxLockTime', 'ParseMaxRowCount', 'SQLText']

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
std_date = str(yesterday) + 'Z'

mail_host = '127.0.0.1'
mail_sub ='阿里云RDS慢查询日志('+str(yesterday)+')'
mail_pass = ''

inifile = os.getcwd() + '/config/rdsinfo.ini'
import_excel = os.getcwd() + '/doc_excel/' + mail_sub + '.xls'
attrname='Aliyun_RDS_Slowlog(' + str(yesterday) + ').xls'
haveattr = True
attrpath = import_excel
format = 'plain'

mail_useremail = 'alirds@alarm.com'
slowlog_mailto = 'rd@test.com'

contenttype = 0



mail_user = mail_useremail.split('@')[0]
mail_postfix = mail_useremail.split('@')[1]


# 读取ini文件
def read_config(config_file_path, field, key):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(config_file_path)
        result = cf.get(field, key)
    except:
        sys.exit(1)
    return result


# 转换邮件地址格式
def changestr(mailaddr):
    m_str = str(mailaddr)
    if ',' in m_str:
        sendto_mail = m_str.split(',')
    else:
        sendto_mail = [m_str,]
    return sendto_mail

# 判断本地文件是否存在
def fileexist(fname):
    """
    :rtype: object
    """
    if os.path.exists(fname):
        return True
    else:
        return False

#发送邮件
def send_mail(to_list, sub, content, haveattr, attrpath, attrname, contype):
    me = '阿里云RDS慢查询日志' + "<" + mail_user+"@"+mail_postfix +">"

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
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        #if isinstance(content,unicode):
        #    content = unicode(content)
    else:
        # 无则创建一个文本的实例
        if isinstance(content,unicode):
            content = str(content)
        if contype == 0:
            msg = MIMEText(content,'plain','utf-8')
        elif contype == 1:
            msg = MIMEText(content,'html','utf-8')
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"

    # 邮件头
    msg['Subject'] = unicode(sub)
    msg['From'] = me
    msg['To'] = ";".join(sendto)
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

def write_slowlog_toexcel(slowlog, engine, byname, excel_file):
    if engine == 'MySQL':
        sql_list = MySQL_list
    elif engine == 'SQLServer':
        sql_list = SQLServer_list
    if fileexist(excel_file):
        rb = xlrd.open_workbook(excel_file)
        wb = copy(rb)
    else:
        wb = xlwt.Workbook(encoding='utf-8')
    styleboldblack = xlwt.easyxf('font: color-index black, bold on')
    headerStyle = styleboldblack
    ws = wb.add_sheet(byname, cell_overwrite_ok=True)
    # 添加标题
    for list_num in range(len(sql_list)):
        ws.write(0, list_num, sql_list[list_num], headerStyle)
        sql_row = 1
    # 分离出list数据
    for list_value in xrange(len(slowlog)):
        list_data = slowlog[list_value]
        #print list_data
        for dict_num in xrange(len(sql_list)):
            dict_key = list_data[sql_list[dict_num]]
            #print dict_key
            ws.write(sql_row, dict_num, dict_key)
        sql_row = sql_row + 1
    wb.save(excel_file)



def export_slowlog_toexcel(id, name, region, daterange):
    accid = 'sssssssssss'
    acckey = 'xxxxxxxxxxxxxxxxxx'
    clt = client.AcsClient(accid, acckey, region)
    request = DescribeSlowLogsRequest.DescribeSlowLogsRequest()
    request.set_accept_format('json')
    # 设置参数
    request.add_query_param('StartTime', daterange)
    request.add_query_param('EndTime', daterange)
    request.add_query_param('SortKey', 'TotalQueryTimes')
    request.add_query_param('DBInstanceId', id)
    request.add_query_param('PageSize', 100)
    try:
        response = clt.do_action_with_exception(request)
        json_data = json.loads(response)
        #print json_data
        rds_sqlslowlog = json_data['Items']['SQLSlowLog']

        #print rds_sqlslowlog
        rds_engine = json_data['Engine']
        #print rds_engine
        #print len(rds_sqlslowlog)
        if rds_sqlslowlog:
            write_slowlog_toexcel(rds_sqlslowlog, rds_engine, name, import_excel)
        else:
            return False
    except Exception, e:
        print e
        return False
    return True




if __name__ == '__main__':
    sendto = changestr(slowlog_mailto)
    for snum in range(7):
        rds_node = 'rds' + str(snum)
        rds_id = read_config(inifile, rds_node, 'rds_id')
        rds_name = read_config(inifile, rds_node, 'rds_name')
        rds_region = read_config(inifile, rds_node, 'rds_region')
        if export_slowlog_toexcel(rds_id, rds_name, rds_region, std_date) == False:
            continue
    if fileexist(import_excel):
        content = "大家好！" + '\n' + '\n' + "      这是查询到的 " + str(yesterday) + " 阿里云RDS实例的慢查询日志，希望大家能够对于慢日志进行优化！" + '\n'
        content = content + "详情见附件，请查阅！" + '\n'
        if send_mail(sendto, mail_sub, content, haveattr, attrpath, attrname, contenttype):
            print "Success"
        else:
            print "Failed"
    else:
        print "太好了，所有的RDS实例都没有慢日志！"






