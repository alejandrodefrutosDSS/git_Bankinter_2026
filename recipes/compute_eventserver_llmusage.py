# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu

# Read recipe inputs
eventserver_cru_logs = dataiku.Dataset("eventserver_cru_logs")
eventserver_llmusage = dataiku.Dataset("eventserver_llmusage")

with eventserver_llmusage.get_writer() as writer:    
    for batch in eventserver_cru_logs.iter_dataframes():
        batch = batch[batch['clientEvent.computeResourceUsage.type'] == "LLM_USAGE"]
        writer.write_dataframe(batch)


