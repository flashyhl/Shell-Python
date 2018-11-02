#/usr/bin/python
#-*- coding: UTF-8 -*-
import sys
import urllib2
import json
import Common

reload(sys)
sys.setdefaultencoding('utf8')

def get_data(cityid):
	city = cityid
	keyid = 'xxxxxxxx22aa547f0bfc9xxxxxxxxxx'
	url = 'https://free-api.heweather.com/v5/weather?city=%s&key=%s' % (city, keyid)
	DayTime1 = str(Common.DateFormat()) + " 06:00:00"
	DayTime2 = str(Common.DateFormat()) + " 18:00:00"
	NowTime = str(Common.TimeFormat())
	NowTimeStamp = Common.TimeStamp()
	try:
		req = urllib2.Request(url)
		request_data = urllib2.urlopen(req).read()
		json_data = json.loads(request_data)
	except Exception, e:
		return False

	data = json_data['HeWeather5'][0]
	try:
		# 获取PM2.5的值
		EnvPm25 = data['aqi']['city']['pm25']
		# 获取空气质量
		AirQuality = data['aqi']['city']['qlty']
	except Exception, e:
		EnvPm25 = 80

	try:
		# 获取更新时间
		UpdateDate = data['basic']['update']['loc']
		# 获取城市
		CityName = data['basic']['city']
		# 获取天气代码
		WeatherCode = data['basic']['id']
	except Exception, e:
		return False


	# 获取今天的温度信息：天气状况，当前、最高、最低温度
	NowWeather = data['now']['cond']['txt']
	NowTemp = data['now']['tmp']
	today = data['daily_forecast'][0]
	HighTemp = today['tmp']['max']
	LowTemp = today['tmp']['min']

	if NowTime >= DayTime1 and NowTime <= DayTime2:
		WeatherCode = NowWeather + "_白天"
	else:
		WeatherCode = NowWeather + "_夜晚"

	result = (NowWeather, WeatherCode, HighTemp, LowTemp, NowTemp, EnvPm25, NowTimeStamp, UpdateDate, cityid)

	#result = (WeatherCode, UpdateDate, NowWeather, EnvPm25, HighTemp, LowTemp, NowTemp)
	return result

#if __name__ == '__main__':
#	areaid = '上海'
#	if get_data(areaid):
#		NowData = get_data(areaid)
#		print "%s\n天气代码：%s\n更新时间：%s\n今天的天气情况：%s\n空气PM2.5浓度:%s \n最高温度：%s \n最低温度：%s \n当前温度：%s " % NowData
#	else:
#		print "连接目标服务器出错或者你所查询的地区不存在！"