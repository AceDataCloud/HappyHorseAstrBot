"""Happy Horse request and terminal-result boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import HappyHorseClient, HappyHorseError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-happyhorse"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_video_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"task_id": "task-123"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await HappyHorseClient("test-key").submit("A paper kite rises")
    assert calls == [
        (
            "https://api.acedata.cloud/happyhorse/videos",
            {
                "action": "generate",
                "prompt": "A paper kite rises",
                "model": "happyhorse-1.1-t2v",
                "ratio": "16:9",
                "resolution": "720P",
                "duration": 3,
                "watermark": False,
                "async": True,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert "video_urls" not in result


@pytest.mark.asyncio
async def test_image_request_uses_one_authorized_first_frame():
    with patch(
        "client.OPENER.open", return_value=FakeResponse({"task_id": "task-456"})
    ) as opening:
        await HappyHorseClient("test-key").submit(
            "A kite rises",
            model="happyhorse-1.1-i2v",
            image_url="https://example.org/kite.png",
            ratio="9:16",
        )
    payload = json.loads(opening.call_args.args[0].data)
    assert payload["action"] == "image_to_video"
    assert payload["image_url"] == "https://example.org/kite.png"
    assert payload["ratio"] == "9:16"


@pytest.mark.asyncio
async def test_task_lookup_withholds_preview_until_terminal_success():
    pending = {"id": "task-123", "finished_at": None, "response": None}
    preview = {
        "id": "task-123",
        "finished_at": None,
        "response": {
            "success": True,
            "data": [
                {
                    "state": "succeeded",
                    "video_url": "https://cdn.example.org/preview.mp4",
                }
            ],
        },
    }
    finished = {
        "finished_at": 123.0,
        "response": {
            "success": True,
            "data": [
                {
                    "state": "succeeded",
                    "video_url": "https://cdn.example.org/final.mp4",
                    "supplier": "internal-only",
                }
            ],
            "cost": {
                "amount": 2.97,
                "list_amount": 3.3,
                "currency": "credit",
                "supplier": "internal-only",
            },
        },
    }
    failed = {
        "finished_at": 123.0,
        "response": {
            "success": False,
            "data": [
                {
                    "state": "failed",
                    "video_url": "https://cdn.example.org/preview.mp4",
                }
            ],
        },
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(pending),
            FakeResponse(preview),
            FakeResponse(finished),
            FakeResponse(failed),
        ],
    ) as opening:
        first = await HappyHorseClient("test-key").query("task-123")
        second = await HappyHorseClient("test-key").query("task-123")
        last = await HappyHorseClient("test-key").query("task-123")
        unsuccessful = await HappyHorseClient("test-key").query("task-123")
    assert opening.call_count == 4
    assert first["status"] == second["status"] == "pending"
    assert first["video_urls"] == second["video_urls"] == []
    assert last["status"] == "succeeded"
    assert last["video_urls"] == ["https://cdn.example.org/final.mp4"]
    assert last["cost"] == {
        "amount": 2.97,
        "list_amount": 3.3,
        "currency": "credit",
    }
    assert "supplier" not in str(last)
    assert unsuccessful["status"] == "failed"
    assert unsuccessful["video_urls"] == []


@pytest.mark.asyncio
async def test_invalid_inputs_never_submit_a_paid_job():
    client = HappyHorseClient("test-key")
    for kwargs in (
        {"prompt": " "},
        {"prompt": "A kite", "model": "unknown"},
        {"prompt": "A kite", "resolution": "480p"},
        {"prompt": "A kite", "image_url": "http://example.org/kite.png"},
        {"prompt": "A kite", "ratio": "21:9"},
        {"prompt": "A kite", "duration": 2},
        {"prompt": "A kite", "model": "happyhorse-1.1-i2v"},
    ):
        with patch("client.OPENER.open") as opening, pytest.raises(HappyHorseError):
            await client.submit(**kwargs)
        assert opening.call_count == 0
