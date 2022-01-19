import json
import pandas as pd
import numpy as np
from datetime import date
import requests
from secedgar import filings
from secedgar import *
import requests

# secedgar creates correct filing object for given arguments
# this will fetch the first 50 filings found over the time span
limit_to_form4 = lambda f: f.form_type.lower() == "4"
daily_filings_limited = secedgar.DailyFilings(start_date=date(2020, 1 ,3),
                                entry_filter=limit_to_form4,)
daily_filings_limited.save("C:/Users/Steven/Documents/Projects/sec4-filings-scanner/data")
