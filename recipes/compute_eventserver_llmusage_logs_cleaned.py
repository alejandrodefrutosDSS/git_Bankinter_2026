# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu


mapping_eventServer = {
    "clientEvent.msgType": "msgType",
    "clientEvent.computeResourceUsage.startTime": "startTime",
    "clientEvent.computeResourceUsage.type": "type",
    "clientEvent.computeResourceUsage.llmUsage.totalComputationTimeMS": "llmUsage_totalComputationTimeMS",
    "clientEvent.computeResourceUsage.llmUsage.llmType": "llmUsage_llmType",
    "clientEvent.computeResourceUsage.llmUsage.totalQueries": "llmUsage_totalQueries",
    "clientEvent.computeResourceUsage.llmUsage.totalPromptTokens": "llmUsage_totalPromptTokens",
    "clientEvent.computeResourceUsage.llmUsage.estimatedCostUSD": "llmUsage_estimatedCostUSD",
    "clientEvent.computeResourceUsage.llmUsage.totalCompletionTokens": "llmUsage_totalCompletionTokens",
    "clientEvent.computeResourceUsage.llmUsage.connection": "llmUsage_connection",
    "clientEvent.computeResourceUsage.llmUsage.cacheMissQueries": "llmUsage_cacheMissQueries",
    "clientEvent.computeResourceUsage.llmUsage.llmId": "llmUsage_llmId",
    "clientEvent.computeResourceUsage.llmUsage.usageType": "llmUsage_usageType",
    "clientEvent.computeResourceUsage.llmUsage.cacheHitQueries": "llmUsage_cacheHitQueries",
    "clientEvent.computeResourceUsage.context.authIdentifier": "context_authIdentifier",
    "clientEvent.computeResourceUsage.context.projectKey": "context_projectKey",
    "clientEvent.computeResourceUsage.context.type": "context_type",
    "clientEvent.computeResourceUsage.context.jobId": "context_jobId",
    "serverTimestamp": "timestamp",
    "clientEvent.dssNodeId": "dssNodeId",
    "clientEvent.dssNodeName": "dssNodeName",
    "clientEvent.auditTopic": "auditTopic",
    "clientEvent.authSource": "authSource",
    "clientEvent.authUser": "authUser",
    "clientEvent.clientIP": "clientIP"
}


# Read recipe inputs
eventserver_llmusage = dataiku.Dataset("eventserver_llmusage")
eventserver_llmusage_df = eventserver_llmusage.get_dataframe(infer_with_pandas=False)
columns = eventserver_llmusage_df.columns

eventserver_llmusage_df.rename(columns=mapping_eventServer, inplace=True)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
logs_clean_df = eventserver_llmusage_df # For this sample code, simply copy input to output

# Write recipe outputs
eventserver_llmusage_logs_cleaned = dataiku.Dataset("eventserver_llmusage_logs_cleaned")
eventserver_llmusage_logs_cleaned.write_with_schema(logs_clean_df)

