from sensor.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig, ModelEvaluationConfig, ModelPusherConfig
from sensor.exception import SensorException
from sensor.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, DataTransformationArtifact, ModelTrainerArtifact, ModelEvaluationArtifact, ModelPusherArtifact
from sensor.components.data_ingestion import DataIngestion
from sensor.components.data_validation import DataValidation
from sensor.components.data_transformation import DataTransformation
from sensor.components.model_evaluation import ModelEvaluation
from sensor.components.model_trainer import ModelTrainer
from sensor.components.model_pusher import ModelPusher
from sensor.cloud_storage.s3_syncer import S3Sync
from sensor.constant.s3_bucket import TRAINING_BUCKET_NAME
from sensor.constant.training_pipeline import SAVED_MODEL_DIR

import sys,os
from sensor.logger import logging

class TrainPipeline:
    is_pipeline_running=False
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()
        # self.data_ingestion_config = DataIngestionConfig(training_pipeline_config = training_pipeline_config)
        # self.training_pipeline_config = TrainingPipelineConfig
    
    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config = self.training_pipeline_config)
            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()

            logging.info("data ingestion completed and artifact: %s", data_ingestion_artifact)
            return data_ingestion_artifact
        except Exception as e:
            raise SensorException(e,sys)

    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact)->DataValidationArtifact:
        try:
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data Validation")
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config = data_validation_config
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f"Data validation completed and artifact: {data_validation_artifact}")
            return data_validation_artifact
        except  Exception as e:
            raise  SensorException(e,sys)
    
    def start_data_transformation(self,data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            data_tranformation_config = DataTransformationConfig(training_pipeline_config = self.training_pipeline_config)
            logging.info("Started data transformation")
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_tranformation_config
            )
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info(f"Data transformation completed and artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise SensorException(e,sys)

    def start_model_trainer(self,data_transformation_artifact: DataTransformationArtifact):
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting model trainer")
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=model_trainer_config)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info(f"Model trainer completed and artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise SensorException(e,sys)

    def start_model_evaluation(self,model_trainer_artifact: ModelTrainerArtifact,data_validation_artifact: DataValidationArtifact):
        try:
            model_eval_config = ModelEvaluationConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info("Starting Model evaluation")
            model_evaluation = ModelEvaluation(model_eval_config=model_eval_config,
                data_validation_artifact=data_validation_artifact,
                model_trainer_artifact=model_trainer_artifact)
            model_evaluation_arifact = model_evaluation.initiate_model_evaluation()
            logging.info(f"Model evaluation completed and artifact: {model_evaluation_arifact}")
            return model_evaluation_arifact
        except Exception as e:
            raise SensorException(e,sys)

    def start_model_pusher(self,model_evaluation_artifact: ModelEvaluationArtifact):
        try:
            model_pusher_config = ModelPusherConfig(training_pipeline_config= self.training_pipeline_config)
            logging.info("Starting Model evaluation")
            model_pusher = ModelPusher(model_evaluation_artifact=model_evaluation_artifact,
                model_pusher_config=model_pusher_config)
            model_pusher_artifact = model_pusher.initiate_model_pusher()
            logging.info(f"Model Pusher completed and artifact: {model_pusher_artifact}")
            return model_pusher_artifact
        except Exception as e:
            raise SensorException(e,sys)

    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise SensorException(e,sys)

    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/{SAVED_MODEL_DIR}"
            self.s3_sync.sync_folder_to_s3(folder = SAVED_MODEL_DIR,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise SensorException(e,sys)

    def run_pipeline(self):
        try:
            TrainPipeline.is_pipeline_running=True

            data_ingestion_artifact:DataIngestionArtifact = self.start_data_ingestion()
            data_validation_artifact:DataValidationArtifact = self.start_data_validation(data_ingestion_artifact = data_ingestion_artifact)
            data_transformation_artifact:DataTransformationArtifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact =data_transformation_artifact)
            model_evaluation_artifact = self.start_model_evaluation(model_trainer_artifact = model_trainer_artifact, data_validation_artifact=data_validation_artifact)
            if not model_evaluation_artifact.is_model_accepted:
                raise Exception("Trained model is not better than the best model")
            model_pusher_arifact = self.start_model_pusher(model_evaluation_artifact = model_evaluation_artifact)
            TrainPipeline.is_pipeline_running=False
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
        except Exception as e:
            self.sync_artifact_dir_to_s3()
            raise SensorException(e,sys)