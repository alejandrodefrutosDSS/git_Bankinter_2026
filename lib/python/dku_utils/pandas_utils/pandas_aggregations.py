import pandas as pd
import numpy as np
from .pandas_utils_commons import clean_dataframe_column_names_for_storage


def pivot_pandas_column(dataframe: pd.core.frame.DataFrame,
                        column_to_pivot: str,
                        rows_for_aggregation_key: list,
                        aggregated_columns: list,
                        aggregation_function: str="max",
                        missing_values_filling: any=None):
    """
    Pivots a dataframe column, with chosen group keys (<-> resulting 'rows') and aggregating functions.

    :param dataframe: pd.core.frame.DataFrame: A pandas dataframe.
    :param column_to_pivot: str: The dataframe column to pivot.
    :param rows_for_aggregation_key: list: The dataframe rows to use as an aggregation key.
    :param aggregated_columns: list: The dataframe columns to aggregate.
    :param aggregation_function: str: The aggregation function to use on the 'aggregated_columns'.
    :param missing_values_filling: The value to use to fill the missing values in the pivoted columns.

    :returns: python_script_libraries_import_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in the python script.
    """
    ALLOWED_AGGREGATIONS = ["min", "max", "sum", "mean", "median",
                            "list", "set", "tuple"]
    
    if aggregation_function not in ALLOWED_AGGREGATIONS:
        log_message = f"""You can't use the aggregation '{aggregation_function}' in this function. """\
        f"""Please choose a value of 'aggregation_function' that is in '{ALLOWED_AGGREGATIONS}'."""
        raise ValueError(log_message)
    
    if aggregation_function == "median":
        aggregation_function = np.median
    elif aggregation_function == "list":
        aggregation_function = list
    elif aggregation_function == "set":
        aggregation_function = set
    elif aggregation_function == "tuple":
        aggregation_function = tuple

    dataframe = dataframe.pivot_table(
        columns=[column_to_pivot],
        index=rows_for_aggregation_key,
        values=aggregated_columns,
        fill_value=missing_values_filling,
        aggfunc=aggregation_function
    )
    dataframe.columns = ['_'.join(col) for col in dataframe.columns]
    dataframe = clean_dataframe_column_names_for_storage(dataframe)
    dataframe.reset_index(inplace=True)
    return dataframe


def compute_rownumber(dataframe: pd.core.frame.DataFrame,
                      partitioning_columns: list=[],
                      order_columns: list=[],
                      row_number_label: str="rownumber",
                      order_columns_to_sort_ascending: list=[],
                      order_columns_to_sort_descending: list=[]):
    """
    Computes a rownumber column on a dataframe, based on paritioning and order columns.

    :param dataframe: pd.core.frame.DataFrame: A pandas dataframe.
    :param partitioning_columns: list: The dataframe columns to use as partitioning keys.
    :param order_columns: list: The dataframe columns to use to sort rows.
    :param row_number_label: str: The name of the 'rownumber' column.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the ascending order.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the descending order.

    :returns: dataframe: pandas.core.frame.DataFrame: The dataframe with the computed rownumber.
    """
    dataframe = prepare_dataframe_for_window(dataframe,
                                             partitioning_columns,
                                             order_columns,
                                             order_columns_to_sort_ascending,
                                             order_columns_to_sort_descending)
    dataframe[row_number_label] = dataframe.groupby(partitioning_columns).cumcount() + 1
    return dataframe


