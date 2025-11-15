from fastapi import FastAPI, WebSocket, HTTPException, Body
import subprocess, asyncio

app = FastAPI()

CONTAINER_NAME = "ubuntu"  # nom du conteneur lancé avec docker run -dit --name ubuntu22 ubuntu:22.04 bash

# ------------------------
# Route HTTP simple
# ------------------------
@app.post("/terminal")
def terminal(command: str = Body(...)):
    try:
        cmd = ["docker", "exec", CONTAINER_NAME, "bash", "-c", command]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = (result.stdout or "") + (result.stderr or "")
        status = "ok" if result.returncode == 0 else "error"
        return {"command": command, "status": status, "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"terminal_error: {str(e)}")

# ------------------------
# Route WebSocket simple
# ------------------------
@app.websocket("/terminal/ws")
async def websocket_terminal(ws: WebSocket):
    await ws.accept()
    await ws.send_text(f"Bienvenue dans le terminal Ubuntu 🚀 (conteneur: {CONTAINER_NAME})\n")
    try:
        while True:
            data = await ws.receive_text()
            cmd = ["docker", "exec", CONTAINER_NAME, "bash", "-c", data]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            output = (stdout.decode() + stderr.decode()).strip()
            await ws.send_text(output + "\n")
    except Exception as e:
        await ws.send_text(f"Erreur: {str(e)}")
        await ws.close()
