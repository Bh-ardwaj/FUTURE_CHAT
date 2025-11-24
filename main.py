# # # backend/main.py
# # import json, asyncio
# # from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
# # from fastapi.responses import FileResponse
# # from fastapi.middleware.cors import CORSMiddleware
# # from pathlib import Path

# # from ollama_client import stream_ollama
# # from llama_client import stream_llamacpp
# # from tts import synthesize_text_to_file

# # APP_DIR = Path(__file__).parent
# # UPLOAD_DIR = APP_DIR / "uploads"
# # HIST_DIR = APP_DIR / "history"
# # UPLOAD_DIR.mkdir(exist_ok=True)
# # HIST_DIR.mkdir(exist_ok=True)

# # app = FastAPI()
# # app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# # MODEL_BACKENDS = {
# #     "ollama": {"type": "ollama"},
# #     "llama_cpp": {"type": "llama_cpp", "cmd": ["./main", "-m", "models/ggml-model.bin", "--threads", "4"]}
# # }

# # def save_chat_backup(chat_id: str, messages: list):
# #     (HIST_DIR / f"{chat_id}.json").write_text(json.dumps(messages, indent=2))

# # @app.post('/upload')
# # async def upload_file(file: UploadFile = File(...)):
# #     dest = UPLOAD_DIR / file.filename
# #     with open(dest, 'wb') as f:
# #         content = await file.read()
# #         f.write(content)
# #     return {"status":"ok","filename":file.filename}

# # @app.get('/file/{filename}')
# # async def get_file(filename: str):
# #     f = UPLOAD_DIR / filename
# #     if not f.exists():
# #         raise HTTPException(404, 'file not found')
# #     return FileResponse(str(f))

# # @app.get('/tts')
# # def tts_endpoint(text: str):
# #     wav = synthesize_text_to_file(text)
# #     return FileResponse(wav, media_type='audio/wav')

# # @app.websocket('/chat')
# # async def websocket_chat(ws: WebSocket):
    
# #     await ws.accept()
# #     chat_id = f"chat_{id(ws)}"
# #     history = []
# #     try:
# #         while True:
# #             data = await ws.receive_text()
# #             req = json.loads(data)
# #             if req.get('type') != 'chat':
# #                 await ws.send_text(json.dumps({'type':'error','error':'unsupported message type'}))
# #                 continue

# #             user_msg = req.get('message','')
# #             backend_key = req.get('model','ollama')
# #             model_name = req.get('model_name','')

# #             history.append({"role":"user","content":user_msg})
# #             save_chat_backup(chat_id, history)

# #             await ws.send_text(json.dumps({'type':'start'}))

# #             backend_cfg = MODEL_BACKENDS.get(backend_key, {'type':'ollama'})

# #             if backend_cfg['type'] == 'ollama':
# #                 async for line in stream_ollama(model_name or 'llama', user_msg):
# #                     try:
# #                         parsed = json.loads(line)
# #                         if 'response' in parsed:
# #                             chunk = parsed['response']
# #                         elif 'token' in parsed:
# #                             chunk = parsed['token']
# #                         else:
# #                             chunk = str(parsed)
# #                     except Exception:
# #                         chunk = line
# #                     await ws.send_text(json.dumps({'type':'chunk','content':chunk}))
# #                 await ws.send_text(json.dumps({'type':'end'}))
# #                 history.append({'role':'assistant','content':'(reply saved on client)'})
# #                 save_chat_backup(chat_id, history)

# #             elif backend_cfg['type'] == 'llama_cpp':
# #                 cmd = backend_cfg['cmd']
# #                 async for chunk in stream_llamacpp(cmd, user_msg):
# #                     await ws.send_text(json.dumps({'type':'chunk','content':chunk}))
# #                 await ws.send_text(json.dumps({'type':'end'}))
# #                 history.append({'role':'assistant','content':'(reply saved on client)'})
# #                 save_chat_backup(chat_id, history)
# #             else:
# #                 await ws.send_text(json.dumps({'type':'error','error':'unknown backend type'}))

# #     except Exception:
# #         try:
# #             await ws.close()
# #         except Exception:
# #             pass
# # backend/main.py
# import json, asyncio
# from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pathlib import Path

# from ollama_client import stream_ollama
# from llama_client import stream_llamacpp
# from tts import synthesize_text_to_file

# # ★ NEW: Import permanent memory system
# from memory import save_memory, retrieve_memory

# APP_DIR = Path(__file__).parent
# UPLOAD_DIR = APP_DIR / "uploads"
# HIST_DIR = APP_DIR / "history"
# UPLOAD_DIR.mkdir(exist_ok=True)
# HIST_DIR.mkdir(exist_ok=True)

