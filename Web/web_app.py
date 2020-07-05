import sys, os
INTERP = os.path.join(os.environ['HOME'], 'askmeair.com', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())



from flask import Flask, render_template
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
    date_string = parseSentDate(data_list[4])
    dataMap = {"humid" : data_list[0], "level" : data_list[1], "longt" : data_list[2], "lat" : data_list[3], "date" : date_string}
    return dataMap

def parseSentDate(s):
    date_items = s.split('-')
    date_string = date_items[1] + "/" + date_items[0] + "/" + date_items[2] + " " + date_items[3] + ":" + date_items[4] + ":" + date_items[5]
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
    f.write(ah +"|" + wl + "|" + temp + "|" + "3.1" + "|" + "3.1" + "|" + data["receiveDate"] + ";" )
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
