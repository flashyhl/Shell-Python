#!/bin/env python
# -*- coding: utf8 -*-

#-------Author:flashyhl--------#
#-------Date:2016-01-18---------#

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko
import socket
import os
import sys
from re import compile, IGNORECASE
from stat import S_ISDIR
import datetime
import time
import ConfigParser
import subprocess
import pipes
import socket
import tarfile
import shutil

reload(sys)
sys.setdefaultencoding('utf-8')

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

conlog_info = ''
conerr_info = ''
weblog_url = 'http://xxx.xxx.xxx.xxx:5500/'
html_head = '''<html>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=gb2312'>
<meta http-equiv='Content-Language' content='zh-cn' />
</head>
<title>Tomcat错误日志或者MySQL慢日志信息</title>
<body>
<font size='2'><p style='margin:5px'>你好，管理员！</p></font>'''
mail_content = html_head + "<font size='2'><p style='margin:5px'>&nbsp;&nbsp;&nbsp;&nbsp;在 " + str(yesterday) + " 搜索到以下服务器上有错误的日志信息，错误日志信息如下：</p></font>" + '\n'
html_foot = '''</body>
</html>'''

mail_useremail = 'Weblog@mowin.com'
log_mailto = 'test@mowin.com'
err_mailto = 'test01@mowin.com,test02@mowin.com,test03@mowin.com,test04@mowin.com'
mail_host = '127.0.0.1'
create_log_sub = '创建日志错误'
errlog_mail_sub = 'Tomcat错误日志以及MySQL慢日志信息'
mail_pass = ''

attrname = None
haveattr = False
attrpath = None

mail_user = mail_useremail.split('@')[0]
mail_postfix = mail_useremail.split('@')[1]

user_name = 'test04'
rsa_file = '/root/.ssh/id_rsa'
inifile = os.getcwd() + '/config/collectlog.ini'
ck_log = '/tmp/checkinfo.log'
err_mail = '/tmp/errmail.log'
el_file = '/backup/collectlog/dictlog'
port=22

# 遍历出子目录,在本地创建
def sftp_walk(remotepath):
    # Kindof a stripped down  version of os.walk, implemented for
    # sftp.  Tried running it flat without the yields, but it really
    # chokes on big directories.
    path=remotepath
    files=[]
    folders=[]
    for f in sftp.listdir_attr(remotepath):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
        else:
            files.append(f.filename)
    # print (path,folders,files)
    yield path,folders,files
    for folder in folders:
        new_path=os.path.join(remotepath,folder)
        for x in sftp_walk(new_path):
            yield x

# 从远程copy目录到本地
def get_all(remotepath,localpath):
    #  recursively download a full directory
    #  Harder than it sounded at first, since paramiko won't walk
    #
    # For the record, something like this would gennerally be faster:
    # ssh user@host 'tar -cz /source/folder' | tar -xz
    # print remotepath,localpath
    sftp.chdir(os.path.split(remotepath)[0])
    parent=os.path.split(remotepath)[1]
    # print parent
    try:
        os.mkdir(localpath)
    except:
        pass
    for walker in sftp_walk(parent):
        try:
            os.mkdir(os.path.join(localpath,walker[0]))
        except:
            pass
        for file in walker[2]:
            sftp.get(os.path.join(walker[0],file),os.path.join(localpath,walker[0],file))

#判断远程路径是否为目录
def isdir(path):
    try:
        return S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False

#移除远程服务器目录
def remote_rmdir(re_path):
    files = sftp.listdir(path=re_path)

    for f in files:
        filepath = os.path.join(re_path, f)
        if isdir(filepath):
            remote_rmdir(filepath)
        else:
            sftp.remove(filepath)

    sftp.rmdir(re_path)


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

# 写入ini文件
def write_config(config_file_path, field, key, value):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(config_file_path)
        cf.set(field, key, value)
        cf.write(open(config_file_path,'w'))
    except:
        sys.exit(1)
    return True

#写入日志或邮件信息文件
def write_file(filename, wstr, mode):
    if mode == 0:
        w_file = open(filename, "w")
        w_file.write(wstr)
        w_file.close
    elif mode == 1:
        w_file = open(filename, "a")
        #w_file.write('\n')
        w_file.write(wstr)
    w_file.close

