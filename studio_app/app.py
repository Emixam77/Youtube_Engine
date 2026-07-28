import os
import sys
import json
import urllib.request
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any

# Ensure required libraries are installed
try:
    import uvicorn
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic"])
    import uvicorn

app = FastAPI(title="Antigravity Creative Studio API")

# Load Notion Token from config if not in environment
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
    database_type: str  # youtube, marketing, creation
    title: str
    properties: Dict[str, Any]

class ValidateRequest(BaseModel):
    database_type: str
    history: List[Dict[str, str]]

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
    # Return our 9 styles and 5 camera archetypes
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

def get_env_keys():
    keys = {
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    }
    # Fallback to reading LanderGen's .env if local variables are not set
    landergen_env = "/Users/Emixam/Documents/Antigravity/LanderGen/.env"
    if os.path.exists(landergen_env):
        try:
            with open(landergen_env, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        parts = line.split("=", 1)
                        key = parts[0].strip()
                        val = parts[1].strip().strip('"').strip("'")
                        if key in keys and not keys[key]:
                            keys[key] = val
        except Exception:
            pass
            
    # Notion fallback for Notion token and Gemini
    try:
        config_path = "/Users/Emixam/.gemini/antigravity/mcp_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                if not keys["GEMINI_API_KEY"]:
                    keys["GEMINI_API_KEY"] = config.get("mcpServers", {}).get("notion-mcp-server", {}).get("env", {}).get("GEMINI_API_KEY")
    except Exception:
        pass
    return keys

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest):
    keys = get_env_keys()
    
    system_instruction = (
        "You are the 'Creative Studio Director' (Claude 3.5 Sonnet) for Antigravity Media Engine. Your role is to help the user structure their video ideas. "
        "Interact in French, friendly and conversationally. Guide them through choosing the best style from our 10 styles (Tokyo Minimal, "
        "Documentary Collage Noir, Premium Paper Stop-Motion, etc.) and camera motions. Once they align, draft the BROLL scene list."
    )
    
    # 1. Prioritize OpenRouter to call Claude 3.5 Sonnet
    if keys["OPENROUTER_API_KEY"]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {keys['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Antigravity Creative Studio"
        }
        
        messages = [{"role": "system", "content": system_instruction}]
        for turn in req.history:
            messages.append({
                "role": "user" if turn["role"] == "user" else "assistant",
                "content": turn["text"]
            })
        messages.append({"role": "user", "content": req.message})
        
        payload = {
            "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku"),
            "messages": messages
        }
        
        req_body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(http_req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                text = res_data["choices"][0]["message"]["content"]
                return {"reply": text}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OpenRouter Claude error: {str(e)}")

    # 2. Support OpenAI API Key
    elif keys["OPENAI_API_KEY"]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {keys['OPENAI_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": system_instruction}]
        for turn in req.history:
            messages.append({
                "role": "user" if turn["role"] == "user" else "assistant",
                "content": turn["text"]
            })
        messages.append({"role": "user", "content": req.message})
        
        # If user points to a custom gateway mapping to Claude, it'll work,
        # otherwise standard OpenAI maps to gpt-4o as default fallback.
        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "messages": messages
        }
        
        req_body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(http_req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                text = res_data["choices"][0]["message"]["content"]
                return {"reply": text}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OpenAI error: {str(e)}")

    # 3. Fallback to Gemini
    elif keys["GEMINI_API_KEY"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={keys['GEMINI_API_KEY']}"
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
            
    else:
        raise HTTPException(status_code=500, detail="Aucune clé d'API valide trouvée (OpenRouter, OpenAI ou Gemini)")

@app.post("/api/chat/validate")
def validate_chat_to_notion(req: ValidateRequest):
    keys = get_env_keys()
    
    # 1. Prepare chat conversation transcript for the AI
    transcript = ""
    for turn in req.history:
        role = "Utilisateur" if turn["role"] == "user" else "Assistant"
        transcript += f"{role}: {turn['text']}\n"
        
    system_instruction = (
        "Tu es un assistant de base de données. Analyse la conversation suivante et extrait les paramètres "
        "nécessaires pour créer un projet vidéo Notion. Tu dois renvoyer STRICTEMENT un objet JSON valide "
        "avec les clés suivantes :\n"
        "- title : Le titre du projet (court et créatif, ex: '🩷 The Curse')\n"
        "- format : Le format exact parmi : '📱 Short 9:16' ou '🖥️ Vidéo HD 16:9'\n"
        "- style : Le style visuel ou la DA identifiée (ex: 'Style 10 — Premium Paper Stop-Motion')\n"
        "- camera : L'archétype de caméra parmi : '🚀 Le Voleur', '🎯 Le Rack Focus', '🔄 Le Chasseur', '🌊 Le Plongeur', '♟️ L'Orbiteur'\n"
        "- notes : Un résumé structuré du script et des prompts d'images associés.\n"
        "Ne renvoie aucun autre texte que le JSON."
    )
    
    ai_reply = None
    if keys["OPENROUTER_API_KEY"]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {keys['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Antigravity Creative Studio"
        }
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Voici la conversation :\n\n{transcript}"}
            ],
            "response_format": {"type": "json_object"}
        }
        req_body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(http_req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                ai_reply = res_data["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OpenRouter extraction error: {str(e)}")
            
    elif keys["OPENAI_API_KEY"]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {keys['OPENAI_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Voici la conversation :\n\n{transcript}"}
            ],
            "response_format": {"type": "json_object"}
        }
        req_body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(http_req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                ai_reply = res_data["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OpenAI extraction error: {str(e)}")
            
    elif keys["GEMINI_API_KEY"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={keys['GEMINI_API_KEY']}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_instruction}\n\nVoici la conversation :\n\n{transcript}"}]
            }]
        }
        req_body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(http_req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gemini extraction error: {str(e)}")
            
    if not ai_reply:
        raise HTTPException(status_code=500, detail="Could not extract data from conversation")
        
    ai_reply = ai_reply.strip()
    if ai_reply.startswith("```"):
        lines = ai_reply.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        ai_reply = "\n".join(lines).strip()
        
    try:
        extracted = json.loads(ai_reply)
    except Exception:
        raise HTTPException(status_code=500, detail=f"Invalid JSON extracted by AI: {ai_reply}")
        
    db_id = DATABASES.get(req.database_type)
    if not db_id:
        raise HTTPException(status_code=404, detail="Database type not found")
        
    import datetime
    current_date = datetime.date.today().isoformat()
    
    properties = {}
    if req.database_type == "creation":
        properties = {
            "Titre du Projet": {"title": [{"text": {"content": extracted.get("title", "Projet Création Libre")}}]},
            "Format": {"select": {"name": extracted.get("format", "📱 Short 9:16")}},
            "Statut": {"select": {"name": "🔵 En cours"}},
            "Style Visuel / DA": {"rich_text": [{"text": {"content": extracted.get("style", "Style 10 — Premium Paper Stop-Motion")}}]},
            "Archétype Caméra": {"select": {"name": extracted.get("camera", "♟️ L'Orbiteur")}},
            "Mode d'Entrée": {"select": {"name": "✍️ Script Brut"}},
            "Notes": {"rich_text": [{"text": {"content": extracted.get("notes", "")}}]},
            "Moteur IA": {"multi_select": [{"name": "Google Flow / OmniFlash"}]},
            "Date de Création": {"date": {"start": current_date}}
        }
    elif req.database_type == "youtube":
        properties = {
            "Titre du Post": {"title": [{"text": {"content": extracted.get("title", "Post YouTube")}}]},
            "v Plateforme": {"select": {"name": "Youtube Short" if "Short" in extracted.get("format", "") else "Youtube"}},
            "Statut": {"select": {"name": "🟠 En rédaction"}},
            "Copywriting": {"rich_text": [{"text": {"content": extracted.get("notes", "")}}]}
        }
    elif req.database_type == "marketing":
        properties = {
            "Titre de la Campagne": {"title": [{"text": {"content": extracted.get("title", "Campagne Marketing")}}]},
            "Plateforme Cible": {"select": {"name": "YouTube" if "Short" in extracted.get("format", "") else "Instagram"}},
            "Objectif": {"select": {"name": "💬 Engagement"}},
            "Branche": {"select": {"name": "📱 Social Media"}},
            "Statut": {"select": {"name": "🔵 En cours"}},
            "Copy / Brief": {"rich_text": [{"text": {"content": extracted.get("notes", "")}}]},
            "Notes": {"rich_text": [{"text": {"content": extracted.get("style", "")}}]}
        }
        
    notion_payload = {
        "parent": {"database_id": db_id, "type": "database_id"},
        "properties": properties
    }
    
    return query_notion("pages", method="POST", data=notion_payload)

# Reference Channels Storage File
CHANNELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_channels.json")

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        # Default starting reference channels
        return ["Vox", "Johnny Harris", "MagnatesMedia"]
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f, indent=2)

class ChannelModel(BaseModel):
    name: str

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
    # Decode name just in case it is URL encoded
    decoded_name = urllib.parse.unquote(name)
    if decoded_name in channels:
        channels.remove(decoded_name)
        save_channels(channels)
    elif name in channels:
        channels.remove(name)
        save_channels(channels)
    return channels

# Mount static files (will be index.html, style.css, app.js)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
