import py_vollib.black_scholes.greeks.analytical
from tda import auth, client
import json
import config
import time
import csv
import historicalVolatilityCalculator

total_options_missed = 0
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path= '/Users/saakethkoka/Documents/Stonks/Code/GammaSqueezeIdentifier/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)


print(json.dumps(c.get_quote('AAPL').json(), indent=4))
print(py_vollib.black_scholes.greeks.analytical.delta('p', 6.92, 15.00, 207/365, 0, 0.7007434498330484))




def get_option_data(ticker, print_data = False):
    option = c.get_option_chain(ticker,
                                contract_type=  client.Client.Options.ContractType.ALL
                                )
    assert option.status_code == 200, option.raise_for_status()

    #print(json.dumps(option.json(), indent=4))
    parser = option.json()
    call_hedge_pos = 0
    put_hedge_pos = 0
    num_calls = 0
    num_puts = 0
    call_OI = 0
    put_OI = 0

    missed_puts = 0
    missed_calls = 0
    historical_volatility = historicalVolatilityCalculator.get_historical_volitility(ticker)
    for key in parser['putExpDateMap']:
        value = parser['putExpDateMap'][key]
        for item in value:
            if (parser['putExpDateMap'][key][item][0]["delta"] == "NaN" or parser['putExpDateMap'][key][item][0]["delta"] < -1):
                #print('delta not found', parser['putExpDateMap'][key][ticker][0]["openInterest"], parser['putExpDateMap'][key][ticker][0]["description"])
                missed_puts += parser['putExpDateMap'][key][item][0]["openInterest"]
                continue

            #print(value[ticker])
            put_hedge_pos += parser['putExpDateMap'][key][item][0]["delta"] * parser['putExpDateMap'][key][item][0]["openInterest"]*100
            put_OI += parser['putExpDateMap'][key][item][0]["openInterest"]
            num_puts += 1
    for key in parser['callExpDateMap']:
        value = parser['callExpDateMap'][key]
        for item in value:
            if(parser['callExpDateMap'][key][item][0]["delta"] == "NaN" or parser['putExpDateMap'][key][item][0]["delta"] < -1):
                #print('delta not found', parser['callExpDateMap'][key][ticker][0]["openInterest"], parser['callExpDateMap'][key][ticker][0]["description"])
                missed_calls += parser['callExpDateMap'][key][item][0]["openInterest"]
                continue
            call_hedge_pos += parser['callExpDateMap'][key][item][0]["delta"] * parser['callExpDateMap'][key][item][0]["openInterest"]*100
            call_OI += parser['callExpDateMap'][key][item][0]["openInterest"]
            num_calls += 1
    if print_data:
        print('Missed Options:', missed_options)
        print("Shares needed to hedge calls:", call_hedge_pos, "Shares needed to hedge puts:", put_hedge_pos)
        print("Number of calls", num_calls,"Number of puts:", num_puts)
        print("Total Needed to hedge:", call_hedge_pos + put_hedge_pos)
        print("Call OI:", call_OI, "Put OI:", put_OI)
        print("Shares out:", c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"])
        print("Num shares needed to hedge/ Shares out:", (call_hedge_pos + put_hedge_pos)*100 / c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"])

    print(missed_calls, missed_puts)
    return call_hedge_pos + put_hedge_pos


def print_snp():
    start_time = time.time()
    filecontent = ''
    with open('s&p500tickerts.txt') as f:
        filecontent = f.readlines()

    with open('May242021.csv', mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        filecontent = [x.strip() for x in filecontent]
        max_val = 0
        max_tick = 'aaa'
        for ticker in filecontent:
            try:
                sharesOutstanding = c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"]
            except:
                continue
            time.sleep(.50)
            if(sharesOutstanding < 10000000):
                continue
            try:
                val = (get_option_data(ticker) / sharesOutstanding) * 100
            except:
                continue
            if(abs(val) > abs(max_val)):
                max_val = val
                max_tick = ticker
                
            writer.writerow([ticker, val])
            print(ticker, val, "        ",max_tick, max_val, time.time()-start_time)
            time.sleep(.50)

# ticker = 'IPOE'
# print(get_option_data(ticker)*100 / c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"])