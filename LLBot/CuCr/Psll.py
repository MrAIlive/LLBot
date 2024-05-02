from typing import Any, Optional, Dict, List

__all__ = [
    "params"
]


class params(dict):
    """
    初始化的参数有
    ```sf,GroupList,以及```FriendList```
    """

    @classmethod
    def from_data(cls, data: Dict[str, List]) -> 'Optional[params]':
        """构造初始化参数的参数"""
        try:
            e = cls(data)
            _ = e.GroupList, e.FriendList
            return e
        except KeyError:
            return None

    @classmethod
    def sfs(cls, data: Dict[str, List]) -> 'Optional[params]':
        data = data["sf"]
        e = cls(data)
        return e

    @property
    def GroupList(self) -> list[dict[str, int]]:
        return self['GroupList']

    @property
    def FriendList(self) -> list[dict[str, int]]:
        return self['FriendList']

    @classmethod
    def GroupDict(cls, data: Dict[str, List], Group_id) -> 'Optional[params]':
        Lists = cls(data).GroupList
        for NameDict in Lists:
            try:
                if NameDict['group_id'] == Group_id:
                    e = cls(NameDict)
                    return e
            except KeyError:
                return None

    @classmethod
    def FriendDict(cls, data: Dict[str, List], Friend_ID) -> 'Optional[params]':
        Lists = cls(data).FriendList
        for FriendDict in Lists:
            try:
                if FriendDict['user_id'] == Friend_ID:
                    e = cls(FriendDict)
                    return e
            except KeyError:
                return None

    nickname: Optional[Any]
    user_id: Optional[int]
    group_name: Optional[str]
    group_id: Optional[int]

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setstate__(self, key, value) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return f"<params,{super().__repr__()}>"
