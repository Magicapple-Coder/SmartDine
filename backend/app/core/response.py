from typing import Any

# 统一响应结构 { code, message, data }，code=0 表示成功（系统设计说明书 8.1）


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}
