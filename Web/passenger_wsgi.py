import sys, os
INTERP = os.path.join(os.environ['HOME'], 'askmeair.com', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())



from flask import Flask, render_template, request, jsonify
application = Flask(__name__)

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import pytz, datetime, pymysql.cursors

@application.route('/')
def index():
    return 'INDEX1'

@application.route('/aquahack')
def aquahack():
    f = open("device1_recent.txt", "r")
    data_string = f.readline()
    f.close()

    Data_map = parseDeviceData(data_string)
    return render_template("aquahack_index.html", data_map = Data_map)

def parseDeviceData(s):
    data_list = s.split('|')
    date_string = parseSentDate(data_list[5])
    dataMap = {"humid" : data_list[0], "level" : data_list[1], "temp" : data_list[2], "longt" : data_list[3], "lat" : data_list[4], "date" : date_string}
    return dataMap

def parseSentDate(s):
    datetime_items = s.split(' ')
    date_items = datetime_items[0].split('-')
    time_items = datetime_items[1].split(':')

    date_string = date_items[2] + "/" + date_items[1] + "/" + date_items[0] + " " + time_items[0] + ":" + time_items[1] + ":" + time_items[2]
    return date_string

@application.route('/aquahack/getdata/CCj5TpgOUr/dn=<dn>ANDah=<ah>ANDwl=<wl>ANDt=<temp>', methods=['GET'])
def getData(dn, ah, wl, temp):
    data = {}
    data["humid"] = ah
    data["level"] = wl
    data["temperature"] = temp
    data["longt"] = "4.1"
    data["lat"] = "7.8"
    data["receiveDate"] = getBakuDateTime()

    # if validate_data(data) != True:
    #     return validate_data(data)

    f = open("device1_recent.txt", "w")
    f.write(ah +"|" + wl + "|" + temp + "|" + "3.1" + "|" + "3.1" + "|" + data["receiveDate"])
    f.close()

    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)

   
    addRecordDB(1, data)
    

    return 'DATA SENT SUCCESFULLY';

def addRecordDB(device_number, record):  
    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)
    sql = "INSERT INTO device1_records VALUES (%s, %s, %s, %s, %s, %s, NULL, '%s', NULL, NULL);"
    connection.cursor().execute(sql % ("0", record["humid"], record["level"], record["temperature"], record["longt"],  record["lat"], record["receiveDate"]))
    connection.commit()
    connection.close()


def getBakuDateTime():
    baku_time = pytz.timezone('Asia/Baku')
    dt = datetime.datetime.now(tz=baku_time)
    date_string = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day) + " " + str(dt.hour) + ":" + str(dt.minute) + ":" + str(dt.second)
    return date_string



# def validate_data(dataMap):
#     if float(dataMap["humid"]) < 0 or float(dataMap["humid"]) > 100:
#         return 'bad humidity value: ' + dataMap["humid"]

#     if float(dataMap["level"]) < 0:
#         return 'bad water level value'
    
#     if float(dataMap["longt"]) < -180 or float(dataMap["longt"]) > 180:
#         return 'bad longtitude value: ' + dataMap["longt"]

#     if float(dataMap["lat"]) < -90 or float(dataMap["lat"]) > 90:
#         return 'bad lattitude value: ' + dataMap["lat"]

#     return True

@application.route('/aquahack/api', methods=['GET', 'POST'])
def api1():
    #?device=1||2||3
    
    if request.args.get('device') == "1":
        f = open("device1_recent.txt", "r")
    elif request.args.get('device') == "2":
        f = open("device1_recent.txt", "r")
    elif request.args.get('device') == "3":
        f = open("device1_recent.txt", "r")
    else:
        return 'DEVICE DOES NOT EXIST'

    data_string = f.readline()
    f.close()

    data_dict = parseDeviceData(data_string)
    data_dict["status"] = "on"
    return jsonify(data_dict)

@application.route('/aquahack/device-count', methods=['GET'])
def getDeviceCount():
    return '3'

@application.route('/aquahack/statistics', methods=['GET'])
def systemStatistics():
    #?device=1&dp=air_humidity&dd=2020-7-4&wp=air_humidity&wd=2020-7-4&yp=air_humidity&yd=2020
    data = {"device" : request.args.get('device'),
    "daily_parameter" : request.args.get('dp'),
    "daily_date" : request.args.get('dd'),
    "weekly_parameter" : request.args.get('wp'),
    "weekly_date" : request.args.get('wd'), 
    "annual_parameter" : request.args.get('yp'),
    "annual_date" : request.args.get('yd')}

    daily_data_array = None #strings
    weekly_data_array = None
    annual_data_array = None

    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)
    daily_row = None

    with connection.cursor() as cur:
        cur.execute("SELECT * FROM device1_daily_records WHERE receive_date = '%s';" % data["daily_date"])
        record = cur.fetchall()
        daily_row = record[0]
    
    statistics = {}

    if data["daily_parameter"] == "water_level":
        daily_data_array = daily_row["water_level_array"]
        statistics["daily_max"] = str(daily_row["max_water_level"])
        statistics["daily_min"] = str(daily_row["min_water_level"])
        statistics["daily_average"] = str(daily_row["average_water_level"])
        statistics["daily_unit"] = " m"
    elif data["daily_parameter"] == "temperature":
        daily_data_array = daily_row["temperature_array"]
        statistics["daily_max"] = str(daily_row["max_temperature"])
        statistics["daily_min"] = str(daily_row["min_temperature"])
        statistics["daily_average"] = str(daily_row["average_temperature"])
        statistics["daily_unit"] = " C"
    else:
        daily_data_array = daily_row["air_humidity_array"]
        statistics["daily_max"] = str(daily_row["max_air_humidity"])
        statistics["daily_min"] = str(daily_row["min_air_humidity"])
        statistics["daily_average"] = str(daily_row["average_air_humidity"])
        statistics["daily_unit"] = "%"

    #weekly check
    # if data["weekly_parameter"] == "water_level":
    #     weekly_data_array = weekly_row["water_level_array"]
    #     statistics["weekly_max"] = weekly_row["max_water_level"]
    #     statistics["weekly_min"] = weekly_row["min_water_level"]
    #     statistics["weekly_average"] = weekly_row["average_water_level"]
    # elif data["daily_parameter"] == "temperature":
    #     weekly_data_array = weekly_row["temperature_array"]
    #     statistics["weekly_max"] = daweekly_rowly_row["max_temperature"]
    #     statistics["weekly_min"] = weekly_row["min_temperature"]
    #     statistics["weekly_average"] = daily_row["average_temperature"]
    # else:
    #     weekly_data_array = weekly_row["air_humidity_array"]
    #     statistics["weekly_max"] = weekly_row["max_air_humidity"]
    #     statistics["weekly_min"] = weekly_row["min_air_humidity"]
    #     statistics["weekly_average"] = weekly_row["average_air_humidity"]
    
    connection.close()
# site_weekly_array = strToArray(weekly_data_array), site_annual_array=strToArray(annual_data_array)
    return render_template("mad-kura-statistics.html", site_data=data, site_statistics=statistics, site_daily_array = strToArray(daily_data_array)
     )

    
def strToArray(s):
    array = list()

    s = s[1:len(s) - 1]
    str_list = s.split(',')

    for el in str_list:
        array.append(float(el))

    return array

    
    




