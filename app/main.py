import uuid
import fastapi
from models.timer import SetTimerRequest, SetTimerResponse

app = fastapi.FastAPI()

@app.post("/timer", response_model=SetTimerResponse)
async def set_timer(request: SetTimerRequest):
    timer_id = str(uuid.uuid4())
    