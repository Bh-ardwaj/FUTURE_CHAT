// frontend/app.js - WebSocket chat, TTS, uploads, voice, history
const WS_URL = "ws://localhost:8000/chat";
let ws;
let streamingDiv = null;
let chats = {};
let activeChat = "chat-1";

function connectWS() {
    ws = new WebSocket(WS_URL);
    ws.onopen = () => console.log("WS connected");
    ws.onmessage = (ev) => {
        try {
            const msg = JSON.parse(ev.data);
            if (msg.type === "start") {
                document.getElementById("typing").classList.remove("hidden");
                streamingDiv = addBubble("assistant", "");
                return;
            }
            if (msg.type === "chunk") {
                if (streamingDiv) {
                    streamingDiv.innerText += msg.content;
                    scrollChat();
                }
                return;
            }
            if (msg.type === "end") {
                document.getElementById("typing").classList.add("hidden");
                if (streamingDiv) {
                    chats[activeChat].push({role:"assistant", content: streamingDiv.innerText});
                    saveChats();
                }
                streamingDiv = null;
                return;
            }
        } catch (e) {
            console.error("ws msg parse error", e);
        }
    };
    ws.onclose = () => console.log("WS closed");
    ws.onerror = (e) => console.error("WS error", e);
}

function addBubble(role, text) {
    const d = document.createElement("div");
    d.className = 'message ' + (role === 'user' ? 'bubble-user' : 'bubble-ai');
    d.innerText = text;
    document.getElementById("chat").appendChild(d);
    scrollChat();
    return d;
}

function scrollChat() {
    const c = document.getElementById("chat");
    c.scrollTop = c.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("msg");
    const text = input.value.trim();
    if (!text) return;
    addBubble("user", text);
    chats[activeChat].push({role:"user", content:text});
    saveChats();
    input.value = "";
    const model = document.getElementById("model").value;
    const modelName = document.getElementById("modelName").value;
    ws.send(JSON.stringify({type:"chat", model: model, model_name: modelName, message: text}));
}

function newChat() {
    const id = "chat-" + (Object.keys(chats).length + 1);
    chats[id] = [];
    activeChat = id;
    renderChatList();
    loadChat(id);
    saveChats();
}

function renderChatList() {
    const el = document.getElementById("chatList");
    el.innerHTML = "";
    for (const id of Object.keys(chats)) {
        const div = document.createElement("div");
        div.className = "chat-list-item";
        div.innerText = id;
        div.onclick = () => loadChat(id);
        el.appendChild(div);
    }
}

function loadChat(id) {
    activeChat = id;
    const c = document.getElementById("chat");
    c.innerHTML = "";
    for (const m of chats[id]) {
        addBubble(m.role === "user" ? "user" : "assistant", m.content);
    }
}

function saveChats() {
    localStorage.setItem("pewdsChats", JSON.stringify(chats));
}

function loadChats() {
    const s = localStorage.getItem("pewdsChats");
    if (s) chats = JSON.parse(s);
    else { chats = {"chat-1": []}; saveChats(); }
    renderChatList();
    if (!activeChat || !chats[activeChat]) activeChat = Object.keys(chats)[0];
    loadChat(activeChat);
}

// upload
async function handleUpload() {
    const f = document.getElementById("fileInput").files[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    const res = await fetch("http://localhost:8000/upload", {method:"POST", body: fd});
    const data = await res.json();
    addBubble("user", `[Uploaded file: ${data.filename}]`);
    chats[activeChat].push({role:"user", content:`[Uploaded file: ${data.filename}]`});
    saveChats();
}

// voice recognition
function startVoice() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        alert("Speech recognition not supported");
        return;
    }
    const recog = new Recognition();
    recog.lang = "en-US";
    recog.onresult = (e) => {
        document.getElementById("msg").value = e.results[0][0].transcript;
    };
    recog.onerror = (e) => console.log("recog err", e);
    recog.start();
}

// play last assistant message via server TTS
async function playLastTTS() {
    const msgs = chats[activeChat];
    const last = [...msgs].reverse().find(m => m.role === "assistant");
    if (!last) return alert("No assistant message");
    const res = await fetch("http://localhost:8000/tts?text=" + encodeURIComponent(last.content));
    if (!res.ok) return alert("TTS failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = new Audio(url);
    a.play();
}

window.addEventListener("load", () => {
    connectWS();
    loadChats();
    document.getElementById("msg").addEventListener("keydown", (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
});
