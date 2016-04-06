#!/bin/bash
#export LANG="zh_CN.UTF-8"

#=========生产环境端使用=============#
#=======Author:flashyhl=============#
#========Date:2015-05-25=============#

cata_log_base=/application/tomcat/logs
catalina_log_file=$cata_log_base/catalina.out
allwebapp_path=/application/applog
local_path=/opt/shell/spliteslog
log_conf=$local_path/conf
catlina_cut=catalina
allwebapp_cut=allwebapp
backup_base=/application/backuplog/cutdaylog
backup_path=$backup_base/formal
all_log_path=$backup_base/interim
runlog=$local_path/info/runlog.log
mailcontent=$local_path/info/mailcontent

#定义时间日期
yesterday_date=`date -d yesterday +%Y%m%d`   #YYYYMMDD
yes_date_path=`date -d yesterday +%Y-%m-%d`  #YYYY-MM-DD

localhost_access=localhost_access_log.$yes_date_path.txt
web_access=$cata_log_base/$localhost_access

#定义邮件发送地址
mailto=test01@mowin.com

#获取当前服务器IP地址
curr_Ip=`/sbin/ifconfig eth0 | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`

#判断web访问日志是否存在
if [ -e $web_access ];then
  size=`wc -c $web_access | awk '{print $1}'`
  if [ $size -ne 0 ];then
   mv $web_access $all_log_path/
  fi
fi

#判断tomcat的日志是否生成
size=`wc -c $catalina_log_file | awk '{print $1}'`
if [ $size -eq 0 ];then
 #echo -e "你好，管理员！\n" > $mailcontent
 #echo -e "\t    $curr_Ip上面$yes_date_path 的Tomcat日志($catalina_log_file)没有生成，文件为空，请检查你的配置！" >> $mailcontent
 #cat $mailcontent | mail -s "Tomcat日志生成错误！" $mailto  
 exit 1
else
 /usr/sbin/logrotate -f $log_conf/$catlina_cut
fi
sleep 3
#判断webapp的日志是否生成
for webapplog in `ls -1 $allwebapp_path/*.log`
 do
  size=`wc -c $webapplog | awk '{print $1}'`
  if [ $size -ne 0 ];then
   /usr/sbin/logrotate -f $log_conf/$allwebapp_cut
   break
  fi
done  
sleep 3
#判断切割的文件是否生成，如果生成就重命名，没有生成就报警
filecount=`ls -A $all_log_path | wc -l`
if [ $filecount -ne 0 ];then
 for logfile in `ls -1 $all_log_path`
  do
    if [[ $logfile =~ "$localhost_access" ]];then
      applog=`echo $logfile | awk -F"." '{print $1"."$3}'` 
      mv $all_log_path/$logfile $all_log_path/$applog.$yesterday_date
    else  
      applog=`echo $logfile | awk -F"." '{print $1"."$2}'` 
      mv $all_log_path/$logfile $all_log_path/tomcat.$applog.$yesterday_date
    fi  
 done
else
 #echo -e "你好，管理员！\n" > $mailcontent
 #echo -e "\t    $curr_Ip上面$yes_date_path 的切割日志目录($all_log_path)中没有文件生成，请检查你的配置！" >> $mailcontent
 #cat $mailcontent | mail -s "切割日志生成错误！" $mailto  
 exit 1 
fi

#创建tar包目录
if [ ! -d $backup_path/$yes_date_path ];then
  mkdir $backup_path/$yes_date_path -p
fi

for logfile in `ls -1 $all_log_path`
  do
    tar czfv $backup_path/$yes_date_path/$logfile.tar.gz -C $all_log_path $logfile
done

if [[ $? = 0 ]]; then
  rm -rf $all_log_path/*
  chown -R test01.test01 $backup_path/*
  echo "$yes_date_path   日志信息转存成功" >> $runlog
  chown -R test01.test01 $runlog
fi
