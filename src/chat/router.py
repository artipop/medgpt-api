import asyncio
import os
import shutil
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from starlette.websockets import WebSocket

from settings import settings
from chat.chat_client import ChatClient
from chat.message_repository import ChatRepository, MessageRepository
from chat.models import Message, Chat, Source, UploadedFile
from chat.schemas import ChatData, MessageData, SourceData
from database import get_session
from common.auth.dependencies import authenticate
from common.auth.schemas.user import UserRead
from chat.repos import UploadedFilesRepository


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
        user=Depends(authenticate),
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
    await repository.delete(chat)


@router.post("/uploadfile")
async def upload_file(file: UploadFile = File(...), session=Depends(get_session), user: UserRead = Depends(authenticate)):

    if not file.filename.endswith(('pdf', 'docx', 'doc')):
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый файл"
        )


    # file saving
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static_files',
        file.filename
    )
    with open(path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_path = f"{settings.api_base_url}/api/uploaded/{file.filename}"

    repository = UploadedFilesRepository(session) 
    query = (
        insert(UploadedFile)
        .values(
            sender_id=user.id,
            file_path=db_path
        )
        .returning(UploadedFile)
    )
    result = await session.execute(query)
    await session.commit()

    # client = ChatClient()
    # content: bytes = await file.read()
    # await client.send_file(content, file.filename, file.content_type)


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
    # TODO: this doesn't work
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
        message = Message(content=content, chat_id=chat_id, role='user')
        # save(user, chat_id, data)
        await msg_repository.create(message)
        in_data = MessageData(id=message.id, content=message.content, role=message.role, sources=[])
        await websocket.send_json(in_data.model_dump_json())
        res = await client.send_message(content)
        x = []
        if res['documents']:
            for doc in res['documents']:
                metadata_ = doc['meta_data']
                source = Source(title=metadata_['title'],
                                extended_title=metadata_['extended']['title'] if metadata_['extended'] else metadata_['title'])
                session.add(source)
#                await session.commit()
#                await session.refresh(source)
                x.append(source)
#                x.append(Source(title=metadata_['title'], extended_title=metadata_['extended']['title'] if metadata_['extended'] else ''))
#                x.append(Source(title=metadata_['title'] if metadata_['title'] else '', extended_title=metadata_['extended']['title'] if metadata_['extended'] else ''))
#                x.append(Source(title=metadata_['title'], extended_title=metadata_['extended']['title']))
        m = Message(content=res['message'], chat_id=chat_id, role='agent', sources=x)
        session.add_all(x + [m])  # добавляем всё сразу
        await session.commit()    # один коммит на всех
        await asyncio.gather(*(session.refresh(s) for s in x))
        #await msg_repository.create(m)
        # map `saved` to data class and send it
        json_data = MessageData(id=m.id, content=m.content, role=m.role, sources=[map_source(a) for a in x])
        await websocket.send_json(json_data.model_dump_json())


def chat_mapping(chat: Chat) -> ChatData:
    return ChatData(id=chat.id, name=chat.name)


def message_mapping(message: Message) -> MessageData:
    return MessageData(id=message.id, content=message.content, role=message.role, sources=[])  # TODO: fix refs


def map_source(source: Source) -> SourceData:
#    return SourceData(None, source.title, source.extended_title)
    return SourceData(id=source.id, title=source.title, extended_title=source.extended_title)
