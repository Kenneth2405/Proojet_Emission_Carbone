from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import os
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv
from carbone import Carbone

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv('ALGORITHM')
SHARED_PASSWORD = os.getenv('SHARED_PASSWORD')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class EmissionRequest(BaseModel):
    ville_depart: str = "cotonou"
    ville_arrivee: str = "paris"
    langue: str = "FR"

class Password(BaseModel):
    password: str

@app.post("/token")
async def generate_token(password_data: Password):
    if password_data.password != SHARED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": "user"}  # Utilisateur générique
    token = create_access_token(data=token_data)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/calcul-emission")
def calcul_emission(trajet: EmissionRequest, token: str):
    payload = verify_token(token)
    carbone = Carbone(trajet.ville_depart, trajet.ville_arrivee, trajet.langue)
    meilleur_mode, meilleur_emission, valeurs, details = carbone.calcul_emission()
    recommandations = carbone.generer_recommandation_par_llama(valeurs)

    return {
        "meilleur_mode": meilleur_mode,
        "meilleur_emission": meilleur_emission,
        "valeurs": valeurs,
        "details": details,
        "recommandations": recommandations
    }
