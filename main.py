from LLBot import *
import os

os.system("cls")

async def AI(websocket, Evnet_params: Event, Lock):
    Spark = SparkAPI(url="wss://spark-api.xf-yun.com/v3.5/chat",
                     APiSecret="NzZjMTI1NTkxMGY5YzdjN2UxYjJlZDQz",
                     apikey="3bdea11a61e16097810ad59e73258749",
                     appid="29693ce8", EVENT=Evnet_params, Lock=Lock)
    await Spark.run_forever(websocket.send)


class LLBotSocket(LLBotSocketServer_ABS):

    async def Request_Group_Invite(self, websocket, data: [dict[dict | list]], Event_params: Event):
        pass

    async def Request_Group_Add(self, websocket, data: [dict[dict | list]], Event_params: Event):
        pass

    async def Request_Friend_Add(self, websocket, data: [dict[dict | list]], Event_params: Event):
        pass

    async def PrivateMsgType(self, websocket, data: [dict[dict | list]], Event_params: Event):
        await AI(websocket=websocket, Evnet_params=Event_params, Lock=self.Lock)

    async def GroupMsgType(self, websocket, data: [dict[dict | list]], Event_params: Event):
        await AI(websocket=websocket, Evnet_params=Event_params, Lock=self.Lock)


if __name__ == '__main__':
    LLBotSocket.LLBotWebSocketStart("127.0.0.1", 8808)
