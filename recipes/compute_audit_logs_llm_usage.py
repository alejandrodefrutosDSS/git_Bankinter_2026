# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu


mapping_eventServer = {
    "message.msgType": "msgType",
    "message.computeResourceUsage.startTime": "startTime",
    "message.computeResourceUsage.type": "type",
    "message.computeResourceUsage.llmUsage.totalComputationTimeMS": "llmUsage_totalComputationTimeMS",
    "message.computeResourceUsage.llmUsage.llmType": "llmUsage_llmType",
    "message.computeResourceUsage.llmUsage.totalQueries": "llmUsage_totalQueries",
    "message.computeResourceUsage.llmUsage.totalPromptTokens": "llmUsage_totalPromptTokens",
    "message.computeResourceUsage.llmUsage.estimatedCostUSD": "llmUsage_estimatedCostUSD",
    "message.computeResourceUsage.llmUsage.totalCompletionTokens": "llmUsage_totalCompletionTokens",
    "message.computeResourceUsage.llmUsage.connection": "llmUsage_connection",
    "message.computeResourceUsage.llmUsage.cacheMissQueries": "llmUsage_cacheMissQueries",
    "message.computeResourceUsage.llmUsage.llmId": "llmUsage_llmId",
    "message.computeResourceUsage.llmUsage.usageType": "llmUsage_usageType",
    "message.computeResourceUsage.llmUsage.cacheHitQueries": "llmUsage_cacheHitQueries",
    "message.computeResourceUsage.context.authIdentifier": "context_authIdentifier",
    "message.computeResourceUsage.context.projectKey": "context_projectKey",
    "message.computeResourceUsage.context.type": "context_type",
    "message.computeResourceUsage.context.jobId": "context_jobId",
    "timestamp": "timestamp",
    "message.dssNodeId": "dssNodeId",
    "message.dssNodeName": "dssNodeName",
    "message.auditTopic": "auditTopic",
    "message.authSource": "authSource",
    "message.authUser": "authUser",
    "message.clientIP": "clientIP"
}


audit_logs = dataiku.Dataset("audit_logs")
audit_logs_llm_usage = dataiku.Dataset("audit_logs_llm_usage")
with audit_logs_llm_usage.get_writer() as writer:
    for batch in audit_logs.iter_dataframes(infer_with_pandas=True, parse_dates=False):
        batch = batch[batch['message.computeResourceUsage.type'] == "LLM_USAGE"]
        batch.rename(columns=mapping_eventServer, inplace=True)
        writer.write_dataframe(batch)
