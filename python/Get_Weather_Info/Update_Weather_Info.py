__author__ = "flashyhl"
#!/usr/bin/python
#-*- coding: UTF-8 -*-

import sys
import Db_Conn
import Get_Weather_Info
import Common

reload(sys)
sys.setdefaultencoding('utf8')

def Insert_New_Data():
	db = Db_Conn.Mydb_Conn()
	insert_new_data = '''
INSERT INTO `nx_dict_area_weather`
            (
             `city_id`,
             `area_id`,
             `city_name`,
             `area_name`,
             `ctime`)
SELECT `f`.`city_id`, `f`.`area_id`, `c`.`name`, `a`.`name`, UNIX_TIMESTAMP() FROM `nx_farm` AS `f`
INNER JOIN `nx_dict_area` AS `c` ON `c`.id = f.city_id
INNER JOIN `nx_dict_area` AS `a` ON `a`.id = f.area_id
WHERE `area_id` NOT IN(
	SELECT `area_id` FROM `nx_dict_area_weather` GROUP BY `area_id`
)
GROUP BY `city_id`, `area_id`
'''
	try:
		Common.Dml(db.conn, insert_new_data)
	except Exception as e:
		print(e)
		pass

def Update_New_Data():
	db = Db_Conn.Mydb_Conn()
	ReqSQL = "select area_name from nx_dict_area_weather"
	ReqData = Common.Query(db.conn, ReqSQL)
	CityCount = len(ReqData)
	for city in range(0,CityCount):
		CityName = list(ReqData[city])[0]
		#print CityName
		Weather_Info = Get_Weather_Info.get_data(CityName)
		Weather = str(Weather_Info[0])
		Weather_Code = str(Weather_Info[1])
		Temp_High = str(Weather_Info[2])
		Temp_Low = str(Weather_Info[3])
		Temp_Current = str(Weather_Info[4])
		Pm25= str(Weather_Info[5])
		Mtime = str(Weather_Info[6])
		Update_Date = str(Weather_Info[7])
		Area_Name = str(CityName)
		Update_SQL = "update nx_dict_area_weather set weather='" + Weather + "',weather_code='" + Weather_Code + "',temp_high='" + Temp_High + "',temp_low='" + Temp_Low + "',temp_current='" + Temp_Current + "',pm25='" + Pm25 + "',mtime='" +  Mtime + "',update_date=DATE_FORMAT('" + Update_Date + "','%Y-%m-%d %H:%i') where area_name='" + Area_Name + "'"
		#Update_SQL = "update nx_dict_area_weather set weather=%s, weather_code=%s, temp_high=%s, temp_low=%s, temp_current=%s, pm25=%s, mtime=%s, update_date=DATE_SUB('%s',INTERVAL 0 day) area_name='" + Area_Name + "'" % Weather_Info
		#print Update_SQL
		try:
			Common.Dml(db.conn, Update_SQL)
		except Exception as e:
			print e
			pass
	db.conn.close()






if __name__=="__main__":
	Insert_New_Data()
	Update_New_Data()



