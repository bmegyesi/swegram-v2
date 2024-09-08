from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import Body
from typing import Dict, Any


app = FastAPI()
connected_clients = []


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/test")
async def get():
    return HTMLResponse(html)


# Fake user data (replace this with your authentication logic)
fake_users = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"}
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # 接收来自客户端的消息
            data = await websocket.receive_text()
            # 广播消息给所有已连接的客户端
            for client in connected_clients:
                await client.send_text(data)
    finally:
        # 断开连接时移除客户端
        connected_clients.remove(websocket)


# WebSocket endpoint for user login
@app.websocket("/login")
async def login(websocket: WebSocket, username: str, password: str):
    if username in fake_users and fake_users[username]["password"] == password:
        await websocket.accept()
        connected_clients[username] = websocket
        await websocket.send_text(f"Welcome, {username}!")
    else:

        await websocket.close(code=1008)

@app.post("/login")
async def post_login(request: Request, data: Dict[str, Any] = Body(...)) -> None:
    return