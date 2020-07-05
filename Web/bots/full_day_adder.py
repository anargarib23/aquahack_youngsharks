import sys, pymysql.cursors, pytz, datetime, random, time

start_time = time.time()

def addFullDay(date, hour_offset, hour_limit):
    connection = pymysql.connect(host="db.askmeair.com", user="db_askmeair", password="sextinaaquafina", db="askmeair_records", cursorclass=pymysql.cursors.DictCursor)

    for hour in range(hour_offset, hour_limit):
        water_level = round(random.uniform(20, 25), 2)
        air_humidity = round(random.uniform(10, 90), 1)
        temperature = round(random.uniform(20, 40), 1)

        receive_date = "%s-%s-%s %s:00:00" % (date["year"], date["month"], date["day"], str(hour))
        sql = "INSERT INTO device1_records VALUES (%s, %s, %s, %s, %s, %s, NULL, '%s', NULL, NULL);"

        # print(sql % ("0", str(air_humidity), str(water_level), str(temperature), "45.5",  "45.5", receive_date))
        # print("\n")

        connection.cursor().execute(sql % ("0", str(air_humidity), str(water_level), str(temperature), "45.5",  "45.5", receive_date))
        connection.commit()

    connection.close()

date_data = {"year" : sys.argv[1], "month": sys.argv[2], "day" : sys.argv[3]}
hour_offset = int(sys.argv[4])
hour_limit = int(sys.argv[5])


addFullDay(date_data, hour_offset, hour_limit)

print("Process Ended. Time Passed: %f" % (time.time() - start_time))