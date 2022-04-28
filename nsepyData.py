from nsepy import get_history
from datetime import datetime, date, timedelta
import os

def get_index_data(symbol="NIFTY 50"):
    today = datetime.now()
    date2022 = datetime(2022, 1, 1)
    data = get_history(symbol=symbol,
                                start=date2022,
                                end=today,
                                index=True)
    
    filename = 'data/{}.csv'.format(symbol.lower().replace(" ", ""))
    if os.path.isfile(filename) == False:
        data.to_csv(filename)
    else:
        pass