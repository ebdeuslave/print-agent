from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from pathlib import Path
from __auth__ import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrintRequest(BaseModel):
    url: str
    authorization_token: str

@app.post("/print")
def print_pdf(data: PrintRequest):
    authorization_token = data.authorization_token
    pdf_url = data.url

    try:
        # check autorization token
        if (authorization_token != AUTH_TOEKN) or not pdf_url.startswith(WEBSITE_URL):
            return {
                "status": "error",
                "message": "Unauthorized"
            }

        # 1. download PDF
        headers = {'Print-Authorization-Token':AUTH_TOEKN}
        r = requests.get(pdf_url, headers=headers, verify=False)
        # r.raise_for_status()
        print('received url ->', pdf_url)

        os.makedirs('pdf', exist_ok=True)
        file_path = Path('pdf') / Path('label.pdf')
        with open(file_path, "wb") as f:
            f.write(r.content)

        # # 2. silent print (Windows only)
        os.startfile(file_path, "print")

        return {
            "status": "success",
            "message": "Printing started"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }