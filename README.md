# Shell-Python  一些Bash Shell和python script
Bash shell and python script

说明：
1、python：         
auto_refresh_aliyun_cdn
auto_refresh_aliyun_cdn/auto_cdn_refresh.py             #阿里云CDN自动刷新工具(根据阿里云官网提供的CDN API修改)
auto_refresh_aliyun_cdn/config
auto_refresh_aliyun_cdn/config/.aliyuncredentials.ini   #访问AccessKey文件
auto_refresh_aliyun_cdn/config/cdn_url                  #刷新预热列表

backuplog_analysis
backuplog_analysis/backuplog_analysis.py                #nginx、mysql慢日志、tomcat日志搜集以及分析错误信息并且发送报警邮件       
backuplog_analysis/config
backuplog_analysis/config/collectlog.ini                #配置信息

monitor_mysql_data
monitor_mysql_data/app_exception_log.py                 #监控app所产生的在mysql中的错误信息，导出为html文件并且发送报警邮件 
monitor_mysql_data/monitor_sms_sender.py                #监控app所产生的数据信息并且发送报警邮件 
 
mysql_data_report
mysql_data_report/gitreport.py                          #导出每天之前一天的报表信息并且发送邮件 
mysql_data_report/config
mysql_data_report/config/click.ini                      #配置文件
            
2、Bash Shell:
spliteslog_mysql                                        #切割mysql慢日志文件
spliteslog_mysql/splitemysqllog.sh             
spliteslog_mysql/conf
spliteslog_mysql/conf/mysqlslow
spliteslog_mysql/info
spliteslog_mysql/info/mailcontent
spliteslog_mysql/info/runlog.log

spliteslog_nginx                                        #切割nginx日志文件
spliteslog_nginx/splitenginxlog.sh
spliteslog_nginx/conf
spliteslog_nginx/conf/nginxlog
spliteslog_nginx/info
spliteslog_nginx/info/runlog.log

spliteslog_tomcat                                       #切割tomcat日志文件
spliteslog_tomcat/splitetomcatlog.sh
spliteslog_tomcat/conf
spliteslog_tomcat/conf/allwebapp
spliteslog_tomcat/conf/catalina
spliteslog_tomcatinfo
spliteslog_tomcatinfo/runlog.log           
