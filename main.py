import requests
import time
import traceback
from datetime import datetime, timedelta
import pandas as pd
result_dict={}
import AngelIntegration

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
def get_user_settings():
    delete_file_contents("OrderLog.txt")
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,Quantity,EMA1,EM2,PositionType
        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Symbol': row['Symbol'],"Quantity":row['Quantity'],'EMA1':row['EMA1'],'EM2':row['EM2']
                ,"PositionType": row['PositionType'],'pivot'  : None,'bc' : None,'tc' :None,'Segment':row['Segment'],
                'TimeFrame': row['TimeFrame'], 'CPR_Timeframe': row['CPR_Timeframe'],"Highesthigh":None,"Lowestow":None,
                'Trade':None,'entryPrice':None,'exitPrice':None,"Once":False,

            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


pnl_list=[]

get_user_settings()
def get_api_credentials():
    credentials = {}

    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials
def get_api_credentials():
    credentials = {}

    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


credentials_dict = get_api_credentials()
stockdevaccount=credentials_dict.get('stockdevaccount')
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)

def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token




def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def main_strategy():
    global result_dict,once,pivot,bc,tc,previousBar_close,currentBar_close,previousBar_low,previousBar_high,pnl_list
    print("main_strategy running ")
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                print(f"{timestamp} Total pnl all stoc : {sum(pnl_list)}")
                if params["Once"]==False:
                    params["Once"]=True
                    data= AngelIntegration.get_historical_data(symbol=params['Symbol'], token=get_token(params['Symbol']),
                                                              timeframe='ONE_DAY', segment=params['Segment'])
                    if params['CPR_Timeframe']=="ONE_DAY":
                        result = data.iloc[-2]
                        high_value = result['high']
                        low_value = result['low']
                        close_value = result['close']
                        params["Highesthigh"]= high_value
                        params["Lowestow"]= low_value
                        params['pivot']= (high_value + low_value + close_value) / 3
                        params['bc'] = (high_value + low_value) / 2
                        params['tc'] = (params['pivot'] - params['bc']) + params['pivot']

                        Orderlog = (f"{timestamp}  {params['Symbol']} @ CPR BC : { params['bc']}, CPR TC :{params['tc']},"
                                    f"High value: {params['Highesthigh']},Low value: {params['Lowestow']}")
                        print(Orderlog)
                        write_to_order_logs(Orderlog)



                    if params['CPR_Timeframe'] == "ONE_WEEK":
                        result = data.iloc[-8:-2]
                        highest_high = result['high'].max()
                        lowest_low = result['low'].min()
                        params["Highesthigh"] = highest_high
                        params["Lowestow"] = lowest_low
                        last_row_close = result.iloc[-1]['close']
                        params['pivot'] = (highest_high + lowest_low + last_row_close) / 3
                        params['bc'] = (highest_high + lowest_low) / 2
                        params['tc'] = (params['pivot'] - params['bc']) + params['pivot']
                        Orderlog = (f"{timestamp}  {params['Symbol']} @ CPR BC : {params['bc']}, CPR TC :{params['tc']},"
                                    f"High value: {params['Highesthigh']},Low value: {params['Lowestow']}")
                        print(Orderlog)
                        write_to_order_logs(Orderlog)
                    if params['CPR_Timeframe'] == "ONE_MONTH":
                        result = data.iloc[-31:-2]
                        highest_high = result['high'].max()
                        lowest_low = result['low'].min()
                        params["Highesthigh"] = highest_high
                        params["Lowestow"] = lowest_low
                        last_row_close = result.iloc[-1]['close']
                        params['pivot'] = (highest_high + lowest_low + last_row_close) / 3
                        params['bc'] = (highest_high + lowest_low) / 2
                        params['tc'] = (params['pivot'] - params['bc']) + params['pivot']
                        Orderlog = (f"{timestamp}  {params['Symbol']} @ CPR BC : {params['bc']}, CPR TC :{params['tc']},"
                                    f"High value: {params['Highesthigh']},Low value: {params['Lowestow']}")
                        print(Orderlog)
                        write_to_order_logs(Orderlog)

                presentDay = AngelIntegration.get_historical_data_ema(symbol=params['Symbol'],
                                                                     token=get_token(params['Symbol']),
                                                                     timeframe=params['TimeFrame'],
                                                                     ema1=params['EMA1'], ema2=params['EM2'],segment=params['Segment'])
                LTP=AngelIntegration.get_ltp(symbol=params['Symbol'],
                                                                     token=get_token(params['Symbol']),segment=params['Segment'])
                secondlastrow=presentDay.iloc[-2]
                thirdlastrow = presentDay.iloc[-3]
                secondlastopen=secondlastrow['open']
                secondlastclose=secondlastrow['close']
                ema1=secondlastrow['EMA1']
                ema2=secondlastrow['EMA2']

                ema1_2 = thirdlastrow['EMA1']
                ema2_2 = thirdlastrow['EMA2']

                if secondlastopen>ema1 and secondlastclose> ema1 and params["Highesthigh"]<params['tc'] and params['Trade']==None:
                    params['Trade'] ="BUY"
                    params['entryPrice'] = LTP


                    Orderlog=f"{timestamp} Buy @ {params['Symbol']} @ price: {LTP}"
                    print(Orderlog)
                    write_to_order_logs(Orderlog)

                if secondlastopen<ema1 and secondlastclose< ema1 and params["Highesthigh"]>params['bc'] and params['Trade']==None:
                    params['Trade'] ="SELL"
                    params['entryPrice'] = LTP
                    Orderlog=f"{timestamp} sell @ {params['Symbol']} @ price: {LTP}"
                    print(Orderlog)
                    write_to_order_logs(Orderlog)

                if params['Trade'] =="BUY":
                    if ema1_2>=ema2_2 and ema1<ema2:
                        params['Trade']="NoTrades"
                        params['exitPrice'] = LTP
                        currenttradepnl=params['exitPrice']-params['entryPrice']
                        pnl_list.append(currenttradepnl)
                        Orderlog = f"{timestamp} buy exit  @ {params['Symbol']} @ price: {LTP}, present trade profit= {currenttradepnl}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)

                if params['Trade'] == "SELL":
                    if ema1_2 >= ema2_2 and ema1 < ema2:
                        params['Trade']="NoTrades"
                        params['exitPrice'] = LTP
                        currenttradepnl =params['entryPrice'] -  params['exitPrice']
                        pnl_list.append(currenttradepnl)
                        Orderlog = f"{timestamp} sell exit  @ {params['Symbol']} @ price: {LTP}, present trade profit= {currenttradepnl}"
                        print(Orderlog)
                        write_to_order_logs(Orderlog)







    except Exception as e:
        print("Error in main strategy : ", str(e))
        traceback.print_exc()


while True:
    print("while loop running ")
    main_strategy()
    time.sleep(2)