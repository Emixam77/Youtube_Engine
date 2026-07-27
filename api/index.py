import os
import sys
import json
import urllib.request
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Antigravity Creative Studio Cloud API")

# Load Notion Token from environment or config fallback
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    try:
        config_path = "/Users/Emixam/.gemini/antigravity/mcp_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
            NOTION_TOKEN = config.get("mcpServers", {}).get("notion-mcp-server", {}).get("env", {}).get("NOTION_TOKEN")
    except Exception:
        pass

# Default Database IDs
DATABASES = {
    "youtube": "3a6362ee-28c7-80ef-a2e9-f9b9450ed4c3",
    "marketing": "3a7362ee-28c7-81de-a0c8-c67eb11f7106",
    "creation": "3a7362ee-28c7-81f3-889d-d8e441305b3b"
}

# Notion API Helper
def query_notion(endpoint: str, method: str = "GET", data: Dict = None):
    if not NOTION_TOKEN:
        raise HTTPException(status_code=500, detail="NOTION_TOKEN not configured")
    
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Pydantic Schemas
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class PageRequest(BaseModel):
    database_type: str
    title: str
    properties: Dict[str, Any]

class ChannelModel(BaseModel):
    name: str

# API Endpoints
@app.get("/api/databases/{db_type}")
def get_database(db_type: str):
    db_id = DATABASES.get(db_type)
    if not db_id:
        raise HTTPException(status_code=404, detail="Database type not found")
    return query_notion(f"databases/{db_id}")

@app.get("/api/databases/{db_type}/pages")
def get_database_pages(db_type: str):
    db_id = DATABASES.get(db_type)
    if not db_id:
        raise HTTPException(status_code=404, detail="Database type not found")
    res = query_notion(f"databases/{db_id}/query", method="POST")
    return res.get("results", [])

@app.post("/api/pages")
def create_page(req: PageRequest):
    db_id = DATABASES.get(req.database_type)
    if not db_id:
        raise HTTPException(status_code=404, detail="Database type not found")
    
    notion_payload = {
        "parent": {"database_id": db_id, "type": "database_id"},
        "properties": req.properties
    }
    return query_notion("pages", method="POST", data=notion_payload)

@app.get("/api/styles")
def get_styles_and_animations():
    return {
        "styles": [
            {"id": "01", "name": "Documentary Collage Noir", "hex": "#0D0D0D", "accent": "Acid Yellow & Blood Red", "desc": "Investigation, hidden systems, dark grain"},
            {"id": "02", "name": "Front Page Manifesto", "hex": "#E8DEC8", "accent": "Red alone", "desc": "Vintage newspaper, action, bold headlines"},
            {"id": "03", "name": "VOX Editorial Lab", "hex": "#F2EDDF", "accent": "Yellow Or", "desc": "Analytical, clean grid with annotations"},
            {"id": "04", "name": "Geopolitical Manifesto", "hex": "#E8DFCb", "accent": "Red alone", "desc": "No typo, pure visual assembly, cracked parchment"},
            {"id": "05", "name": "Tokyo Minimal", "hex": "#FFFFFF", "accent": "Red sun", "desc": "Minimalist, zen, wide empty space"},
            {"id": "06", "name": "Bauhaus Konstrukt", "hex": "#F5F0E0", "accent": "Red & Black", "desc": "Swiss grid, strong shapes (diamonds, triangles)"},
            {"id": "07", "name": "Retro TV Strip", "hex": "#EAE0CC", "accent": "RGB 3-stripes", "desc": "1970s TV test bands, warmth, optimism"},
            {"id": "08", "name": "Pop Prism 60s", "hex": "#E8D8BC", "accent": "Vibrant colors", "desc": "Translucent gel filters, multi-angle triptych"},
            {"id": "09", "name": "Typo Explosion Pop", "hex": "#FFFFFF", "accent": "Orange & Red", "desc": "Loud typography fragments, halftone dots, high energy"},
            {"id": "10", "name": "Premium Paper Stop-Motion", "hex": "#D2B48C", "accent": "Custom/Kraft", "desc": "3D stacked cardstock sheets, laser-cut edges, locked camera, paper ASMR"}
        ],
        "cameras": [
            {"name": "🚀 Le Voleur", "desc": "Flies low between diorama layers at ground level"},
            {"name": "🎯 Le Rack Focus", "desc": "Shifts focus from background to foreground sharply"},
            {"name": "🔄 Le Chasseur", "desc": "Chases a moving object like a circular rail camera"},
            {"name": "🌊 Le Plongeur", "desc": "Sinks vertically below a surface to reveal hidden elements"},
            {"name": "♟️ L'Orbiteur", "desc": "Orbits 90 degrees around a central element"}
        ]
    }

@app.post("/api/chat")
def chat_with_gemini(req: ChatRequest):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    system_instruction = (
        "You are the 'Gemini Video Director' for Antigravity Media Engine. Your role is to help the user structure their video ideas. "
        "Interact in French, friendly and conversationally. Guide them through choosing the best style from our 10 styles (Tokyo Minimal, "
        "Documentary Collage Noir, Premium Paper Stop-Motion, etc.) and camera motions. Once they align, draft the BROLL scene list."
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    
    contents = []
    for turn in req.history:
        contents.append({
            "role": "user" if turn["role"] == "user" else "model",
            "parts": [{"text": turn["text"]}]
        })
    contents.append({
        "role": "user",
        "parts": [{"text": f"System Guidelines: {system_instruction}\nUser Message: {req.message}"}]
    })
    
    payload = {"contents": contents}
    req_body = json.dumps(payload).encode("utf-8")
    http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(http_req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Reference Channels Storage File
CHANNELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_channels.json")

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        return ["Vox", "Johnny Harris", "MagnatesMedia"]
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_channels(channels):
    try:
        with open(CHANNELS_FILE, "w") as f:
            json.dump(channels, f, indent=2)
    except Exception:
        pass

@app.get("/api/reference-channels")
def get_reference_channels():
    return load_channels()

@app.post("/api/reference-channels")
def add_reference_channel(channel: ChannelModel):
    channels = load_channels()
    if channel.name and channel.name not in channels:
        channels.append(channel.name)
        save_channels(channels)
    return channels

@app.delete("/api/reference-channels/{name}")
def delete_reference_channel(name: str):
    channels = load_channels()
    decoded_name = urllib.parse.unquote(name)
    if decoded_name in channels:
        channels.remove(decoded_name)
        save_channels(channels)
    elif name in channels:
        channels.remove(name)
        save_channels(channels)
    return channels

# Mount static files only if running locally (not on Vercel serverless)
if not os.getenv("VERCEL"):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
