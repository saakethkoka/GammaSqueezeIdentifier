import mySQL_config
import mysql.connector
import TDA_stock_data_analyzer
import datetime as dt
import time
import twilio_config

mydb = mysql.connector.connect(
    host=mySQL_config.host,
    user=mySQL_config.user,
    password=mySQL_config.password,
    database='open_interest_db'
)
cursor = mydb.cursor()


def delete_date(date):
    base_of_query = "DELETE FROM daily_option_data WHERE DATE_VALUE = "
    cursor.execute(base_of_query + "'" + date + "'")
    mydb.commit()

def send_message(message_text):
    message = twilio_config.client.messages.create(
        body= message_text,
        from_='+14432340921',
        to='+14697718557'
    )
    print(message.sid)


def update_database_daily():
    send_message('Starting option scraping.')
    start_time = time.time()
    delete_date(str(dt.date.today()))
    base_of_query = "INSERT INTO daily_option_data (DATE_VALUE, TICKER, SHARES_HEDGE_CALLS, SHARES_HEDGE_PUTS, CALL_OI, PUT_OI, CALL_TOTAL_VALUE, PUT_TOTAL_VALUE, NET_HEDGE," \
                    " WEIGHTED_CALL_VOLUME, WEIGHTED_PUT_VOLUME, OPEN_PRICE, CLOSE_PRICE, HIGH_PRICE, LOW_PRICE, VOLUME, SHARES_OUT, HISTORICAL_VOLATILITY) "
    filecontent = ''
    with open('tickers.txt') as f:
        filecontent = f.readlines()

    ticker_list = [x.strip() for x in filecontent]
    daily_ticker_data = TDA_stock_data_analyzer.get_ticker_data(ticker_list)
    fundamental_data = TDA_stock_data_analyzer.get_fundamental_data(ticker_list)
    for i in range(100):
        if(len(daily_ticker_data) == len(ticker_list)):
            continue
        if(i == 99):
            raise Exception
        daily_ticker_data = TDA_stock_data_analyzer.get_ticker_data(ticker_list)
        time.sleep(.6)
    counter = 0
    for ticker in ticker_list:
        counter += 1
        print(counter)
        try:
            option_data = TDA_stock_data_analyzer.get_option_data(ticker, False, daily_ticker_data[ticker]["mark"])
        except:
            continue


        table_input = "VALUES ('" + str(dt.date.today()) + "', '" + ticker + "', " + str(option_data[0]) + ", " + str(option_data[1])\
                      + ", " + str(option_data[2]) + ", " + str(option_data[3]) + ", " + str(option_data[4]) + ", " + str(option_data[5])\
                      + ", " + str(option_data[6]*100 / fundamental_data[ticker]["fundamental"]["sharesOutstanding"]) + ", " + str(option_data[7]) + ", " \
                      + str(option_data[8]) + ", " + str(daily_ticker_data[ticker]["openPrice"]) + ", " + str(daily_ticker_data[ticker]["closePrice"])\
                      + ", " + str(daily_ticker_data[ticker]["highPrice"]) + ", " + str(daily_ticker_data[ticker]["lowPrice"]) + ", " \
                      + str(daily_ticker_data[ticker]["totalVolume"]) + ", " + str(fundamental_data[ticker]["fundamental"]["sharesOutstanding"]) + ", " \
                      + str(option_data[9]) + ")"
        print(table_input)
        cursor.execute(base_of_query + table_input)
        mydb.commit()
        time.sleep(.55)
    message = 'Done running. Time took: ' + str((time.time() - start_time)/60) + "minutes"
