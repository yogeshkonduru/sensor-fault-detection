from sensor.configuration.mongo_db_connection import MongoDBClient
from sensor.exception import SensorException
import os,sys
from sensor.logger import logging
from sensor.pipeline import training_pipeline
from sensor.pipeline.training_pipeline import TrainPipeline
import pandas as pd
from sensor.utils.main_utils import read_yaml_file
from sensor.constant.training_pipeline import SAVED_MODEL_DIR, PREDICTED_FILE_NAME
from sensor.constant.training_pipeline import UPLOAD_FILE_NAME
from fastapi import FastAPI, File, UploadFile
from sensor.constant.application import APP_HOST, APP_PORT
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from fastapi.responses import Response, FileResponse
from sensor.ml.model.estimator import ModelResolver,TargetValueMapping
from sensor.utils.main_utils import load_object
from fastapi.middleware.cors import CORSMiddleware
import shutil

predict_file_path = os.path.join(os.getcwd(),PREDICTED_FILE_NAME)
upload_file_path  = os.path.join(os.getcwd(),UPLOAD_FILE_NAME)
env_file_path=os.path.join(os.getcwd(),"env.yaml")

def set_env_variable(env_file_path):

    if os.getenv('MONGO_DB_URL',None) is None:
        env_config = read_yaml_file(env_file_path)
        os.environ['MONGO_DB_URL']=env_config['MONGO_DB_URL']


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:

        train_pipeline = TrainPipeline()
        if train_pipeline.is_pipeline_running:
            return Response("Training pipeline is already running.")
        train_pipeline.run_pipeline()
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")

@app.post("/uploadfile")
async def predict_data(file: UploadFile = File(...)):
    try:
        with open (f'{upload_file_path}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"file_name": file.filename}
    except Exception as e:
        raise Response(f"Error Occured! {e}")

@app.get("/predict")
async def predict_route():
    try:
        if not os.path.exists(upload_file_path):
            return {"error": "Please upload a file to predict"}        
        df=pd.read_csv(upload_file_path)
        model_resolver = ModelResolver(model_dir=SAVED_MODEL_DIR)
        if not model_resolver.is_model_exists():
            return Response("Model is not available")
        
        best_model_path = model_resolver.get_best_model_path()
        model = load_object(file_path=best_model_path)
        y_pred = model.predict(df)
        df['predicted_column'] = y_pred
        df['predicted_column'].replace(TargetValueMapping().reverse_mapping(),inplace=True)
        # if os.path.exists(upload_file_path):
        #     os.remove(upload_file_path)
        df.to_csv(predict_file_path)
        if os.path.exists(predict_file_path):
            return FileResponse(predict_file_path)
        return {"error": "File does not exist"}
        
    except Exception as e:
        raise Response(f"Error Occured! {e}")

        
def main():
    try:
        set_env_variable(env_file_path)
        training_pipeline = TrainPipeline()
        training_pipeline.run_pipeline()
    except Exception as e:
        print(e)
        logging.exception(e)


if __name__=="__main__":
    #main()
    set_env_variable(env_file_path)
    app_run(app, host=APP_HOST, port=APP_PORT)
