import database_manager as dm
import datetime as dt
import time


print(dt.datetime.now())
time.sleep(1000)
base_query = "SELECT TICKER FROM daily_option_data WHERE DATE_VALUE="
date = str(dt.date.today())
dm.cursor.execute(base_query + "'" + date + "'")
ticker_list = dm.cursor.fetchall()


base_query = "SELECT NET_HEDGE, OPEN_PRICE, CLOSE_PRICE FROM daily_option_data WHERE TICKER="

for ticker in ticker_list:
    dm.cursor.execute(base_query + "'" + ''.join(ticker) + "'")
    list = dm.cursor.fetchall()
    print(ticker[0], float(list[3][0]) - float(list[2][0]), float(list[0][2]), float(list[1][2]))




