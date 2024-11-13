import pandas as pd
import re


def clean_column_name_for_storage(column_name: str, output_case: str="lowercase"):
    """
    Cleans a column name to prevent issues when generating/filling data in a storage.

    :param column_name: str: The name of the column to clean.
    :param output_case: str: The case to use for the output column name.

    :returns: cleaned_column_name: str: The cleaned column name.
    """
    # Define a regular expression pattern for problematic characters
    # This pattern includes whitespaces, punctuation, and control characters
    FORBIDDEN_CHARACTERS_PATTERN = r'[ \t\n\r\f\v,;:\'"`\\/\|!?.*&%$#@+<>\[\]{}()\^~\-\=\0-\x1F\x7F]'

    # Replace the matched characters with '_'
    cleaned_column_name = re.sub(FORBIDDEN_CHARACTERS_PATTERN, '_', column_name)

    # Optional: Handle starting with a number by prefixing with an underscore
    if cleaned_column_name and cleaned_column_name[0].isdigit():
        cleaned_column_name = '_' + cleaned_column_name
    
    if output_case == "lowercase":
        cleaned_column_name = cleaned_column_name.lower()
    elif output_case == "uppercase":
        cleaned_column_name = cleaned_column_name.upper()
    return cleaned_column_name


def clean_dataframe_column_names_for_storage(dataframe: pd.core.frame.DataFrame, output_case: str="lowercase"):
    """
    Cleans all dataframe columns to prevent issues when generating/filling data in a storage.

    :param dataframe: pd.core.frame.DataFrame: The dataframe of concern.
    :param output_case: str: The case to use for the output column names.

    :returns: dataframe: pd.core.frame.DataFrame: The dataframe with cleaned column names.
    """
    dataframe.columns = [clean_column_name_for_storage(str(col), output_case) for col in dataframe.columns]
    return dataframe