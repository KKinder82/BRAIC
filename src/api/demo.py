from fastapi import APIRouter, Request

from src.api.ApiModel import ApiResponse

demo_router = APIRouter()

@demo_router.get("/test", response_model=ApiResponse, tags=["路由测试"])
async def test():
    return ApiResponse(
        success=True,
        message="Demo 路由测试成功",
        data={}
    )
    

@demo_router.post("/post", response_model=ApiResponse, tags=["路由测试2"])
async def post(request: Request):
    body = await request.body()
    print(body)
    return ApiResponse(
        success=True,
        message="Demo 路由测试2成功",
        data={"body":body}
    )


