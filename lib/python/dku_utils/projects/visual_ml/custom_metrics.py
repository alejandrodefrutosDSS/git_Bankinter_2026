# WAPE:
WAPE_DESCRIPTION = """The Weighted Absolute Percentage Error (WAPE) is a metric used to evaluate the accuracy of forecasts 
or predictions. It is particularly useful when you want to account for the importance or significance of different data points 
in your evaluation. WAPE calculates the percentage error for each data point, takes the absolute value of these errors, 
weights them based on some criterion, and then computes the average of these weighted absolute percentage errors."""

WAPE_CODE = '''
def score(y_valid, y_pred):
    diff = y_valid - y_pred
    wape = 100 * diff.abs().sum()/y_valid.sum()
    return wape
'''

WAPE_SETTINGS = {
    "name" : "Weighted Absolute Percentage Error (WAPE)",
    "code": WAPE_CODE,
    "description": WAPE_DESCRIPTION,
    "greater_is_better": False,
    "use_probas": False 
 }

# All metrics settings:
ALL_METRICS_SETTINGS = {
    "WAPE": WAPE_SETTINGS
}