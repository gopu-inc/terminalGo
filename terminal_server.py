from fastapi import FastAPI, WebSocket, HTTPException, Body
import subprocess, asyncio

app = FastAPI()

# ------------------------
# Route HTTP simple
# ------------------------
@app.post("/terminal")
def terminal(command: str = Body(...)):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = (result.stdout or "") + (result.stderr or "")
        status = "ok" if result.returncode == 0 else "error"
        return {
            "command": command,
            "status": status,
            "output": output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"terminal_error: {str(e)}")

# ------------------------
# Route WebSocket interactive
# ------------------------
@app.websocket("/terminal/ws")
async def websocket_terminal(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Bienvenue dans le terminal Render 🚀\n")
    try:
        while True:
            cmd = await ws.receive_text()
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            output = (stdout.decode() + stderr.decode()).strip()
            await ws.send_text(output + "\n")
    except Exception as e:
        await ws.send_text(f"Erreur: {str(e)}")
        await ws.close()
