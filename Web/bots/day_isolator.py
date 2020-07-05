import sys, pymysql.cursors, datetime, pytz, time
from datetime import date

start_time = time.time()
def findMaxStrArray(array):
    mx = float(array[0])

    for el in array:
        if float(el) > mx:
            mx = float(el)
    
    return mx

def findMinStrArray(array):
    mn = float(array[0])

    for el in array:
        if float(el) < mn:
            mn = float(el)
    
    return mn

def findAveStrArray(array):
    sm = 0
    size = len(array)

    for el in array:
        sm = sm + float(el)
    
    return float(sm) / size
    

def isolateDay(date_data):
    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cur:
        cur.execute("SELECT * FROM device1_records WHERE receive_date BETWEEN '%s-%s-%s 00:00:00' AND '%s-%s-%s 23:00:00' " % 
        (date_data["year"],  date_data["month"], date_data["day"], date_data["year"],  date_data["month"], date_data["day"]))

        isolated_day = cur.fetchall()

    connection.close()

    return isolated_day

def addDay(date_data):
    isolated_day = isolateDay(date_data)
    record_length = len(isolated_day)

    air_humidity_array = list()
    water_level_array = list()
    temperature_array = list()

    for record in isolated_day:
        air_humidity_array.append(record["air_humidity"])
        water_level_array.append(record["water_level"])
        temperature_array.append(record["temperature"])

    maxes = {"max_air_humidity" : findMaxStrArray(air_humidity_array),
    "max_water_level" : findMaxStrArray(water_level_array),
    "max_temperature" : findMaxStrArray(temperature_array)}

    mins = {"min_air_humidity" : findMinStrArray(air_humidity_array),
    "min_water_level" : findMinStrArray(water_level_array),
    "min_temperature" : findMinStrArray(temperature_array)}

    averages = {"average_air_humidity" : findAveStrArray(air_humidity_array),
    "average_water_level" : findAveStrArray(water_level_array),
    "average_temperature" : findAveStrArray(temperature_array)}

    week_day_value = date(int(date_data["year"]), int(date_data["month"]), int(date_data["day"])).weekday()

    week_day = {0 : "Mon", 1: "Tue", 2 : "Wed", 3 : "Thr", 4: "Fri", 5: "Sat", 6: "Sun"}

    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)
    sql = "INSERT INTO device1_daily_records VALUES(0, '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s')" % (
    str(water_level_array), str(air_humidity_array), str(temperature_array), str(maxes["max_water_level"]), str(mins["min_water_level"]), str(round(averages["average_water_level"], 2)),
    str(maxes["max_air_humidity"]), str(mins["min_air_humidity"]), str(round(averages["average_air_humidity"], 2)),
    str(maxes["max_temperature"]), str(mins["min_temperature"]), str(round(averages["average_temperature"], 2)), week_day[week_day_value], date_data["year"] + "-" + date_data["month"] + "-" +
    date_data["day"] + ";")

    connection.cursor().execute(sql)
    connection.commit()
    connection.close()

date_data = {"year" : sys.argv[1], "month" : sys.argv[2], "day" : sys.argv[3]}

addDay(date_data)

print("Process ended. Time passed: " + str(time.time() - start_time))