#分析文件找出异常的行
def analysis_log(log_file,errlog_file):
    #匹配的错误信息关键字的正则表达式
    debug = compile(r'(?!\[DEBUG\])',IGNORECASE)
    info = compile(r'(?!\[INFO\])',IGNORECASE)
    pattern = compile(r'Exception|^\t+\bat\b|^\[ERROR\]')
    error_list = []
    try:
        data = open(log_file,'r')
    except:
        exit()
    for line in data:
        if debug.match(line):
            if info.match(line):
                if pattern.search(line):
                    write_file(errlog_file,line,1)
    data.close()

#判断远程服务器中的目录是否存在
def dictexist(remote_name,remote_ip,remote_path):
    ssh_host = remote_name + '@' + str(remote_ip)
    d_path = remote_path
    resp = subprocess.call(
        ['ssh', ssh_host, 'test -d ' + pipes.quote(d_path)])
    if resp == 0:
        return True
    else:
        return False

#判断本地文件是否存在
def fileexist(fname):
    """
    :rtype: object
    """
    if os.path.exists(fname):
        return True
    else:
        return False

#判断远程服务器是否存在
def pingServerCall(remote_ip):
    fnull = open(os.devnull, 'w')
    result = subprocess.call('ping '+ remote_ip +' -c 3', shell = True, stdout = fnull, stderr = fnull)
    if result:
          return True
    else:
        return True
    fnull.close()

#检测ssh是否正常，即检测ssh的22端口是否正常
def check_aliveness(remote_ip, remote_port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((remote_ip, remote_port))
        return True
    except Exception:
          return False
    finally:
        sk.close()
    return False

#遍历搜索文件
def traversal_file(src_dict,filter_word):
    for rt, dirs, files in os.walk(src_dict):
        file = files
    fw = str(filter_word)
    tomcat_file = filter(lambda x:fw in x,file)
    return tomcat_file

# 压缩文件为tar.gz
def compress_file(output_file, source_dir):
    tar = tarfile.open(output_file,"w:gz")
    for root,dir,files in os.walk(source_dir):
        for file in files:
            pathfile = os.path.join(root, file)
            tar.add(pathfile, arcname=file)
    tar.close()

# 解压TarBall文件
def extract_file(tar_path, target_path):
    try:
        tar = tarfile.open(tar_path, "r:gz")
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, target_path)
        tar.close()
    except Exception, e:
        raise Exception, e

# 删除目录下所有的文件以及目录
def removeDir(dirPath):
    """

    :rtype: object
    """
    if not os.path.isdir(dirPath):
        return
    files = os.listdir(dirPath)
    try:
        for file in files:
            filePath = os.path.join(dirPath, file)
            if os.path.isfile(filePath):
                os.remove(filePath)
            elif os.path.isdir(filePath):
                removeDir(filePath)
        os.rmdir(dirPath)
    except Exception, e:
        print e

#发送邮件
def send_mail(to_list, sub, content, haveattr, attrpath, attrname, contype):
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


