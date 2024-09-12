from langchain.agents import tool
from typing import List, Dict
import requests
from langchain_community.retrievers import AzureCognitiveSearchRetriever
import os
import config


"""
This file holds the tools, that can be bound to the AgentExecutor object.
Here, we define new functions that the agent can invoke and that help it to solve the tasks. These functions
can, e.g., include database operations, real time log queries, control of the factory, etc.
Be careful though, the AI itself decides, based on the provided docstring, which tool to invoke and what
parameters to pass! So carefully consider, which tools you want to add... ;)
"""


### HELP-TOOL: GET INFORMATION ABOUT THE DATABASE ###


@tool
def get_db_info() -> str:
    """
    This function can be used to retrieve information about the database, that can be accessed.
    It returns a text describing the database's structure for the user.

    Returns:
        str: text, describing the database-structure
    """

    return config.DATABASE_DESCR


### TASK 1: GET IIOT DATA (input, ambient, machine, qa) ###


@tool
def get_machine_data(
    from_timestamp: str | None,
    to_timestamp: str | None,
    min_comb_op_tmp_1: int = 0,
    max_comb_op_tmp_1: int = 200,
    min_comb_op_tmp_2: int = 0,
    max_comb_op_tmp_2: int = 200,
    min_comb_op_tmp_3: int = 0,
    max_comb_op_tmp_3: int = 200,
    min_material_pressure: int = 0,
    max_material_pressure: int = 1000,
    min_material_temperature: int = 0,
    max_material_temperature: int = 200,
    min_motor_rpm: int = 0,
    max_motor_rpm: int = 3000,
) -> str:
    """
    This function can be used to get data of machine 1 for a given timespan.

    For each column in the machine table, there exists a min and a max parameter to filter values.

    You can filter by time using the parameters from_timestamp and to_timestamp. All timestamps are in UTC.

    Args:
        from_timestamp (str | None): Start timestamp for filtering (format: %Y-%m-%d %H:%M:%S)
        to_timestamp (str | None): End timestamp for filtering (format: %Y-%m-%d %H:%M:%S)

    Returns:
        str: A list containing a dict for every sample. Each dict contains the keys combiner_operation_temperature_1, combiner_operation_temperature_2, combiner_operation_temperature_3, id, material_pressure, material_temperature, motor_rpm and time_stamp.
    """

    # Send the request to get the data from the machine endpoint
    results = requests.get(config.BACKEND_URL + "/machine", params={
        'from_ts': from_timestamp,
        'to_ts': to_timestamp,
        'min_comb_op_tmp_1': min_comb_op_tmp_1,
        'max_comb_op_tmp_1': max_comb_op_tmp_1,
        'min_comb_op_tmp_2': min_comb_op_tmp_2,
        'max_comb_op_tmp_2': max_comb_op_tmp_2,
        'min_comb_op_tmp_3': min_comb_op_tmp_3,
        'max_comb_op_tmp_3': max_comb_op_tmp_3,
        'min_material_pressure': min_material_pressure,
        'max_material_pressure': max_material_pressure,
        'min_material_temperature': min_material_temperature,
        'max_material_temperature': max_material_temperature,
        'min_motor_rpm': min_motor_rpm,
        'max_motor_rpm': max_motor_rpm,
    })

    print(results.text)

    return results.text


@tool
def get_ambient(
    from_timestamp: str | None,
    to_timestamp: str | None,
    min_value_humidity: int = 0,
    max_value_humidity: int = 100,
    min_value_amb_temperature: int = 0,
    max_value_amb_temperature: int = 100,
    min_value_zone_1_temperature: int = 0,
    max_value_zone_1_temperature: int = 100,
) -> str:
    """
    This function can be used to get ambient data of the machine floor for a given timespan.  

    For each column in the ambient table, there exists a min and a max parameter to filter values.

    You can filter by time using the parameters from_timestamp and to_timestamp. All timestamps are in UTC.

    Args:
        from_timestamp (str | None): Start timestamp for filtering (format: %Y-%m-%d %H:%M:%S)
        to_timestamp (str | None): End timestamp for filtering (format: %Y-%m-%d %H:%M:%S)

    Returns:
        str: A list containing a dict for every sample. Each dict contains the keys ambient_humidity, ambient_temperature, id, time_stamp and zone_1_temperature.
    """

    # Send the request to get the data from the ambient endpoint
    results = requests.get(config.BACKEND_URL + "/ambient", params={
        'from_ts': from_timestamp,
        'to_ts': to_timestamp,
        'min_value_humidity': min_value_humidity,
        'max_value_humidity': max_value_humidity,
        'min_value_amb_temperature': min_value_amb_temperature,
        'max_value_amb_temperature': max_value_amb_temperature,
        'min_value_zone_1_temperature': min_value_zone_1_temperature,
        'max_value_zone_1_temperature': max_value_zone_1_temperature,
    })

    print(results.text)

    return results.text


# Question: Do you need to invoke the API Endpoints for the other tables as well? (input, ambient, qa)


### TASK 2: QUERY LOGS-API-ENDPOINT ###

@tool
def get_logs() -> str:
    """
    Returns error messages for machine 1. The result is a list of dictionaries containing an id, message and timestamp.

    All timestamps are in UTC.

    Returns:
        List[Dict[str, str]]: ...
    """

    results = requests.get(config.BACKEND_URL + "/logs")

    print(results.text)

    return results.text


### TASK 3: QUERY DOCUMENTATION USING RAG ###


@tool
def query_documentation(question: str) -> str:
    """
    ### Description of the function
    ### IMPORTANT! The LLM decides to call it or not based on this docstring!

    Args:
        question (str): Short description of required information or question that can be answered using the documentation

    Returns:
        str: Answer to the passed question
    """

    # Create instance of the class AzureCognitiveSearchRetriever
    retriever = AzureCognitiveSearchRetriever(
        content_key="content",
        service_name="hackathon-v2-ai-search",
        index_name="hackathon-v2-vector-idx-2",
        api_key=os.environ.get("AZURE_SEARCH_KEY"),
        top_k=10,
    )

    # Get the top_k most relevant chunks based on the question
    pass

    # Optional: Filter the retrieved documents based on a score-threshold (doc.metadata["@search.score"])
    pass

    # Build the new prompt that contains both the question as well as the relevant chunks
    pass

    # Create new ChatOpenAI instance to submit the new prompt
    pass

    # Invoke the new ChatOpenAI instance to retrieve the final answer based on the provided context
    pass

    return None


### BONUS: TOOL FOR VISUALIZING COLUMNS OF A TABLE (FROM THE DATABASE) ###


@tool
def visualize(table: str, column: str) -> str:
    """
    ### Description of the function
    ### IMPORTANT! The LLM decides to call it or not based on this docstring!

    Args:
        table (str): the table that holds the column that should be plotted
        column (str): the numerical column to plot

    Returns:
        str: the url in the backend that the visualization can be accessed with
    """

    # Create the URL to fetch the data from the correct endpoint
    pass

    # Fetch the data from the API using the URL
    pass

    # Plot the sedired column (using matplotlib)
    pass

    # Save the resulting figure on this webserver (in this case locally)
    pass

    # Return a response to the AI containing the markdown to display the image
    # --> Create a separate API endpoint for this
    return None
