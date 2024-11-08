from typing import List, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, Result, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import Response
from starlette.websockets import WebSocket

from chat.chat_client import ChatClient
from chat.message_repository import ChatRepository, MessageRepository
from chat.models import Message, Chat
from chat.schemas import ChatData, MessageData
from database import get_session
from common.auth.dependencies import authenticate
from google_auth.schemas.oidc_user import UserInfoFromIDProvider
from common.auth.schemas.user import UserRead
router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.get("/")
async def get_chats(
        session: AsyncSession = Depends(get_session),
        user: UserRead = Depends(authenticate)
) -> List[ChatData]:
    """
    Get all chats available for authenticated user.
    """
    repository = ChatRepository(session)
    chats = await repository.get_by_filter({"owner_id": user.id})
    return [chat_mapping(chat) for chat in chats]


@router.post("/")
async def new_chat(
        data: ChatData,
        session=Depends(get_session),
        user=Depends(authenticate)
):
    repository = ChatRepository(session)
    chat = Chat(name=data.name, owner_id=user.id)
    await repository.create(chat)
    return ChatData(id=chat.id, name=chat.name)


@router.get("/{chat_id}")
async def get_chat(
        chat_id: UUID,
        session: AsyncSession = Depends(get_session),
        user=Depends(authenticate)
):
    repository = ChatRepository(session)
    chat = await repository.find_by_id(chat_id)
    if not chat:
        return Response(status_code=404)
    if chat.owner_id != user.id:
        return Response(status_code=403)
    msgs = [message_mapping(msg) for msg in chat.messages]
    data = ChatData(id=chat.id, name=chat.name, messages=msgs)
    return data


# only `name` is allowed for update
@router.put("/{chat_id}")
async def update_chat(
        chat_id: UUID,
        data: ChatData,
        session=Depends(get_session),
        user=Depends(authenticate)
):
    repository = ChatRepository(session)
    chat = await repository.find_by_id(chat_id)
    if not chat:
        return Response(status_code=404)
    if chat.owner_id != user.id:
        return Response(status_code=403)
    if data and data.name != chat.name:
        chat.name = data.name
        await repository.update(chat)
    return ChatData(id=chat.id, name=chat.name)


@router.delete("/{chat_id}")
async def delete_chat(
        chat_id: UUID,
        session=Depends(get_session),
        user=Depends(authenticate)
):
    repository = ChatRepository(session)
    chat = await repository.find_by_id(chat_id)
    if not chat:
        return Response(status_code=404)
    if chat.owner_id != user.id:
        return Response(status_code=403)
    await repository.delete_by_id(chat_id)


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
        chat_id: UUID,
        websocket: WebSocket,
        session=Depends(get_session)
):
    await websocket.accept()
    # dependencies:
    chat_repository = ChatRepository(session)
    msg_repository = MessageRepository(session)
    client = ChatClient()
    chat = await chat_repository.find_by_id(chat_id)
    if not chat:
        return Response(status_code=404)
    # TODO: pass user data in WS and then it will work
    # user_repository = OIDCRepository(session)
    # user = await user_repository.get_existing_user(user_info)
    # if chat.owner_id != user.id:
    #     return Response(status_code=403)
    while True:
        data = await websocket.receive_json()
        content = data["content"]
        # map `data` to ORM class and save it
        message = Message(content=content, chat_id=chat_id)
        # save(user, chat_id, data)
        await msg_repository.create(message)
        res = await client.send_message(content)
        m = Message(content=res['message'], chat_id=chat_id)
        await msg_repository.create(m)
        # map `saved` to data class and send it
        json_data = MessageData(id=m.id, content=m.content, references=[])
        await websocket.send_json(json_data.model_dump_json())


def chat_mapping(chat: Chat) -> ChatData:
    return ChatData(id=chat.id, name=chat.name)


def message_mapping(message: Message) -> MessageData:
    return MessageData(id=message.id, content=message.content, references=[])  # TODO: fix refs