if __name__ == '__main__':
    for snum in range(1,11):
        cl_snum='CollectLog'+str(snum)
        # print cl_snum
        # 获取ip地址
        t_conerr_info = ''
        ip_addr = read_config(inifile,cl_snum,'host_ip')
        #print ip_addr
        # 获取源地址、目标地址、服务类型信息
        src_path = read_config(inifile,cl_snum,'backup_path')
        dest_path = read_config(inifile,cl_snum,'local_path')
        ser_type = read_config(inifile,cl_snum,'backup_type')
        if pingServerCall(ip_addr):
            if check_aliveness(ip_addr,port):
                # 连接ssh
                key=paramiko.RSAKey.from_private_key_file(rsa_file)
                t = paramiko.Transport((ip_addr, port))
                t.connect(username=user_name, pkey=key)
                sftp = paramiko.SFTPClient.from_transport(t)
                src_path = src_path + os.sep + str(yesterday)
                if dictexist(user_name,ip_addr,src_path):
                    dest_path = dest_path + os.sep + str(ip_addr) + os.sep
                    get_all(src_path,dest_path)
                    remote_rmdir(src_path)
                    if ser_type == 'Tomcat-App':
                        tomtar_path = dest_path + os.sep + str(yesterday)
                        tomtar_file = traversal_file(tomtar_path,'tomcat.')
                        list_len = len(tomtar_file)
                        if list_len <> 0:
                            for fl in range(list_len):
                                tarball_file = dest_path + str(yesterday) + os.sep + tomtar_file[fl]
                                extract_file(tarball_file,el_file)
                                ext_list = traversal_file(el_file,'tomcat.')
                                #print ext_list
                                ext_file = el_file + os.sep + ext_list[0]
                                err_file = 'error.' + ext_list[0]
                                err_log_path = el_file + os.sep + err_file
                                analysis_log(ext_file,err_log_path)
                                if fileexist(err_log_path):
                                    tomerr_log = err_file + '.tar.gz'
                                    compress_errlog = dest_path + str(yesterday) + os.sep + tomerr_log
                                    os.remove(ext_file)
                                    compress_file(compress_errlog,el_file)
                                    if len(t_conerr_info) == 0:
                                        t_conerr_info = "<font size='2'><p style='margin:5px'>" + str(ip_addr) + ' 上面 ' + str(yesterday) + ' 的Tomcat错误日志已生成！请查明原因！' + '</p></font>' + '\n'
                                        conerr_info = conerr_info + t_conerr_info
                                        conerr_info = conerr_info + "<font size='2' color='red'><p style='margin:5px'>下载地址：<a href='" + weblog_url + str(ip_addr) + '/' + str(yesterday) + '/' + tomerr_log + "'>" + tomerr_log + '</a></p></font>\n'
                                    else:
                                        conerr_info = conerr_info + "<font size='2' color='red'><p style='margin:5px'>下载地址：<a href='" + weblog_url + str(ip_addr) + '/' + str(yesterday) + '/' + tomerr_log + "'>" + tomerr_log + '</a></p></font>\n'
                                    #write_file(err_mail,ser_info,0)
                                    removeDir(el_file)
                                else:
                                    removeDir(el_file)
                        else:
                             conlog_info = conlog_info + str(ip_addr) + ' 上面 ' + str(yesterday) + ' 的Tomcat日志不存在！' + str(src_path) + ' 中没有Tomcat文件生成，请检查你的配置！' + '\n'
                             #write_file(ck_log,ser_info,0)
                    elif ser_type == 'Mysql':
                         mysql_path = dest_path + os.sep + str(yesterday)
                         mysql_file = traversal_file(mysql_path,'mysqlSlow')
                         mysql_slow_file = mysql_file[0]
                         t_conerr_info = "<font size='2'><p style='margin:5px'>" + str(ip_addr) + ' 上面 ' + str(yesterday) + ' 的MySQL慢日志已生成！请查明原因！' + '</p></font>' + '\n'
                         conerr_info = conerr_info + t_conerr_info
                         conerr_info = conerr_info + "<font size='2' color='red'><p style='margin:5px'>下载地址：<a href='" + weblog_url + str(ip_addr) + '/' + str(yesterday) + '/' + mysql_slow_file + "'>" + mysql_slow_file + '</a></p></font>\n'
                else:
                     conlog_info = conlog_info + str(ip_addr) + ' 上面 ' + str(yesterday) + ' 的切割日志目录 ' + str(src_path) + ' 中没有文件生成，请检查你的配置！' + '\n'
                     #write_file(ck_log,ser_info,0)

            else:
                 conlog_info = conlog_info + str(ip_addr) + ' 上的 ' + str(port) + ' 端口有问题，需要紧急处理！' + '\n'
                 #write_file(ck_log,ser_info,0)
                 continue
        else:
             conlog_info = conlog_info + '请注意，服务器 ' + str(ip_addr) + ' 已经宕机，需要紧急处理！' + '\n'
             #write_file(ck_log,ser_info,0)
             continue

    if len(conerr_info) <> 0:
        conerr_info = mail_content + conerr_info + html_foot
        sendto = changestr(err_mailto)
        if send_mail(sendto, errlog_mail_sub, conerr_info, haveattr, attrpath, attrname, 1):
            print "Error log mail send success!"
        else:
            print "Error log mail send failed!"
        #print conerr_info

    if len(conlog_info) <> 0:
        conlog_info = '你好，管理员！\n' + conlog_info
        sendto = changestr(log_mailto)
        if send_mail(sendto, create_log_sub, conlog_info, haveattr, attrpath, attrname, 0):
            print "Create log mail send success!"
        else:
            print "Create log mail send failed!"
        #print conlog_info
