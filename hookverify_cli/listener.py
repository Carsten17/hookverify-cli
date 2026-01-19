"""WebSocket listener for receiving webhooks locally."""
import asyncio
import json
import httpx
import websockets


async def forward_to_localhost(port: int, path: str, payload: dict, headers: dict) -> dict:
    """Forward webhook to localhost."""
    url = f"http://localhost:{port}{path}"
    
    forward_headers = {k: v for k, v in headers.items() if k.lower() not in [
        "host", "content-length", "transfer-encoding", "connection"
    ]}
    forward_headers["Content-Type"] = "application/json"
    forward_headers["X-Forwarded-By"] = "HookVerify-CLI"
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(url, json=payload, headers=forward_headers)
            return {
                "success": True,
                "status_code": response.status_code,
                "body": response.text[:500] if response.text else ""
            }
        except httpx.ConnectError:
            return {"success": False, "error": f"Connection refused - is your server running on port {port}?"}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def listen_for_webhooks(
    api_key: str,
    api_url: str,
    port: int,
    path: str = "/",
    on_webhook=None,
    on_connect=None,
    on_error=None
):
    """
    Connect to HookVerify WebSocket and forward webhooks to localhost.
    """
    ws_url = api_url.replace("https://", "wss://").replace("http://", "ws://")
    ws_endpoint = f"{ws_url}/ws/listen/{api_key}"
    
    while True:
        try:
            async with websockets.connect(ws_endpoint) as ws:
                msg = await ws.recv()
                data = json.loads(msg)
                
                if data.get("type") == "connected":
                    if on_connect:
                        on_connect(data)
                    
                    async def ping_loop():
                        while True:
                            await asyncio.sleep(30)
                            try:
                                await ws.send("ping")
                            except:
                                break
                    
                    ping_task = asyncio.create_task(ping_loop())
                    
                    try:
                        async for message in ws:
                            if message == "pong":
                                continue
                                
                            try:
                                webhook_data = json.loads(message)
                                
                                if webhook_data.get("type") == "webhook":
                                    result = await forward_to_localhost(
                                        port=port,
                                        path=path,
                                        payload=webhook_data.get("payload", {}),
                                        headers=webhook_data.get("headers", {})
                                    )
                                    
                                    if on_webhook:
                                        on_webhook(webhook_data, result)
                                        
                            except json.JSONDecodeError:
                                pass
                    finally:
                        ping_task.cancel()
                else:
                    if on_error:
                        on_error(f"Unexpected response: {data}")
                    break
                    
        except websockets.exceptions.ConnectionClosed as e:
            if on_error:
                on_error(f"Connection closed: {e.reason}")
            await asyncio.sleep(5)
            
        except Exception as e:
            if on_error:
                on_error(f"Connection error: {str(e)}")
            await asyncio.sleep(5)
            