from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from io import StringIO
import os
import contextlib
import subprocess

app = FastAPI(
    title="PyAPI",
    description="API to execute python code",
    version="0.0.1",
)

class CodeExecutionRequest(BaseModel):
    code: str
    folder: str

ROOT_FOLDER = os.getcwd() + '/tmp'
os.chdir(ROOT_FOLDER)

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


@app.get("/")
async def root() -> dict:
    '''Root endpoint; confirm the app is up and running'''
    return {"message": "Hello World"}


@app.post("/execute/")
async def execute_code(req: CodeExecutionRequest) -> dict:
    '''Exceute arbitrary python code from a string input and return the result'''
    try:
        # with stdoutIO() as s:
        if not os.path.exists(ROOT_FOLDER + '/' + req.folder):
            mkdir_cmd = f"mkdir -p {ROOT_FOLDER + '/' + req.folder}"
            os.system(mkdir_cmd)
        os.chdir(ROOT_FOLDER + '/' + req.folder)

        # Run the code in a separate subprocess
        process = subprocess.Popen(
            ['python', '-c', req.code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Error: {stderr.decode()}")

        return {"result": stdout.decode()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)