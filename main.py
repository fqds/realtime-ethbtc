import time
from bs4 import BeautifulSoup
from selenium import webdriver
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


ETH_URL = "https://ru.tradingview.com/symbols/ETHUSD/?exchange=CRYPTO"
BTC_URL = "https://ru.tradingview.com/symbols/BTCUSD/?exchange=CRYPTO"
DB_NAME = "ethbtc"
DB_USER = "tester"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
ALARM_DEVIATION = 0.005  # Процент отклонений роста eth от btc необходимый для вызова ahtung()
OFFSET_MINUTES = 60  # Период проверки отклонений


def parseCourse(driver):
    page_source = driver.page_source
    soupe = BeautifulSoup(page_source, "lxml")
    value = soupe.find("div", class_="lastContainer-JWoJqCpY")
    return float(value.text[:-4])


# Сохраняет в БД курсы eth и btc
def createStatNote(cursor, unix, eth_value, btc_value):
    cursor.execute("INSERT INTO stat (unix, eth_value, btc_value) VALUES (%s, %s, %s)",
                   (unix, eth_value, btc_value))


def getStatNoteByUnix(cursor, unix):
    cursor.execute("SELECT eth_value, btc_value FROM stat WHERE unix = %s",
                   (unix,))
    note = cursor.fetchall()
    return note


# Возвращает unix время, в которое произойдет следующее добавление результатов в БД
def getNextUnix():
    return int(time.time())//60*60+60


def ahtung():
    print("AHTUNG!!!!!!!!!!!!!!!")
    print("AHTUNG!!!!!!!!!!!!!!!")
    print("AHTUNG!!!!!!!!!!!!!!!")


def main():
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

    cursor = connection.cursor()
    next_unix = getNextUnix()

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver_eth = webdriver.Chrome(executable_path="driver_path", options=options)
    driver_eth.get(url=ETH_URL)
    driver_btc = webdriver.Chrome(executable_path="driver_path", options=options)
    driver_btc.get(url=BTC_URL)

    while True:
        try:
            current_time = int(time.time())
            if current_time >= next_unix:
                eth_value = parseCourse(driver_eth)
                btc_value = parseCourse(driver_btc)
                print("current time:", datetime.fromtimestamp(next_unix))
                print("eth:", eth_value, "\nbtc:", btc_value)

                createStatNote(cursor, next_unix, eth_value, btc_value)
                connection.commit()

                note = getStatNoteByUnix(cursor, next_unix-60*OFFSET_MINUTES)
                if note == []:
                    print(OFFSET_MINUTES, "minutes ago was no note")
                else:
                    deviation = abs(note[0]["eth_value"]/eth_value - note[0]["btc_value"]/btc_value)
                    print("deviation for", OFFSET_MINUTES, "minutes:", '{:0.9f}'.format(deviation))
                    if deviation >= ALARM_DEVIATION:
                        ahtung()

                next_unix = getNextUnix()

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
