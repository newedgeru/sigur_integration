from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

environment = {
    "storage_api": os.getenv("STORAGE_API", "storage_api:8080/api"),
    "search_api": os.getenv("SEARCH_API", "search:8089"),
    "dnn_api": os.getenv("DNN_API", "dnnapi:8080/dnnapi"),
    "data_storage_path": os.getenv("DATA_STORAGE_PATH", "/storage/ivac"),
}


@dataclass
class Config:
    storage_api: str
    search_api: str
    dnn_api: str
    data_storage_path: str


def get_config():
    return Config(**environment)
