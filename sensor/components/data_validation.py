from distutils import dir_util
from sensor.constant.training_pipeline import SCHEMA_FILE_PATH
from sensor.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from sensor.entity.config_entity import DataValidationConfig
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.utils.main_utils import read_yaml_file,write_yaml_file
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
class DataValidation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                        data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise  SensorException(e,sys)
    
    def drop_zero_std_columns(self,dataframe):
        pass


    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self._schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns:
                return True
            return False
        except Exception as e:
            raise SensorException(e,sys)

    def is_numerical_column_exist(self,dataframe:pd.DataFrame)->bool:
        try:
            numerical_columns = self._schema_config["numerical_columns"]
            dataframe_columns = dataframe.columns

            numerical_column_present = True
            missing_numerical_columns = []
            for num_column in numerical_columns:
                if num_column not in dataframe_columns:
                    numerical_column_present=False
                    missing_numerical_columns.append(num_column)
            
            logging.info(f"Missing numerical columns: [{missing_numerical_columns}]")
            return numerical_column_present
        except Exception as e:
            raise SensorException(e,sys)       

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try :
            return pd.read_csv(file_path)
        except Exception as e :
            raise SensorException(e,sys)        

    def detect_dataset_drift(self):
        try :
            pass
        except Exception as e :
            raise SensorException(e,sys)

    def initiate_data_validation(self)->DataValidationArtifact:
        try :
            error_message = ""
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            #reading the data from train and test file location
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            #validate number of columns
            status = self.validate_number_of_columns(dataframe= train_dataframe)
            if not status:
                error_message = f"{error_message} train dataframe does not contain all columns"

            status = self.validate_number_of_columns(dataframe = test_dataframe)
            if not status:
                error_message = f"{error_message} test dataframe does not contain all columns"

            #validate numerical columns
            status = self.is_numerical_column_exist(dataframe = train_dataframe)
            if not status:
                error_message =f"{error_message} train dataframe does not contain all numerical columns"

            status = self.is_numerical_column_exist(dataframe = test_dataframe)
            if not status:
                error_message =f"{error_message} test dataframe does not contain all numerical columns"

            if len(error_message)>0:
                raise Exception(error_message)

            #let's check for the data drift
            return None
           
        except Exception as e :
            raise SensorException(e,sys)