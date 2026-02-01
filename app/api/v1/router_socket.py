from fastapi import APIRouter, WebSocket,WebSocketDisconnect
from typing import Dict

class ConnectionManger:
    def __init__(self):
        self.active_connections: Dict[int,Dict[int,WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int) -> None:
        """
        Устанавливает соединение с пользователем
        websocket.accept() - подтверждает подключение.
        :param websocket: Websocket
        :param room_id: ID комнаты чата
        :param user_id: ID подключаемого пользователя
        :return: None
        """
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int) -> None:
        """
        Закрывает соединение и удаляет его из списка активных подключений.
        Если в комнате больше нет пользователей, удаляет комнату.
        :param room_id: ID комнаты чата
        :param user_id: ID подключаемого пользователя
        :return: None
        """
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: int, sender_id: int) -> None:
        """
        Рассылает сообщение всем пользователям в комнате.
        :param message: Текст сообщения
        :param room_id: ID комнаты чата
        :param sender_id: ID отправителя
        :return:
        """
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                message_with_class = {
                    "text": message,
                    "is_self": user_id == sender_id,
                }
                await connection.send_json(message_with_class)

router = APIRouter(prefix="/ws/chat")
manager = ConnectionManger()

@router.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, user_id: int, username: str) -> None:
    await manager.connect(websocket, room_id, user_id)
    await manager.broadcast(f"{username} присоединился к чату.", room_id, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username} (ID: {user_id}): {data}", room_id, user_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)
        await manager.broadcast(f"{username} (ID: {user_id}) покинул чат.", room_id, user_id)