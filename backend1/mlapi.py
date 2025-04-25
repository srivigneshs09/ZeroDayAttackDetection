from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import pickle
import joblib
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn
import warnings
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from passlib.context import CryptContext
from typing import Dict

warnings.filterwarnings("ignore")

app = FastAPI()
load_dotenv()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection details
mongodb_username = os.getenv("MONGODB_USERNAME")
mongodb_password = os.getenv("MONGODB_PASSWORD")
mongodb_cluster = os.getenv("MONGODB_CLUSTER")
mongodb_db = os.getenv("MONGODB_DATABASE", "mydatabase")

# URL-encode username and password
encoded_username = quote_plus(mongodb_username)
encoded_password = quote_plus(mongodb_password)

# Construct MongoDB URI
mongodb_url = f"mongodb+srv://{encoded_username}:{encoded_password}@{mongodb_cluster}/{mongodb_db}?retryWrites=true&w=majority"
try:
    client = MongoClient(mongodb_url)
    db = client[mongodb_db]
    users_collection = db["users"]
except Exception as e:
    print(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model
class User(BaseModel):
    username: str
    password: str

# User registration endpoint
@app.post("/register")
def register(user: User):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        return {"message": False}
    hashed_password = pwd_context.hash(user.password)
    users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": True}

# User login endpoint
@app.post("/login")
def login(user: User):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user and pwd_context.verify(user.password, existing_user["password"]):
        return {"username": user.username, "message": True}
    return {"message": False}

# Load machine learning models
model_files = {
    "main_model": "./Models/RandomForestmodel",
    "botmodel": "./Models/bot_model.pkl",
    "ddos_model": "./Models/ddos_model.pkl",
    "ddoshulk_model": "./Models/ddoshulk_model.pkl",
    "dos_goldeneye_model": "./Models/dos_goldeneye_model.pkl",
    "dos_slowhttptest_model": "./Models/dos_slowhttptest_model.pkl",
    "dos_slowloris_model": "./Models/dos_slowloris_model.pkl",
    "ftppatator_model": "./Models/FTP- PATATOR_model.pkl",
    "infiltration_model": "./Models/infiltration_model.pkl",
    "ssh_patator_model": "./Models/ssh_patator_model.pkl",
    "webattack_bruteforce_model": "./Models/webattack_bruteforce_model.pkl",
    "webattack_sqlinjection_model": "./Models/webattack_sqlinjection_model.pkl",
}

models: Dict = {}
for model_name, model_path in model_files.items():
    try:
        models[model_name] = pickle.load(open(model_path, 'rb'))
    except Exception as e:
        print(f"Failed to load model {model_name} from {model_path}: {str(e)}")
        raise

# Map known attack models
known_attack_models = {
    models["botmodel"]: "bot",
    models["ddos_model"]: "ddos",
    models["ddoshulk_model"]: "ddoshulk",
    models["dos_goldeneye_model"]: "ddosgoldeneye",
    models["dos_slowhttptest_model"]: "dosslowhttptest",
    models["dos_slowloris_model"]: "dosslowloris",
    models["ftppatator_model"]: "ftppatator",
    models["infiltration_model"]: "infiltration",
    models["ssh_patator_model"]: "sshpatator",
    models["webattack_bruteforce_model"]: "webattackbruteforce",
    models["webattack_sqlinjection_model"]: "webattacksqlinjection",
}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), username: str = Form(...)):
    try:
        df = pd.read_csv(file.file, index_col=False, dtype='unicode')
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return {"error": "Invalid CSV file"}

    df.dropna(inplace=True)
    df = df[~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)]

    # Uncomment if specific columns need to be dropped for CICIDS2017 dataset
    # colsfromindex = [' Subflow Bwd Bytes',' ECE Flag Count',' Fwd URG Flags',' Active Max','Init_Win_bytes_forward',' act_data_pkt_fwd',' Bwd Header Length',' min_seg_size_forward',' Fwd Header Length', ' Label']
    # df.drop(colsfromindex, axis=1, inplace=True, errors='ignore')

    print("processing")
    # Convert to numeric and handle infinite/NaN values
    df = df.apply(pd.to_numeric, errors='coerce')
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    print("predicting")
    df_values = df.values
    try:
        prediction = models["main_model"].predict(df_values)
        prediction = (prediction > 0.5).astype(int)
        prediction = list(prediction)
    except Exception as e:
        print(f"Error during main model prediction: {str(e)}")
        return {"error": "Prediction failed"}

    count_0, count_1 = prediction.count(0), prediction.count(1)

    if count_1 == 0:  # BENIGN
        return {
            "Prediction": "Not Malicious",
            "nonmal": count_0,
            "mali": count_1,
            "attack": "NA",
        }
    else:  # MALICIOUS
        attack = ""
        no_of_records = len(df_values)

        for model in known_attack_models:
            try:
                whichpred = model.predict(df_values)
                inliers = list(whichpred).count(1)
                if inliers > (no_of_records // 2):
                    attack = known_attack_models[model]
                    break
            except Exception as e:
                print(f"Error during attack model prediction: {str(e)}")
                continue

        if attack == "":
            attack = "zeroday"

        send_email(username, attack)
        print(attack)
        return {
            "Prediction": "malicious",
            "nonmal": count_0,
            "mali": count_1,
            "attack": attack,
        }

def send_email(email: str, attack: str):
    # Email configuration
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("Email credentials not found in .env")
        return

    subject = f"Urgent Security Alert: {attack} Attack Detected"
    
    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    body = f"""
Dear {email},

We regret to inform you that upon conducting a thorough analysis of your network logs, we have discovered some alarming findings. It appears that your network has been targeted and attacked by a malicious entity utilizing the {attack} method.

This type of attack can have severe consequences, ranging from data breaches to system malfunctions. To safeguard your network and protect your sensitive information, we strongly recommend taking immediate action.

We understand that this situation is concerning, but taking proactive measures is crucial for protecting your network from further harm.

Please do not hesitate to reach out if you require any assistance or guidance during this process. Our team is here to support you in any way we can.

Stay vigilant,

Team 41,
Detective Zero-day.
"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)