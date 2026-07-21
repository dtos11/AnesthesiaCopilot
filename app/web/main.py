from datetime import date
from functools import lru_cache
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.web.backend import WebBackend


WEB_ROOT = Path(__file__).resolve().parent

app = FastAPI(title="AnesthesiaCopilot")
app.mount(
    "/static",
    StaticFiles(directory=WEB_ROOT / "static"),
    name="static",
)
templates = Jinja2Templates(directory=WEB_ROOT / "templates")


@lru_cache(maxsize=1)
def get_backend() -> WebBackend:
    return WebBackend()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
    )


@app.get("/estado", response_class=HTMLResponse)
def state_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="state_form.html",
        context={"today": date.today().isoformat()},
    )


@app.post("/estado", response_class=HTMLResponse)
def state_result(request: Request, day: date = Form(...)):
    view = get_backend().department_state_for(day)
    return templates.TemplateResponse(
        request=request,
        name="state_result.html",
        context={"view": view},
    )


@app.get("/validar", response_class=HTMLResponse)
def validation_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="validation_form.html",
    )


@app.post("/validar", response_class=HTMLResponse)
def validation_result(
    request: Request,
    workbook: UploadFile = File(...),
):
    filename = Path(workbook.filename or "").name

    if not filename.casefold().endswith(".xlsx"):
        return templates.TemplateResponse(
            request=request,
            name="validation_form.html",
            context={"error": "Seleccione un archivo Excel .xlsx."},
            status_code=400,
        )

    with TemporaryDirectory() as temporary_directory:
        workbook_path = Path(temporary_directory) / filename

        with workbook_path.open("wb") as destination:
            shutil.copyfileobj(workbook.file, destination)

        view = get_backend().validate_workbook(str(workbook_path))

    return templates.TemplateResponse(
        request=request,
        name="validation_result.html",
        context={"view": view},
    )
