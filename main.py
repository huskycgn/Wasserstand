import RPi.GPIO as GPIO
import time
from cred import *
from datetime import datetime
import mariadb

# Weißes Kabel Trigger - Port 4
# Oranges Kabel Echo - Port 11
# Rotes Kabel VCC
# Schwarzes Kabel Erdung

def getutc():
    return datetime.utcnow()


def write_percentage(table) -> None:
    """Executes SQL statements
    :param table, con:
    :return:
    """
    connection = mariadb.connect(
        host=db_host, user=db_user, password=db_pass, database=db_name
    )
    statement = f"INSERT INTO {table} (time, tank) VALUES('{getutc()}', {calculatewaterlevel()});"

    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    return None


def get_distance():
    GPIO.setmode(GPIO.BOARD)
    PIN_TRIGGER = 7
    PIN_ECHO = 11

    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    print("Waiting for sensor to settle")

    time.sleep(2)

    print("Calculating distance")

    GPIO.output(PIN_TRIGGER, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time

    distancecm = round(pulse_duration * 17150, 2)

    print(distancecm)

    GPIO.cleanup()

    return distancecm

def calculatewaterlevel():
    full = 60
    #Höhe des Tanks
    distance = get_distance()

    while distance > full:
        print("Wert unplausibel")
        distance = get_distance()

    percentage = round(((distance * 100 / full) - 100) * -1, 2)

    return percentage


write_percentage("tank")