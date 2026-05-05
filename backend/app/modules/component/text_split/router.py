"""
文本切分组件 API：进程内调用 algorithm/NL_to_cypher。
"""
import asyncio
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....deps.auth import require_admin
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/component/text-split",
    tags=["component", "text-split"],
    dependencies=[Depends(require_admin)],
)


class TextRequestBody(BaseModel):
    text: str


@router.get("/health")
async def text_split_health() -> dict[str, Any]:
    return service.health()


@router.post("/split/character")
async def split_character(body: TextRequestBody) -> dict[str, Any]:
    if not (body.text or "").strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    try:
        result = await asyncio.to_thread(
            service.split_by_character,
            text=body.text.strip(),
        )
        return result
    except Exception as e:
        logger.exception("字符切片失败")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/split/recursive")
async def split_recursive(body: TextRequestBody) -> dict[str, Any]:
    if not (body.text or "").strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    try:
        result = await asyncio.to_thread(
            service.split_recursively,
            text=body.text.strip(),
        )
        return result
    except Exception as e:
        logger.exception("递归字符切片失败")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/split/markdown")
async def split_markdown(body: TextRequestBody) -> dict[str, Any]:
    if not (body.text or "").strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    try:
        result = await asyncio.to_thread(
            service.split_by_markdown,
            text=body.text.strip(),
        )
        return result
    except Exception as e:
        logger.exception("Markdown切片失败")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/split/python")
async def split_python(body: TextRequestBody) -> dict[str, Any]:
    if not (body.text or "").strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    try:
        result = await asyncio.to_thread(
            service.split_by_language_python,
            text=body.text.strip(),
        )
        return result
    except Exception as e:
        logger.exception("Python语言切片失败")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/mutiRetriever")
async def get_all_info() -> List[Dict[str, Any]]:
    try:
        results = await asyncio.to_thread(service.muti_retriever)
        return results
    except Exception as e:
        logger.exception("获取向量数据失败")
        raise HTTPException(status_code=500, detail=str(e)) from e