def compute_column_lag_or_leads(dataframe: pd.core.frame.DataFrame,
                                target_column: str,
                                partitioning_columns: list=[],
                                order_columns: list=[],
                                order_columns_to_sort_ascending: list=[],
                                order_columns_to_sort_descending: list=[],
                                lag_values_to_retrieve: list=[],
                                lead_values_to_retrieve: list=[]):
    """
    Computes a lag/lead values of a dataframe column, based on paritioning and order columns.

    :param dataframe: pd.core.frame.DataFrame: A pandas dataframe.
    :param target_column: str: The column on which the lag/lead values must be computed.
    :param partitioning_columns: list: The dataframe columns to use as partitioning keys.
    :param order_columns: list: The dataframe columns to use to sort rows.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the ascending order.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the descending order.
    :param lag_values_to_retrieve: list: A list containing the indexes of the lag values to retrieve in each row.
        Example: 'lag_values_to_retrieve' = [1, 3, 7] will retrieve the values that are 1, 3 and 7 rows before each row.
    :param lead_values_to_retrieve: list: A list containing the indexes of the lead values to retrieve in each row.
        Example: 'lead_values_to_retrieve' = [1, 3, 7] will retrieve the values that are 1, 3 and 7 rows after each row.

    :returns: dataframe: pandas.core.frame.DataFrame: The dataframe with the computed lag/lead values.
    """
    if (not lag_values_to_retrieve) and (not lead_values_to_retrieve):
        log_message =\
            f"""You set bad parameters in the function: Both 'lag_values_to_retrieve' and 'lead_values_to_retrieve' are empty. """\
            f"""Please fill at list one of the two lists."""
        raise Exception(log_message) 
    dataframe = prepare_dataframe_for_window(dataframe,
                                             partitioning_columns,
                                             order_columns,
                                             order_columns_to_sort_ascending,
                                             order_columns_to_sort_descending)
    def apply_lag_or_lead(group):
        for lag_index in lag_values_to_retrieve:
            group[f'{target_column}_lag_{lag_index}'] = group[target_column].shift(lag_index)
        for lead_index in lead_values_to_retrieve:
            group[f'{target_column}_lead_{lead_index}'] = group[target_column].shift(-lead_index)
        return group

    dataframe = dataframe.groupby(partitioning_columns, as_index=False).apply(apply_lag_or_lead)
    return dataframe


def prepare_dataframe_for_window(dataframe: pd.core.frame.DataFrame,
                      partitioning_columns: list=[],
                      order_columns: list=[],
                      order_columns_to_sort_ascending: list=[],
                      order_columns_to_sort_descending: list=[]):
    """
    Prepares a dataframe for window computations.

    :param dataframe: pd.core.frame.DataFrame: A pandas dataframe.
    :param partitioning_columns: list: The dataframe columns to use as partitioning keys.
    :param order_columns: list: The dataframe columns to use to sort rows.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the ascending order.
    :param order_columns_to_sort_ascending: list: The dataframe columns to use to sort rows in the descending order.

    :returns: dataframe: pandas.core.frame.DataFrame: The dataframe prepared to apply window functions
    """
    if not partitioning_columns:
        partitioning_columns = []
    if not order_columns:
        order_columns = []
    if (not partitioning_columns) and (not order_columns):
        log_message =\
            f"""You set bad parameters in the function: Both 'partitioning_columns' and 'order_columns' are empty. """\
            f"""Please fill at list one of the two lists"""
        raise Exception(log_message)
    
    intersection_between_partitioning_and_order_columns = set(partitioning_columns).intersection(order_columns)
    if intersection_between_partitioning_and_order_columns:
        log_message = """You can't have columns being the role of both 'partitioning' and 'order' columns. """\
        f"""The following columns are in this case: {intersection_between_partitioning_and_order_columns}"""
        raise Exception(log_message)

    if partitioning_columns:
        order_columns_ascending = [True for __ in partitioning_columns]
    else:
        order_columns_ascending = []

    for column_name in order_columns:
        if column_name in order_columns_to_sort_ascending:
            order_columns_ascending.append(True)
        else:
            if column_name in order_columns_to_sort_descending:
                order_columns_ascending.append(False)
            else:
                order_columns_ascending.append(True)
    if order_columns:
        dataframe = dataframe.sort_values(by=partitioning_columns+order_columns, ascending=order_columns_ascending)
    else:
        dataframe = dataframe.sort_values(by=partitioning_columns+order_columns)
    return dataframe