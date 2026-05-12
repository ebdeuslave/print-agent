from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from pathlib import Path
# import win32api


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

@app.post("/print")
def print_pdf(data: PrintRequest):
    pdf_url = data.url

    try:
        # 1. download PDF
        r = requests.get(pdf_url, verify=False)
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