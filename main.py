import logging

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

logging.basicConfig(
    format="%(asctime)s - %(levelname)s:%(name)s:%(message)s",
    level=logging.INFO,
)

app = FastAPI()

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


@app.get("/")
async def get():
    return HTMLResponse(html)

ws_list = list()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_list.append(websocket)
    while True:
        data = await websocket.receive_text()
        logging.info(f"Received {data}")
        for ws in ws_list:
            message = f"{websocket} sent: {data}"
            await ws.send_text(message)
            logging.info(f"Sent {data} from {websocket} {ws}")


if __name__ == '__main__':
    root_logger = logging.root
    for uv_logger_name in uvicorn.config.LOGGING_CONFIG.get('loggers').keys():
        uv_logger = logging.getLogger(uv_logger_name)
        uv_logger.parent = root_logger
    uvicorn.run(app)
