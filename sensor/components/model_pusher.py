from sensor.logger import logging
from sensor.exception import SensorException
import os,sys
import pandas as pd
from sensor.utils.main_utils import save_object,load_object,write_yaml_file
from sensor.entity.artifact_entity import ModelEvaluationArtifact,ModelPusherArtifact
from sensor.entity.config_entity import ModelPusherConfig
from sensor.ml.metric.classification_metric import get_classification_score
from sensor.ml.model.estimator import SensorModel,ModelResolver
import shutil

class ModelPusher:

    def __init__(self,model_evaluation_artifact: ModelEvaluationArtifact,
        model_pusher_config: ModelPusherConfig):
        try:
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
        except Exception as e:
            raise SensorException(e,sys)
    
    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            trained_model_path = self.model_evaluation_artifact.trained_model_path
            
            #creating model pusher dir to save model
            model_file_path = self.model_pusher_config.model_file_path 
            os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
            shutil.copy(src=trained_model_path,dst=model_file_path)

            #saved model directory 
            saved_model_path = self.model_pusher_config.saved_model_file_path
            os.makedirs(os.path.dirname(saved_model_path), exist_ok=True)
            shutil.copy(src=trained_model_path,dst=saved_model_path)

            #prepare artifact
            model_pusher_artifact= ModelPusherArtifact(saved_model_path=saved_model_path,model_file_path=model_file_path)
            return model_pusher_artifact
        except Exception as e:
            raise SensorException(e,sys)        
