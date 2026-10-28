from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os, win32api
import subprocess
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
        print("[PRINT] 1. Checking authorization", flush=True)

        if authorization_token != AUTH_TOEKN or not pdf_url.startswith(WEBSITE_URL):
            print("[PRINT] Unauthorized request", flush=True)
            return {"status": "error", "message": "Unauthorized"}

        print("[PRINT] 2. Downloading PDF...", flush=True)

        headers = {"Print-Authorization-Token": AUTH_TOEKN}
        r = requests.get(
            pdf_url,
            headers=headers,
            verify=False,
            timeout=(5, 30)
        )
        r.raise_for_status()

        print(f"[PRINT] 3. Download complete: HTTP {r.status_code}, {len(r.content)} bytes", flush=True)

        os.makedirs("pdf", exist_ok=True)
        file_path = Path("pdf") / "label.pdf"

        with open(file_path, "wb") as f:
            f.write(r.content)

        print(f"[PRINT] 4. PDF saved: {file_path.resolve()}", flush=True)

        print("[PRINT] 5. Starting Windows print...", flush=True)
        # os.startfile(str(file_path.resolve()), "print")
        # win32api.ShellExecute(0, "print", str(file_path), None,  ".",  0)
        
        PDF_READER = r"C:\Users\hp\AppData\Local\SumatraPDF\SumatraPDF.exe"
        PRINTER = "Deli 740C Printer"
        
        cmd = [
            PDF_READER,
            "-print-to", PRINTER,
            "-silent",
            str(file_path.resolve()),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
      
        if result.returncode != 0:
            raise RuntimeError(
                f"PDF printing failed: {result.returncode}\n"
                f"{result.stdout}\n{result.stderr}"
            )

        print("[PRINT] 6. Print command sent", flush=True)

        return {
            "status": "success",
            "message": "Printing started"
        }

    except Exception as e:
        print(f"[PRINT] ERROR: {type(e).__name__}: {e}", flush=True)
        raise
