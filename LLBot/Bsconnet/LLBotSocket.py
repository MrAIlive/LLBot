import asyncio
from abc import ABC, abstractmethod
from asyncio import CancelledError
import websockets.client
from LLBot.aiosend.onebotAPI import OneBotAPI
from websockets import serve, ConnectionClosedError, ConnectionClosedOK
from LLBot.CuCr import *
from LLBot.Plugin.log import *

__all__ = [
    "LLBotSocketServer_ABS",
    "LLBotSocketClient_ABS"
]


class LLBotSocketServer_ABS(ABC):
    """推荐在继承实现```PrivateMsgType等所有```
        ```连接地址/v11/LLBotSocket```
    方法之后将```LLBotWebSocketStart```作为连接的主方法
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.Lock = asyncio.Lock()  # acquire() #release()

    @staticmethod
    async def InitSelf(websocket, ID: int) -> dict:
        import json
        data = {}

        async def InitSelf() -> dict:
            await OneBotAPI(send=websocket.send).get_login_info()
            DATA = json.loads(await websocket.recv())["data"]
            return DATA

        async def InitGroup() -> dict:
            await OneBotAPI(send=websocket.send).get_group_list()
            DATA = json.loads(await websocket.recv())["data"]
            return DATA

        async def InitFriend() -> dict:
            await OneBotAPI(send=websocket.send).get_friend_list()
            DATA = json.loads(await websocket.recv())["data"]
            return DATA

        async def InitStart() -> dict:
            data.update({"sf": await InitSelf()})
            data.update({"GroupList": await InitGroup()})
            data.update({"FriendList": await InitFriend()})
            return data

        async def ERROR() -> dict:
            logger.warning("账号:[%d]开始尝试重新初始化!")
            num = 0
            while True:
                logger.warning("账号:[%d]开始第%d次回调尝试", num + 1, ID)
                try:
                    DATA = await InitStart()
                    return DATA
                except KeyError as K:
                    logger.error("账号:[%d]第%d次初始化回调失败!,ERROR:%S", ID, num, K)
                    await asyncio.sleep(1)
                    continue

        try:
            data = await InitStart()
            logger.info("初始化成功!你好!%s(%d)", data['sf']['nickname'], data['sf']['user_id'])
            logger.info("加载到好友%d位!", len(data['FriendList']))
            logger.info("加载到群聊%d个!", len(data['GroupList']))
            logger.info("开始为账号:%s(%d)处理消息!", data['sf']['nickname'], data['sf']['user_id'])
            return data
        except Exception as E:
            logger.error("账号:[%d]初始化错误!%s", ID, E)
            data = await ERROR()
            return data

    @abstractmethod
    async def GroupMsgType(self, websocket, data: [dict[dict | list]], Event_params: Event):
        """
        用于处理群消息
        :param websocket: await websocket.send() 用于发送消息
        :param data: 自身的属性，（自己的名字和好友列表以及加入的群列表）
        :param Event_params: 经过处理后的Event是一个字典也就是事件
        :return:
        """
        pass

    @abstractmethod
    async def PrivateMsgType(self, websocket, data: [dict[dict | list]], Event_params: Event):
        """
        用于处理私聊消息
        :param websocket: await websocket.send() 用于发送消息
        :param data: 自身的属性，（自己的名字和好友列表以及加入的群列表）
        :param Event_params: 经过处理后的Event是一个字典也就是事件
        :return:
        """
        pass

    @abstractmethod
    async def Request_Group_Add(self, websocket, data: [dict[dict | list]], Event_params: Event):
        """
        用于处理群聊加群消息
        :param websocket: await websocket.send() 用于发送消息
        :param data: 自身的属性，（自己的名字和好友列表以及加入的群列表）
        :param Event_params: 经过处理后的Event是一个字典也就是事件
        :return:
        """
        pass

    @abstractmethod
    async def Request_Group_Invite(self, websocket, data: [dict[dict | list]], Event_params: Event):
        """
        用于处理群聊加群邀请
        :param websocket: await websocket.send() 用于发送消息
        :param data: 自身的属性，（自己的名字和好友列表以及加入的群列表）
        :param Event_params: 经过处理后的Event是一个字典也就是事件
        :return:
        """
        pass

    @abstractmethod
    async def Request_Friend_Add(self, websocket, data: [dict[dict | list]], Event_params: Event):
        """
        用于处理好友添加事件
        :param websocket: await websocket.send() 用于发送消息
        :param data: 自身的属性，（自己的名字和好友列表以及加入的群列表）
        :param Event_params: 经过处理后的Event是一个字典也就是事件
        :return:
        """
        pass

    async def LogGroupMessage(self, websocket, data: [dict[dict | list]], Event_params: Event) -> None:
        if Event_params.type == "message" and Event_params.detail_type == "group":
            logger.info(
                "账号:[%s(%d)]收到群聊【%s(%d)】%s(%d)的消息 --> %s", params.sfs(data).nickname,
                params.sfs(data).user_id, params.GroupDict(data, Event_params.group_id).group_name,
                params.GroupDict(data, Event_params.group_id).group_id, Event_params.sender['nickname'],
                Event_params.user_id, Event_params.message
            )

            # 加入消息处理函数
            await self.GroupMsgType(websocket, data, Event_params)

    async def LogPrivateMessage(self, websocket, data: dict, Event_params: Event) -> None:
        if Event_params.type == "message" and Event_params.detail_type == "private":
            logger.info("账号:[%s(%d)]收到私聊用户【%s(%d)】的消息 --> %s", params.sfs(data).nickname,
                        params.sfs(data).user_id, Event_params.sender['nickname'], Event_params.user_id,
                        Event_params.message)
            # 加入消息处理函数
            await self.PrivateMsgType(websocket, data, Event_params)

    async def LogRequestGroup(self, websocket, data: dict, Event_params: Event) -> None:
        if Event_params.type == "request" and Event_params.detail_type == "group":
            async def Group_add():
                logger.info("账号:[%s(%d)]收到加群请求!",
                            params.sfs(data).nickname, params.sfs(data).user_id)
                #  加入群加入处理函数
                await self.Request_Group_Add(websocket, data, Event_params)

            async def Group_invite() -> None:
                logger.info("账号:[%s(%d)]收到加群邀请!",
                            params.sfs(data).nickname, params.sfs(data).user_id)
                # 加入群邀请处理函数
                await self.Request_Group_Invite(websocket, data, Event_params)

            await Group_add() if Event_params.sub_type != "invite" else await Group_invite()

    async def LogRequestFriendAddMsg(self, websocket, data: dict, Event_params: Event) -> None:
        """
        这个函数是关于好友申请的函数
        """
        if Event_params.type == "request" and Event_params.detail_type == "friend":
            logger.info("账号:[%s(%d)]收到加好友请求!", params.sfs(data).nickname, params.sfs(data).user_id)
            await self.Request_Friend_Add(websocket, data, Event_params)

    async def EventTypeStart(self, websocket, data: dict) -> None:
        """消息处理需要自己实现"""
        while True:
            Event_params: Event = Event.from_Params(await websocket.recv())
            if Event_params is None:
                continue
            # Lock.acquire()
            # Lock.release()
            Task = (
                self.LogRequestGroup(websocket=websocket, Event_params=Event_params, data=data),
                self.LogRequestFriendAddMsg(websocket=websocket, Event_params=Event_params, data=data),
                self.LogGroupMessage(websocket=websocket, Event_params=Event_params, data=data),
                self.LogPrivateMessage(websocket=websocket, Event_params=Event_params, data=data))
            Task = [asyncio.create_task(Task[i]) for i in range(len(Task))]
            Start = asyncio.wait(Task)
            try:
                await Start
                Start.close()
            except RuntimeError:
                Start.close()

    async def LLBotHandler(self, websocket, path) -> None:
        ID = Event.from_Params(await websocket.recv()).self_id
        if path != "/v11/LLBotSocket":
            logger.warning("由于账号:[%d]连接路径不正确(%s),已拒绝连接!", ID, path)
            await websocket.close()
        logger.info("账号:[%d]已通过路径(%s)连接服务!开始加载账号信息!", ID, path)
        data = await self.InitSelf(websocket, ID)
        try:
            await self.EventTypeStart(websocket, data)
        except ConnectionClosedOK:
            await websocket.close()
            logger.warning("服务已关闭!已关闭所有连接!")
        except ConnectionClosedError:
            logger.warning("账号:[%d]已离线!", ID)
            await websocket.close()

    async def LLBotStart(self) -> None:
        server = serve(
            ws_handler=self.LLBotHandler, host=self.host, port=self.port
        )
        logger.info("LLBot已启动!")
        logger.info("LLBot开始等待连接处理消息!")
        try:
            async with server:
                await asyncio.Future()
        except CancelledError:
            pass

    @classmethod
    def LLBotWebSocketStart(cls, host: str, port: int) -> None:
        try:
            _ = cls(host, port)
            asyncio.run(_.LLBotStart())
        except KeyboardInterrupt:
            pass


class LLBotSocketClient_ABS(ABC):
    # TODO: 正向websocket连接未完!
    def __init__(self, url, port):
        self.url = url
        self.port = port

    async def LLBotStart(self):
        start = websockets.client
        await start.connect(uri=self.url+str(self.port))
