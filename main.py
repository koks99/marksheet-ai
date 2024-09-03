import io
import pytesseract
import json

from bson import ObjectId
from PIL import Image
from fastapi import UploadFile
from fastapi import FastAPI, Request, status, Form, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from starlette.status import HTTP_302_FOUND
from starlette.middleware.sessions import SessionMiddleware

from utils.database import students_col, users_col
from utils.util import verify_password, get_password_hash, get_data_from_extracted_text, get_search_results

app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Configuring Middleware for session awareness
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Mount the static directory to serve static files (like CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"username": request.session.get("username"), "request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"username": request.session.get("username"), "request": request})

@app.post('/parse_mark')
async def parse_mark(file: UploadFile, request: Request):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image, config = "--psm 6")
        parsed_data = get_data_from_extracted_text(text)
        parsed_data["owner"] = request.session.get("username")
        data_json = json.dumps(parsed_data)
        return templates.TemplateResponse("display_mark.html", {"data": parsed_data, "username": parsed_data["owner"],
                                                            "request": request, "data_json": data_json})
    except Exception as e:
        print(repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='There was an error uploading the file',
        )
    finally:
        await file.close()

@app.post('/persist_mark')
async def persist_mark(request: Request, extracted_data: str = Form(...), action: str = Form(...)):
    data = json.loads(extracted_data)
    data["visibility"] = "public"
    if action == "true":
        data["visibility"] = "private"
    existing_doc = students_col.find_one({"roll_no": data["roll_no"], "name": data["name"],
                                          "user": request.session.get("username")})
    if not existing_doc:
        students_col.insert_one(data)
    else:
        for course in existing_doc['courses']:
            if not any(d['course'] == course['course'] for d in data['courses']):
                data['courses'].append(course)
        students_col.update({"_id": ObjectId(existing_doc["_id"])}, data)
    return RedirectResponse("/", status_code=HTTP_302_FOUND)

@app.get('/search')
async def search(request: Request, query: Optional[str] = None):
    query_regex = {"$regex": query.strip(), "$options": "i"}

    public_query = {"$and": [
        {"$or": [{"roll_no": query_regex},{"name": query_regex}]},
        {"visibility": "public"}
        ]
    }
    results = get_search_results(public_query, students_col)

    if request.session.get("username"):
        private_query = {"$and": [
            {"$or": [{"roll_no": query_regex}, {"name": query_regex}]},
            {"$and": [{"owner": request.session.get("username")}, {"visibility": "private"}]}
        ]
        }
        results.extend(get_search_results(private_query, students_col))

    return templates.TemplateResponse("search.html", {"data": results, "username": request.session.get("username"),
                                                        "request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "username": request.session.get("username")})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "username": request.session.get("username")})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if users_col.find_one({"user": username}):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken"})
    hashed_password = get_password_hash(password)
    users_col.insert_one({"user": username, "hashed_password": hashed_password})
    return RedirectResponse("/", status_code=HTTP_302_FOUND)

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_data = users_col.find_one({"user": username})
    if user_data["hashed_password"] and verify_password(password, user_data["hashed_password"]):
        request.session["username"] = username
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=HTTP_302_FOUND)
