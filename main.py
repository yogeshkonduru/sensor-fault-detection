from sensor.configuration.mongo_db_connection import MongoDBClient
from sensor.constant import training_pipeline
from sensor.exception import SensorException
from sensor.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
import os,sys
from sensor.logger import logging
from sensor.pipeline.training_pipeline import TrainPipeline

if __name__ == '__main__':
    training_pipeline= TrainPipeline()
    training_pipeline.run_pipeline()


# if __name__ == '__main__':
#     # training_pipeline_config = TrainingPipelineConfig()
#     # data_ingestion_config = DataIngestionConfig(training_pipeline_config)
#     # print(data_ingestion_config.__dict__)