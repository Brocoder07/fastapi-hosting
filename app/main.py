from fastapi import FastAPI
from .routes import search, chat, metadata, users, history # [!code ++]

app = FastAPI(title="Healing Protocols API")

# Include Routers
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(metadata.router) # [!code ++]
app.include_router(users.router)  # [!code ++]
app.include_router(history.router)

@app.get("/")
def home():
    return {"message": "Healing Protocols API is running"}