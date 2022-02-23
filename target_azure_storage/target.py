"""Azure Storage target class."""

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_azure_storage.sinks import AzureStorageSink


class TargetAzureStorage(Target):
    """Sample target for Azure Storage."""

    name = "target-azure-storage"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "storage_account_name",
            th.StringType,
            required=True,
            description="Azure storage account name.",
        ),
        th.Property(
            "storage_account_key",
            th.StringType,
            description="Azure storage account key.",
        ),
        th.Property(
            "naming_convention",
            th.StringType,
            description="""
                The format of the parquet file location. Use {stream}, {date}, {time} and {timestamp} as variables.
                You can also define different file formats: 'parquet', 'json', 'jsonlines' and 'csv'.
            """,
        ),
    ).to_dict()
    default_sink_class = AzureStorageSink
