from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from tools.chat_assistant_service_request import chat_assistant_service_request
from models.chat_assistant_service import ChatAssistantServiceRequest

app = FastAPI(title="Cloud Meter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/v1")


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.post("/chat")
async def chat_endpoint(request: Request):
    print(">>> request:", request)
    body = await request.json()
    print(">>> body:", body)
    # Parse into your model
    chat_data = ChatAssistantServiceRequest(**body["chat_assistant_data"])

    # ✅ Await the async function
    try:
        response = await chat_assistant_service_request(chat_data)
    except Exception as e:
        return {"error": str(e), "data": body}
    return {"response": response.model_dump(), "data": body}


app.include_router(router)
