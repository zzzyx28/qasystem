"""
文本切片组件：进程内调用 algorithm/NL_to_cypher 中的 splitter 能力。
使用前需安装 algorithm/NL_to_cypher 依赖。
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parents[5]
_NL2CYPHER_ROOT = _ROOT / "algorithm" / "NL_to_cypher"
if _NL2CYPHER_ROOT.exists() and str(_NL2CYPHER_ROOT) not in sys.path:
    sys.path.insert(0, str(_NL2CYPHER_ROOT))


def health() -> dict[str, Any]:
    try:
        _get_splitter()
        return {"status": "ok"}
    except Exception as e:
        return {
            "status": "unavailable",
            "detail": f"文本切片模块不可用: {e}。请确认已安装 algorithm/NL_to_cypher 依赖。",
        }


def _get_splitter():
    """懒加载 NL_to_cypher.splitter 模块并返回引用"""
    try:
        import splitter as _mod  # type: ignore
        return _mod
    except Exception as e:
        logger.warning("加载切片模块失败: %s", e)
        raise


def _make_docs(text: str, source: str = "unknown"):
    """创建文档并添加 metadata"""
    from langchain_core.documents import Document

    return [Document(page_content=text, metadata={"source": source})]


def split_by_character(text: str) -> dict[str, Any]:
    mod = _get_splitter()
    docs = _make_docs(text)
    split_docs = mod.split_by_character(docs)
    return {"chunks": [d.page_content for d in split_docs]}


def split_recursively(text: str) -> dict[str, Any]:
    mod = _get_splitter()
    docs = _make_docs(text)
    split_docs = mod.split_recursively(docs)
    return {"chunks": [d.page_content for d in split_docs]}


def split_by_markdown(text: str) -> dict[str, Any]:
    mod = _get_splitter()
    docs = _make_docs(text)
    split_docs = mod.split_by_markdown(docs)
    return {"chunks": [d.page_content for d in split_docs]}


def split_by_language_python(text: str) -> dict[str, Any]:
    mod = _get_splitter()
    docs = _make_docs(text)
    split_docs = mod.split_by_language_python(docs)
    return {"chunks": [d.page_content for d in split_docs]}


def muti_retriever() -> List[Dict[str, Any]]:
    try:
        import rag
    except Exception as e:
        logger.warning("加载 RAG 模块失败: %s", e)
        raise
    nodes = rag.load_json_nodes(_NL2CYPHER_ROOT / "records.json")
    results = rag.get_vectors_for_nodes(nodes)
    if results:
        return _json_safe(results)
    logger.info(
        "mutiRetriever: records.json 中 VectorAddress 未在 Milvus 命中任何条，回退为当前集合全表导出"
    )
    fallback = rag.list_all_milvus_rows_for_multiretriever()
    return _json_safe(fallback)


def _json_safe(obj: Any) -> Any:
    """Milvus 查询结果中可能含 protobuf RepeatedScalarContainer、numpy 标量等，需转为可 JSON 序列化类型。"""
    if obj is None or isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    try:
        import numpy as np

        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return _json_safe(obj.tolist())
    except ImportError:
        pass
    if hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, dict)):
        try:
            return [_json_safe(x) for x in list(obj)]
        except Exception:
            pass
    return str(obj)

