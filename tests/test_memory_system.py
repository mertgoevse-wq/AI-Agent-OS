"""Tests for 4-Tier Memory System (STM, LTM, Knowledge, Vector DB)."""

import pytest
from src.memory.base import MemoryItem
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.memory.knowledge import KnowledgeMemory
from src.memory.vector_db import InMemoryVectorStore, VectorRecord


@pytest.mark.asyncio
async def test_short_term_memory():
    stm = ShortTermMemory(max_turns=3)

    await stm.add_message("user", "Hello 1")
    await stm.add_message("assistant", "Hi 1")
    await stm.add_message("user", "Hello 2")
    await stm.add_message("assistant", "Hi 2")

    context = stm.get_context_window()
    assert len(context) == 3
    assert context[0]["content"] == "Hi 1"
    assert context[-1]["content"] == "Hi 2"

    stm.set_scratchpad_value("current_task", "analysis")
    assert stm.get_scratchpad_value("current_task") == "analysis"


@pytest.mark.asyncio
async def test_long_term_memory():
    ltm = LongTermMemory()

    await ltm.set("user_pref_theme", "dark", category="preference")
    val = await ltm.get("user_pref_theme")
    assert val == "dark"

    items = await ltm.retrieve("theme")
    assert len(items) == 1
    assert items[0].id == "user_pref_theme"


@pytest.mark.asyncio
async def test_knowledge_memory():
    km = KnowledgeMemory()

    doc_text = "Python is an interpreted high-level programming language. Artificial intelligence relies heavily on Python."
    chunks = await km.add_document("doc_py", doc_text, chunk_size=5)

    assert len(chunks) == 3

    results = await km.retrieve("programming language")
    assert len(results) > 0
    assert "programming" in results[0].content



@pytest.mark.asyncio
async def test_in_memory_vector_store():
    store = InMemoryVectorStore()

    vec1 = store.create_simple_embedding("crypto trading strategy", dim=8)
    vec2 = store.create_simple_embedding("music composition synthesizers", dim=8)

    rec1 = VectorRecord(id="rec1", vector=vec1, content="Crypto Pilot strategy", metadata={"app": "cryptopilot"})
    rec2 = VectorRecord(id="rec2", vector=vec2, content="AirBeat music synth", metadata={"app": "airbeat"})

    await store.add([rec1, rec2])

    # Search with query close to rec1
    query_vec = store.create_simple_embedding("crypto trading", dim=8)
    search_results = await store.search(query_vec, limit=2)

    assert len(search_results) == 2
    assert search_results[0].record.id == "rec1"
    assert search_results[0].score > search_results[1].score

    # Search with metadata filter
    filtered = await store.search(query_vec, limit=2, metadata_filter={"app": "airbeat"})
    assert len(filtered) == 1
    assert filtered[0].record.id == "rec2"
