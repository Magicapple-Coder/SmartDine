from pydantic import BaseModel


class LoginIn(BaseModel):
    account: str
    password: str


class WxLoginIn(BaseModel):
    code: str  # 小程序 wx.login() 返回的 code


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
