import asyncio
import struct
import logging
from fastapi import WebSocket

logger = logging.getLogger("X4G-Relay")
RELAY_BUF = 65536

def parse_vless_header(data: bytes):
    if len(data) < 18:
        return None
    version = data[0]
    uuid_bytes = data[1:17]
    addons_len = data[17]
    idx = 18 + addons_len
    if len(data) < idx + 4:
        return None
    command = data[idx]
    port = struct.unpack(">H", data[idx+1:idx+3])[0]
    addr_type = data[idx+3]
    idx += 4
    
    host = ""
    if addr_type == 1:
        if len(data) < idx + 4: return None
        host = ".".join(str(b) for b in data[idx:idx+4])
        idx += 4
    elif addr_type == 2:
        if len(data) < idx + 1: return None
        domain_len = data[idx]
        idx += 1
        if len(data) < idx + domain_len: return None
        host = data[idx:idx+domain_len].decode("utf-8", errors="ignore")
        idx += domain_len
    elif addr_type == 3:
        if len(data) < idx + 16: return None
        host = ":".join(f"{struct.unpack('>H', data[i:i+2])[0]:x}" for i in range(idx, idx+16, 2))
        idx += 16

    header_len = idx
    return {
        "version": version,
        "uuid": uuid_bytes.hex(),
        "command": command,
        "port": port,
        "host": host,
        "header_len": header_len,
        "payload": data[header_len:]
    }

async def check_and_use(uuid: str, bytes_count: int) -> bool:
    from main import LINKS, LINKS_LOCK, is_link_allowed
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
        if not is_link_allowed(link):
            return False
        link["used_bytes"] = link.get("used_bytes", 0) + bytes_count
    return True

async def relay_ws_to_tcp(ws: WebSocket, writer: asyncio.StreamWriter, uuid: str):
    try:
        while True:
            data = await ws.receive_bytes()
            if not await check_and_use(uuid, len(data)):
                break
            writer.write(data)
            await writer.drain()
    except Exception:
        pass

async def relay_tcp_to_ws(reader: asyncio.StreamReader, ws: WebSocket, uuid: str):
    try:
        while True:
            data = await reader.read(RELAY_BUF)
            if not data:
                break
            if not await check_and_use(uuid, len(data)):
                break
            await ws.send_bytes(data)
    except Exception:
        pass

async def websocket_tunnel(websocket: WebSocket, uuid: str):
    await websocket.accept()
    from main import LINKS, LINKS_LOCK, is_link_allowed, connections
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    if not link or not is_link_allowed(link):
        await websocket.close(code=1008)
        return

    conn_id = f"{uuid}_{id(websocket)}"
    client_ip = websocket.client.host if websocket.client else "unknown"
    connections[conn_id] = {"uuid": uuid, "ip": client_ip, "transport": "vless-ws", "bytes": 0}

    try:
        first_data = await websocket.receive_bytes()
        header = parse_vless_header(first_data)
        if not header:
            await websocket.close(code=1003)
            return

        reader, writer = await asyncio.open_connection(header["host"], header["port"])
        writer.write(bytes([header["version"], 0]))
        if header["payload"]:
            writer.write(header["payload"])
        await writer.drain()

        t1 = asyncio.create_task(relay_ws_to_tcp(websocket, writer, uuid))
        t2 = asyncio.create_task(relay_tcp_to_ws(reader, websocket, uuid))
        await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
        t1.cancel()
        t2.cancel()
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        logger.debug(f"Tunnel error: {e}")
    finally:
        connections.pop(conn_id, None)
        try:
            await websocket.close()
        except Exception:
            pass
