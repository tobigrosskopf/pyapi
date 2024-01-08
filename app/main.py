from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from io import StringIO
import contextlib

app = FastAPI(
    title="PyAPI",
    description="API to execute python code",
    version="0.0.1",
)

class CodeExecutionRequest(BaseModel):
    code: str


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/execute/")
async def execute_code(req: CodeExecutionRequest):
    code = req.code
    try:
        with stdoutIO() as s:
            exec(code)
        return {"result": s.getvalue()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)