import asyncio

import websockets


class WsServer:
  def __init__(self, host: str, port: int) -> None:
    self._host = host
    self._port = port
    self._clients: set = set()
    self._loop: asyncio.AbstractEventLoop | None = None

  async def _handler(self, websocket) -> None:
    self._clients.add(websocket)
    print(f"WS client connected: {websocket.remote_address}")
    try:
      async for _ in websocket:
        pass
    finally:
      self._clients.discard(websocket)
      print(f"WS client disconnected: {websocket.remote_address}")

  async def _run(self) -> None:
    self._loop = asyncio.get_running_loop()
    async with websockets.serve(self._handler, self._host, self._port):
      print(f"WS server listening on {self._host}:{self._port}")
      await asyncio.Future()

  def run(self) -> None:
    asyncio.run(self._run())

  def broadcast(self, message: str) -> None:
    if self._loop is None:
      print("WS server not ready yet, dropping message")
      return
    asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

  async def _broadcast(self, message: str) -> None:
    if not self._clients:
      return
    await asyncio.gather(*(ws.send(message) for ws in list(self._clients)), return_exceptions=True)