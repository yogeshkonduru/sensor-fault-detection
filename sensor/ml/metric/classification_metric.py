from sensor.entity.artifact_entity import ClassificationMetricArifact
from sensor.exception import SensorException
from sklearn.metrics import f1_score, precision_score,recall_score
import os,sys


def get_classification_score(y_true,y_pred)->ClassificationMetricArifact:
    try:
        model_f1_score = f1_score(y_true,y_pred)
        model_recall_score = recall_score(y_true,y_pred)
        model_precison_score = precision_score(y_true,y_pred)

        classification_metric =  ClassificationMetricArifact(f1_score = model_f1_score,
                precison_score=model_precison_score,
                recall_score=model_recall_score)
        return classification_metric
    except Exception as e:
        raise SensorException(e,sys)