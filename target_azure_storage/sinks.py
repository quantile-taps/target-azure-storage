"""Azure Storage target sink class, which handles writing streams."""


import pandas as pd
from singer_sdk.sinks import BatchSink


class AzureStorageSink(BatchSink):
    """Azure Storage target sink class."""

    max_size = 10000  # Max records to write in one batch
    batches = {}  # Buffer for the incoming records

    def start_batch(self, context: dict) -> None:
        """
        Create a new batch in memory
        """
        self.batches[context["batch_id"]] = []

    def process_record(self, record: dict, context: dict) -> None:
        """
        Append the record to the batch
        """
        self.batches[context["batch_id"]].append(record)

    def format_file_name(self, context: dict) -> str:
        # Get the naming convention from the settings
        naming_convention = self.config["naming_convention"]

        # Get all possible variables we need to replace
        stream_name = self.stream_name
        date = context["batch_start_time"].strftime('%Y-%m-%d')
        time = context["batch_start_time"].strftime('%H:%M:%S')
        datetime = context["batch_start_time"].strftime('%Y%m%dT%H%M%S')

        # Replace all variables in the file name
        file_name = naming_convention.replace("{stream}", stream_name)
        file_name = file_name.replace("{date}", date)
        file_name = file_name.replace("{time}", time)
        file_name = file_name.replace("{timestamp}", datetime)

        return file_name

    def store_dataframe(
        self,
        df: pd.DataFrame,
        file_name: str,
    ) -> None:
        """
        Store the dataframe in Azure storage.

        Args:
            df (pd.DataFrame): The dataframe to store.
            file_name (str): The file name to store the dataframe as.

        Raises:
            ValueError: If the file extension is not supported.
        """
        configuration = {}

        # Switch for all the different file formats
        if file_name.endswith(".parquet"):
            storage_function = df.to_parquet
            configuration = {"engine": "pyarrow"}
        elif file_name.endswith(".json"):
            storage_function = df.to_json
        elif file_name.endswith(".jsonlines"):
            storage_function = df.to_json
            configuration = {"lines": True, "orient": "records"}
        elif file_name.endswith(".csv"):
            storage_function = df.to_csv
        else:
            raise ValueError("The specified file format is not supported")

        # Call the defined storage function
        storage_function(
            f"abfs://{file_name}",
            storage_options={
                "account_name": self.config["storage_account_name"],
                "account_key": self.config["storage_account_key"],
            },
            **configuration,
        )

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written."""
        # Transform the records to a dataframe
        df = pd.DataFrame(self.batches[context["batch_id"]])

        # Replace the variables in the naming convention
        file_name = self.format_file_name(context)

        # Store the dataframe in Azure storage
        self.store_dataframe(df, file_name)
