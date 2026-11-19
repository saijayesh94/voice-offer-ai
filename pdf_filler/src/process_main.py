import os
import re
import time

from dotenv import load_dotenv

# Load pdf_filler/.env before importing modules that read credentials
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from process_pdf import PDFUpdater

app = FastAPI()
router = APIRouter()
# router = APIRouter(prefix="/ai_ws")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)   


@router.post("/fill_pdf")
async def chat(payload: dict):
    
    try:
        updater = PDFUpdater(payload['pdf_fields'], payload['envelope_args'])
        updater.process_files()
        return {"status": "success", "message": ""}
    
    except Exception as e:
        print("Exception", str(e))
        return {"status": "fail", "message": "Internal Server Error!!:", "resp_obj": ""}
    


app.include_router(router)

# -----------------------------------------------------

# app.ds_conn_obj = DataSourceConnector.connect()

# app.mysql_last_recylced = time.time()
# def recycle_connecions():
#     curr_time = time.time()
#     elapsed_time = curr_time - app.mysql_last_recylced
#     CustomLogger.info(f"Elapsed time since last mysql recycled : {elapsed_time}")

#     if elapsed_time >= 100:
#         # CustomLogger.info(f"Recycling connection...")
#         app.ds_conn_obj = DataSourceConnector.connect() 
#     else:
#         pass
#         # CustomLogger.info(f"Connection reused...")
#     app.mysql_last_recylced = time.time()


# @router.post("/chat", dependencies=[Depends(recycle_connecions)])
