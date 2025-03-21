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
    "clientEvent.clientIP": "clientIP",
    "clientEvent.computeResourceUsage.totalTime": "totalTime"
}

eventserver_cru_logs = dataiku.Dataset("eventserver_cru_logs")
eventserver_llmusage_logs_cleaned = dataiku.Dataset("eventserver_llmusage_logs_cleaned")
with eventserver_llmusage_logs_cleaned.get_writer() as writer:
    for batch in eventserver_cru_logs.iter_dataframes(infer_with_pandas=True, parse_dates=False):
        print("Sample of 'clientEvent.computeResourceUsage.totalTime' before filtering:")
        print(batch['clientEvent.computeResourceUsage.totalTime'].head(30))
        print("Non-null count:", batch['clientEvent.computeResourceUsage.totalTime'].notnull().sum())
        batch = batch[batch['clientEvent.computeResourceUsage.type'] == "LLM_USAGE"]
        batch.rename(columns=mapping_eventServer, inplace=True)
        writer.write_dataframe(batch)