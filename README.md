# Shell-Python  一些Bash Shell和python script<br>
Bash shell and python script<br>

说明：<br>
#1、python：<br>
##auto_refresh_aliyun_cdn<br>
##auto_refresh_aliyun_cdn/auto_cdn_refresh.py             #阿里云CDN自动刷新工具(根据阿里云官网提供的CDN API修改)<br>
##auto_refresh_aliyun_cdn/config<br>
##auto_refresh_aliyun_cdn/config/.aliyuncredentials.ini   #访问AccessKey文件<br>
##auto_refresh_aliyun_cdn/config/cdn_url                  #刷新预热列表<br>

##backuplog_analysis<br>
##backuplog_analysis/backuplog_analysis.py                #nginx、mysql慢日志、tomcat日志搜集以及分析错误信息并且发送报警邮件<br>      
##backuplog_analysis/config<br>
##backuplog_analysis/config/collectlog.ini                #配置信息<br>

##monitor_mysql_data<br>
##monitor_mysql_data/app_exception_log.py                 #监控app所产生的在mysql中的错误信息，导出为html文件并且发送报警邮件<br> 
##monitor_mysql_data/monitor_sms_sender.py                #监控app所产生的数据信息并且发送报警邮件<br> 
 
##mysql_data_report<br>
##mysql_data_report/gitreport.py                          #导出每天之前一天的报表信息并且发送邮件<br> 
##mysql_data_report/config<br>
##mysql_data_report/config/click.ini                      #配置文件<br>
            
#2、Bash Shell:<br>
##spliteslog_mysql                                        #切割mysql慢日志文件<br>
##spliteslog_mysql/splitemysqllog.sh<br>             
##spliteslog_mysql/conf<br>
##spliteslog_mysql/conf/mysqlslow<br>
##spliteslog_mysql/info<br>
##spliteslog_mysql/info/mailcontent<br>
##spliteslog_mysql/info/runlog.log<br>

##spliteslog_nginx                                        #切割nginx日志文件<br>
##spliteslog_nginx/splitenginxlog.sh<br>
##spliteslog_nginx/conf<br>
##spliteslog_nginx/conf/nginxlog<br>
##spliteslog_nginx/info<br>
##spliteslog_nginx/info/runlog.log<br>

##spliteslog_tomcat                                       #切割tomcat日志文件<br>
##spliteslog_tomcat/splitetomcatlog.sh<br>
##spliteslog_tomcat/conf<br>
##spliteslog_tomcat/conf/allwebapp<br>
##spliteslog_tomcat/conf/catalina<br>
##spliteslog_tomcatinfo<br>
##spliteslog_tomcatinfo/runlog.log<br>           
