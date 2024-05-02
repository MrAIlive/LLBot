from typing import Any, Optional, Dict, List

__all__=[
    "Event"
]
class Event(dict):
    """构造Params参数列表,如果是是字符串需要提前调用from_Params进行转换"""

    @classmethod
    def from_Params(cls, Params: str | Dict) -> 'Optional[Event]':
        """
        从Event构造Params对象，
        需要注意的是```type```和```detail_type```在没消息的和是str时候单独调用可能会报错
        """
        try:
            import json
            e = cls(json.loads(Params))
            # 判断是否有消息没有的话则报错返回None
            _ = e.type, e.detail_type
            return e
        except KeyError:
            return None

    @property
    def type(self) -> str:
        """
        事件类型，有``message``、``notice``、``request``、``meta_event``等。"""
        return self['post_type']

    @property
    def detail_type(self) -> str:
        """
        事件具体类型，依 `type` 的不同而不同，以 ``message`` 类型为例，有
        ``private``、``group``、``discuss`` 等。
        """
        return self[f"{self.type}_type"]

    @property
    def sub_type(self) -> str:
        """
        事件子类型，依 `detail_type` 不同而不同，以 ``message.private`` 为例，有
        ``friend``、``group``、``discuss``、``other`` 等。
        """
        return self.get('sub_type')

    @property
    def group_params(self) -> dict | None:
        """此方法用于快速获取群聊消息的参数"""
        try:
            params = {"group_id": self["group_id"], "message": self["message"], "user_id": self["user_id"],
                      "role": self["sender"]["role"], "name": self["sender"]["nickname"], "self_id": self["self_id"]}
            return params
        except KeyError:
            return None

    @property
    def private_params(self) -> dict | None:
        """此方法用于快速获取私聊消息的参数"""
        try:
            params = {"user_id": self["user_id"], "self_id": self["self_id"], "message": self["message"],
                      "name": self["sender"]["nickname"]}
            return params
        except KeyError:
            return None

    @property
    def request_friend(self) -> dict | None:
        try:
            params = {"self_id": self["self_id"], "user_id": self["user_id"], "comment": self["comment"]}
            return params
        except KeyError:
            return None

    @property
    def request_group(self) -> dict | None:
        try:
            params = {"self_id": self["self_id"], "user_id": self["user_id"], "group_id": self["group_id"],
                      "comment": self["comment"]}
            return params
        except KeyError:
            return None

    # TODO:这里需要实现notice和request的参数过滤

    self_id: int  # 机器人自身 ID
    user_id: Optional[int]  # 用户 ID
    operator_id: Optional[int]  # 操作者 ID
    group_id: Optional[int]  # 群 ID
    discuss_id: Optional[int]  # 讨论组 ID，此字段已在 OneBot v11 中移除
    message_id: Optional[int]  # 消息 ID
    message: Optional[Any]  # 消息
    raw_message: Optional[str]  # 未经 OneBot (CQHTTP) 处理的原始消息
    sender: Optional[Dict[str, Any]]  # 消息发送者信息
    anonymous: Optional[Dict[str, Any]]  # 匿名信息
    file: Optional[Dict[str, Any]]  # 文件信息
    comment: Optional[str]  # 请求验证消息
    flag: Optional[str]  # 请求标识

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setattr__(self, key, value) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return f"<Event,{super().__repr__()}>"

