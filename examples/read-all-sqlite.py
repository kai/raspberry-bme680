#!/usr/bin/env python

import bme680
import time
import sqlite3

def main():

    sensor = bme680.BME680()

    database = "C:\\sqlite\db\sensordata.db"

    # create a database connection
    conn = create_connection(database)

    # These calibration data can safely be commented
    # out, if desired.

    print("Calibration data:")
    for name in dir(sensor.calibration_data):

        if not name.startswith('_'):
            value = getattr(sensor.calibration_data, name)

            if isinstance(value, int):
                print("{}: {}".format(name, value))

    # These oversampling settings can be tweaked to
    # change the balance between accuracy and noise in
    # the data.

    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

    # print("\n\nInitial reading:")
    # for name in dir(sensor.data):
    #    value = getattr(sensor.data, name)

    #    if not name.startswith('_'):
    #        print("{}: {}".format(name, value))

    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)

    # Up to 10 heater profiles can be configured, each
    # with their own temperature and duration.
    # sensor.set_gas_heater_profile(200, 150, nb_profile=1)
    # sensor.select_gas_heater_profile(1)

    try:
        while True:
            if sensor.get_sensor_data():
                reading = "{0:.2f},{1:.2f},{2:.2f}".format(sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)

                if sensor.data.heat_stable:
                    reading = "{0},{1} Ohms".format(reading, sensor.data.gas_resistance)

                # else:
                #    print(output)

                with conn:
                    task_id = create_entry(conn, reading)
                    print(task_id)

            time.sleep(30)

    except KeyboardInterrupt:
        pass

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    dbfile = sensordata.db
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def create_entry(conn, entry):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO bme680readings(temp,pressure,humidity,resistance)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, entry)
    return cur.lastrowid

if __name__ == '__main__':
    main()