# app = FastAPI()
# app.add_middleware(CORS_MIDDLEWARE := CORSMiddleware,
#                    allow_origins=["*"],
#                    allow_methods=["*"],
#                    allow_headers=["*"])

# MODEL_BACKENDS = {
#     "ollama": {"type": "ollama"},
#     "llama_cpp": {"type": "llama_cpp", "cmd": ["./main", "-m", "models/ggml-model.bin", "--threads", "4"]}
# }

# def save_chat_backup(chat_id: str, messages: list):
#     (HIST_DIR / f"{chat_id}.json").write_text(json.dumps(messages, indent=2))


# # -------------------- FILE UPLOAD --------------------
# @app.post('/upload')
# async def upload_file(file: UploadFile = File(...)):
#     dest = UPLOAD_DIR / file.filename
#     with open(dest, 'wb') as f:
#         f.write(await file.read())
#     return {"status": "ok", "filename": file.filename}


# @app.get('/file/{filename}')
# async def get_file(filename: str):
#     f = UPLOAD_DIR / filename
#     if not f.exists():
#         raise HTTPException(404, 'file not found')
#     return FileResponse(str(f))


# # -------------------- TTS --------------------
# @app.get('/tts')
# def tts_endpoint(text: str):
#     wav = synthesize_text_to_file(text)
#     return FileResponse(wav, media_type='audio/wav')


# # -------------------- WEBSOCKET CHAT --------------------
# @app.websocket('/chat')
# async def websocket_chat(ws: WebSocket):

#     await ws.accept()
#     chat_id = f"chat_{id(ws)}"
#     history = []

#     try:
#         while True:

#             # Receive message from frontend
#             data = await ws.receive_text()
#             req = json.loads(data)

#             if req.get('type') != 'chat':
#                 await ws.send_text(json.dumps({'type': 'error', 'error': 'unsupported message type'}))
#                 continue

#             user_msg = req.get('message', '')
#             backend_key = req.get('model', 'ollama')
#             model_name = req.get('model_name', 'llama2')

#             # -------------------- MEMORY RETRIEVAL --------------------
#             recalled_memories = retrieve_memory(user_msg)

#             # Build enhanced prompt
#             enhanced_prompt = (
#                 "You are PewdsBot with long-term memory.\n"
#                 "Retrieve relevant facts and stay consistent.\n\n"
#                 "🔮 *Relevant memories from past chats:*\n"
#                 f"{chr(10).join(recalled_memories)}\n\n"
#                 "💬 *Current user message:*\n"
#                 f"{user_msg}\n"
#             )

#             # Save user's message to memory
#             save_memory("user", user_msg)

#             # Save normal chat history
#             history.append({"role": "user", "content": user_msg})
#             save_chat_backup(chat_id, history)

#             await ws.send_text(json.dumps({'type': 'start'}))

#             backend_cfg = MODEL_BACKENDS.get(backend_key, {'type': 'ollama'})

#             # -------------------- OLLAMA --------------------
#             if backend_cfg['type'] == 'ollama':

#                 async for line in stream_ollama(model_name, enhanced_prompt):

#                     # parse each token from Ollama
#                     try:
#                         parsed = json.loads(line)
#                         if 'response' in parsed:
#                             chunk = parsed['response']
#                         elif 'token' in parsed:
#                             chunk = parsed['token']
#                         else:
#                             chunk = str(parsed)
#                     except Exception:
#                         chunk = line

#                     await ws.send_text(json.dumps({'type': 'chunk', 'content': chunk}))

#                 await ws.send_text(json.dumps({'type': 'end'}))

#                 # save assistant reply into memory + backup
#                 save_memory("assistant", "(assistant replied)")
#                 history.append({'role': 'assistant', 'content': '(reply saved on client)'})
#                 save_chat_backup(chat_id, history)

#             # -------------------- LLAMA-CPP --------------------
#             elif backend_cfg['type'] == 'llama_cpp':
#                 cmd = backend_cfg['cmd']

#                 async for chunk in stream_llamacpp(cmd, enhanced_prompt):
#                     await ws.send_text(json.dumps({'type': 'chunk', 'content': chunk}))

#                 await ws.send_text(json.dumps({'type': 'end'}))

#                 save_memory("assistant", "(assistant replied)")
#                 history.append({'role': 'assistant', 'content': '(reply saved on client)'})
#                 save_chat_backup(chat_id, history)

#             else:
#                 await ws.send_text(json.dumps({'type': 'error', 'error': 'unknown backend type'}))

#     except Exception:
#         try:
#             await ws.close()
#         except Exception:
#             pass
# backend/main.py
import json
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from ollama_client import stream_ollama
from llama_client import stream_llamacpp
from tts import synthesize_text_to_file

