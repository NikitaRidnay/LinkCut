from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import validators   # type: ignore

app = FastAPI()

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="templates")

links = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten/")
async def shorten_link(url: str = Form(...), custom_id: str = Form(None)):
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    if not custom_id:
        custom_id = str(uuid4())[:6]  

    if custom_id in links:
        raise HTTPException(status_code=400, detail="Custom ID is already taken")

    links[custom_id] = url
    shortened_url = f"http://127.0.0.1:8000/{custom_id}"
    return JSONResponse(content={"shortened_url": shortened_url})

@app.get("/{shortened_id}")
async def redirect_link(shortened_id: str):
    url = links.get(shortened_id)
    if url is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
