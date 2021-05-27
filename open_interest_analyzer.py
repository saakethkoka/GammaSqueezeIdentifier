import database_manager as dm
import datetime as dt

dm.update_database_daily()
base_query = "SELECT TICKER FROM daily_option_data WHERE DATE_VALUE="
date = '2021-05-25'
dm.cursor.execute(base_query + date)
list = dm.cursor.fetchall()

print(list)

