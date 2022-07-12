import fastapi
import socket

app = fastapi.FastAPI()


@app.get("/greet/{name}")
def greet(name: str):
    return {
        "data": {
            "message": f"Hello {name}!"
        },
        "info": {
            "hostname": socket.gethostname()
        }
    }
