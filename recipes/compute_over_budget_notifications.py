# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu

# Read recipe inputs
budget_joined_prepared = dataiku.Dataset("budget_joined_prepared")
budget_joined_prepared_df = budget_joined_prepared.get_dataframe()


# Compute recipe outputs from inputs
# TODO: Replace this part by your actual code that computes the output, as a Pandas dataframe
# NB: DSS also supports other kinds of APIs for reading and writing data. Please see doc.

over_budget_notifications_df = budget_joined_prepared_df # For this sample code, simply copy input to output


# Write recipe outputs
over_budget_notifications = dataiku.Dataset("over_budget_notifications")
over_budget_notifications.write_with_schema(over_budget_notifications_df)