# 🔁 Long-term memory
from memory import save_memory, retrieve_memory

APP_DIR = Path(__file__).parent
UPLOAD_DIR = APP_DIR / "uploads"
HIST_DIR = APP_DIR / "history"

UPLOAD_DIR.mkdir(exist_ok=True)
HIST_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# You can still pick backends from the frontend
MODEL_BACKENDS = {
    "ollama": {"type": "ollama"},
    "llama_cpp": {
        "type": "llama_cpp",
        "cmd": ["./main", "-m", "models/ggml-model.bin", "--threads", "4"],
    },
}


def save_chat_backup(chat_id: str, messages: list):
    (HIST_DIR / f"{chat_id}.json").write_text(json.dumps(messages, indent=2))


# -------------------- FILE UPLOAD --------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        f.write(await file.read())
    return {"status": "ok", "filename": file.filename}


@app.get("/file/{filename}")
async def get_file(filename: str):
    f = UPLOAD_DIR / filename
    if not f.exists():
        raise HTTPException(404, "file not found")
    return FileResponse(str(f))


# -------------------- TTS --------------------
@app.get("/tts")
def tts_endpoint(text: str):
    wav = synthesize_text_to_file(text)
    return FileResponse(wav, media_type="audio/wav")


# -------------------- WEBSOCKET CHAT --------------------
@app.websocket("/chat")
async def websocket_chat(ws: WebSocket):

    await ws.accept()
    chat_id = f"chat_{id(ws)}"
    history = []

    try:
        while True:
            # Receive message from frontend
            data = await ws.receive_text()
            req = json.loads(data)

            if req.get("type") != "chat":
                await ws.send_text(
                    json.dumps(
                        {"type": "error", "error": "unsupported message type"}
                    )
                )
                continue

            user_msg = req.get("message", "")
            backend_key = req.get("model", "ollama")
            # Example: "tinyllama", "tinydolphin", etc. from frontend
            model_name = req.get("model_name", "tinyllama")

            # -------------------- MEMORY RETRIEVAL --------------------
            recalled_memories = retrieve_memory(user_msg)  # list[str]

            mem_block = (
                "\n".join(recalled_memories) if recalled_memories else "None yet."
            )

            # Build enhanced prompt for the local model
            enhanced_prompt = (
                "You are FutureChat, a helpful AI assistant with long-term memory.\n"
                "Use the past memories only if they are relevant. Stay consistent with what the user has told you earlier.\n\n"
                "🔮 Relevant memories from past chats:\n"
                f"{mem_block}\n\n"
                "💬 Current user message:\n"
                f"{user_msg}\n"
            )

            # Save normal chat history (backup on disk)
            history.append({"role": "user", "content": user_msg})
            save_chat_backup(chat_id, history)

            # Notify frontend that streaming is starting
            await ws.send_text(json.dumps({"type": "start"}))

            backend_cfg = MODEL_BACKENDS.get(backend_key, {"type": "ollama"})

            # -------------------- OLLAMA BACKEND --------------------
            if backend_cfg["type"] == "ollama":
                full_reply = ""

                async for line in stream_ollama(model_name, enhanced_prompt):
                    # parse each token / line from Ollama
                    try:
                        parsed = json.loads(line)
                        if "response" in parsed:
                            chunk = parsed["response"]
                        elif "token" in parsed:
                            chunk = parsed["token"]
                        else:
                            chunk = str(parsed)
                    except Exception:
                        chunk = line

                    full_reply += chunk
                    await ws.send_text(
                        json.dumps({"type": "chunk", "content": chunk})
                    )

                await ws.send_text(json.dumps({"type": "end"}))

                # save assistant reply into long-term memory + backup
                save_memory(chat_id, user_msg, full_reply)
                history.append(
                    {"role": "assistant", "content": "(reply saved on client)"}
                )
                save_chat_backup(chat_id, history)

            # -------------------- LLAMA-CPP BACKEND --------------------
            elif backend_cfg["type"] == "llama_cpp":
                cmd = backend_cfg["cmd"]
                full_reply = ""

                async for chunk in stream_llamacpp(cmd, enhanced_prompt):
                    full_reply += chunk
                    await ws.send_text(
                        json.dumps({"type": "chunk", "content": chunk})
                    )

                await ws.send_text(json.dumps({"type": "end"}))

                save_memory(chat_id, user_msg, full_reply)
                history.append(
                    {"role": "assistant", "content": "(reply saved on client)"}
                )
                save_chat_backup(chat_id, history)

            else:
                await ws.send_text(
                    json.dumps({"type": "error", "error": "unknown backend type"})
                )

    except Exception as e:
        print(f"[websocket_chat] Error: {e}")
        try:
            await ws.close()
        except Exception:
            pass
