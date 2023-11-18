from fastapi_poe.types import ProtocolMessage
from fastapi_poe.client import get_bot_response
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import FastAPI, File, UploadFile, Depends, Form

from typing import Optional, Dict

import asyncio

import uvicorn
from instagrapi import Client
import uuid
from dependencies import ClientStorage, get_clients

app = FastAPI()
concated= ""

# router = APIRouter()
# router.add_api_route('/api/v2/hello-world', 
# endpoint = HelloWorld().read_hello, methods=["GET"])
# app.include_router(router)

from pydantic import BaseModel


class Item(BaseModel):
    apikey: str
    request: str

# class InstaInfo(BaseModel):
#     account: str
#     password: str
#     description: str
#     file: UploadFile = File(...)


@app.post("/instagram/login")
async def auth_login(username: str = Form(...),
                     password: str = Form(...),
                     verification_code: Optional[str] = Form(""),
                     proxy: Optional[str] = Form(""),
                     locale: Optional[str] = Form(""),
                     timezone: Optional[str] = Form(""),
                     clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    if proxy != "":
        cl.set_proxy(proxy)

    if locale != "":
        cl.set_locale(locale)

    if timezone != "":
        cl.set_timezone_offset(timezone)

    result = cl.login(
        username,
        password,
        verification_code=verification_code
    )
    if result:
        clients.set(cl)
        return cl.sessionid
    return result

@app.post("/instagram/publish")
async def upload_media(file: UploadFile = File(...),
                       sessionid: str = Form(...),
                       caption: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)):
    
    cl = clients.get(sessionid)
    #cl.login(item.account, item.password)

    file.filename = f"uploaded.jpg"
    contents = await file.read()

    # save the file
    with open(f"./images/uploaded.jpg", "wb") as f:
        f.write(contents)

    media = cl.photo_upload("./images/uploaded.jpg", caption, 
    extra_data={
        "custom_accessibility_caption": "alt text example",
        "like_and_view_counts_disabled": 1,
        "disable_comments": 1,
    })
    
    return JSONResponse(content=media.pk, status_code=201)


@app.get("/instagram/publish_test")
async def upload_media():
    cl = Client()
    cl.login("daily.good.q", "i@264381")
    media = cl.photo_upload("./images/tree.jpg", "Test caption for photo with #hashtags and mention users such", 
    extra_data={
        "custom_accessibility_caption": "alt text example",
        "like_and_view_counts_disabled": 1,
        "disable_comments": 1,
    })
    
    return JSONResponse(content=media.pk, status_code=201)

@app.post("/liama")
async def call_liama(item: Item):
    global concated # 전역변수 사용
    await concat_message(item.apikey, item.request, "Llama-2-13b")
    
    return JSONResponse(content=concated, status_code=201)

@app.post("/call/{botname}")
async def call_liama(botname: str, item: Item):
    global concated # 전역변수 사용
    await concat_message(item.apikey, item.request, botname)
    
    return JSONResponse(content=concated, status_code=201)


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Hello world!"}, status_code=201)

@app.get("/gpt3")
async def call_gpt3(request: str, apikey: str):
    global concated # 전역변수 사용

    await concat_message(apikey, request, "GPT-3.5-Turbo")
    return {"message": concated}

@app.get("/gpt4/{request}")
async def call_gpt4(request: str, apikey: str):
    global concated # 전역변수 사용

    await concat_message(apikey, request, "GPT-4.0")
    return {"message": concated}

@app.get("/bot/{botname}")
async def call_bot(botname: str, request: str, apikey: str):
    global concated # use global variable

    await concat_message(apikey, request, botname)
    return {"message": concated}

async def concat_message(apikey, request, botname):
    global concated # use global variable
    concated= "" # 초기화

    message = ProtocolMessage(role="user", content=request)
    async for partial in get_bot_response(messages=[message], bot_name=botname, api_key=apikey): 
        #print(partial.text, end='')
        concated = concated + partial.text

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)
   #test_endpoint()