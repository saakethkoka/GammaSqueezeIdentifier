import mySQL_config
import mysql.connector


mydb = mysql.connector.connect(
  host=mySQL_config.host,
  user=mySQL_config.user,
  password=mySQL_config.password,
  database='open_interest_db'
)

cursor = mydb.cursor()
cursor.execute("insert into daily_option_data (DATE_VALUE, TICKER, SHARES_HEDGE_CALLS, SHARES_HEDGE_PUTS, CALL_OI, PUT_OI, CALL_TOTAL_VALUE, PUT_TOTAL_VALUE, NET_HEDGE, WEIGHTED_CALL_VOLUME, WEIGHTED_PUT_VOLUME, OPEN_PRICE, CLOSE_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME, VOLUME_3M, SHARES_OUT, SHARES_SHORT,HISTORICAL_VOLATILITY) values ('2021-5-25', 'AAPL', 1000,1212,212,121,21232,543,435,43543,43543,231234,23432,324231,2312,21312,34524,1231,342,.001)")

mydb.commit()