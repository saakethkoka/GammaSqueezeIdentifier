import py_vollib.black_scholes.greeks.analytical
from tda import auth, client
import TDA_config
import historicalVolatilityCalculator

total_options_missed = 0
try:
    c = auth.client_from_token_file(TDA_config.token_path, TDA_config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path= '/Users/saakethkoka/Documents/Stonks/Code/GammaSqueezeIdentifier/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, TDA_config.api_key, TDA_config.redirect_uri, TDA_config.token_path)






def get_option_data(ticker, print_data = False, stock_price=-1,):
    option = c.get_option_chain(ticker,
                                contract_type=  client.Client.Options.ContractType.ALL
                                )
    assert option.status_code == 200, option.raise_for_status()
    if stock_price == -1:
        stock_price = c.get_quote(ticker).json()[ticker]["closePrice"]
    #print(json.dumps(option.json(), indent=4))
    parser = option.json()

    # Data to collect:
    call_hedge_pos = 0
    put_hedge_pos = 0
    call_OI = 0
    put_OI = 0
    call_total_value = 0
    put_total_value = 0
    weighted_call_volume = 0
    weighted_put_volume = 0

    historical_volatility = historicalVolatilityCalculator.get_historical_volitility(ticker)
    for key in parser['putExpDateMap']:
        value = parser['putExpDateMap'][key]
        for item in value:
            days_till_expiry = value[item][0]["daysToExpiration"]
            strike_price = value[item][0]["strikePrice"]
            delta = py_vollib.black_scholes.greeks.analytical.delta('p', stock_price, strike_price, days_till_expiry/365, 0, historical_volatility)

            put_hedge_pos += delta * value[item][0]["openInterest"]*100
            put_OI += value[item][0]["openInterest"]
            put_total_value += value[item][0]["openInterest"] * value[item][0]["mark"]
            weighted_put_volume += value[item][0]["totalVolume"] * delta

    for key in parser['callExpDateMap']:
        value = parser['callExpDateMap'][key]
        for item in value:
            days_till_expiry = value[item][0]["daysToExpiration"]
            strike_price = value[item][0]["strikePrice"]
            delta = py_vollib.black_scholes.greeks.analytical.delta('c', stock_price, strike_price, days_till_expiry/365, 0, historical_volatility)

            call_hedge_pos += delta * value[item][0]["openInterest"]*100
            call_OI += value[item][0]["openInterest"]
            call_total_value += value[item][0]["openInterest"]*value[item][0]["mark"]
            weighted_call_volume += value[item][0]["totalVolume"] * delta

    if print_data:
        print("Shares needed to hedge calls:", call_hedge_pos, "Shares needed to hedge puts:", put_hedge_pos)
        print("Total Needed to hedge:", call_hedge_pos + put_hedge_pos)
        print("Call OI:", call_OI, "Put OI:", put_OI)
        print("Shares out:", c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"])
        print("Num shares needed to hedge/ Shares out:", (call_hedge_pos + put_hedge_pos)*100 / c.search_instruments(ticker, client.Client.Instrument.Projection.FUNDAMENTAL).json()[ticker]["fundamental"]["sharesOutstanding"])

    return_list = []
    return_list.append(call_hedge_pos)
    return_list.append(put_hedge_pos)
    return_list.append(call_OI)
    return_list.append(put_OI)
    return_list.append(call_total_value)
    return_list.append(put_total_value)
    return_list.append(call_hedge_pos + put_hedge_pos) # Returning net hedge as # of shares, not % of Shares out.
    return_list.append(weighted_call_volume)
    return_list.append(weighted_put_volume)
    return_list.append(historical_volatility)

    return return_list



def get_ticker_data(ticker_list):
    ticker_data_daily = {}
    temp_list = []
    for i in range(len(ticker_list)):
        temp_list.append(ticker_list[i])
        if len(temp_list) > 450 or i == len(ticker_list) - 1:
            ticker_data_daily = {**ticker_data_daily, **(c.get_quotes(temp_list).json())}
            temp_list.clear()
    return ticker_data_daily


def get_fundamental_data(ticker_list):
    fundamental_data_list = {}
    temp_list = []
    for i in range(len(ticker_list)):
        temp_list.append(ticker_list[i])
        if len(temp_list) > 450 or i == len(ticker_list) - 1:
            fundamental_data_list = {**fundamental_data_list, **(c.search_instruments(temp_list, client.Client.Instrument.Projection.FUNDAMENTAL).json())}
            temp_list.clear()
    return fundamental_data_list
