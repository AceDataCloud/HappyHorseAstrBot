"""Happy Horse tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import HappyHorseClient, HappyHorseError


class HappyHorsePlugin(Star):
    """Expose one video submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="happyhorse_generate_video")
    async def happyhorse_generate_video(
        self,
        event: AstrMessageEvent,
        prompt: str,
        model: str = "happyhorse-1.1-t2v",
        image_url: str = "",
        ratio: str = "16:9",
        resolution: str = "720P",
        duration: int = 3,
    ) -> str:
        """Submit one billable Happy Horse text or image video job.

        Args:
            prompt(string): Description of the desired video.
            model(string): Supported Happy Horse t2v or i2v model ID.
            image_url(string): Optional authorized HTTPS source image.
            ratio(string): Output ratio such as 16:9 or 9:16.
            resolution(string): 720P or 1080P.
            duration(number): 3–15 video seconds.

        Returns:
            JSON submission status and task ID, never a finished-video claim.
        """
        try:
            result = await HappyHorseClient(self.config.get("api_key", "")).submit(
                prompt, model, image_url, ratio, resolution, duration
            )
        except HappyHorseError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="happyhorse_get_task")
    async def happyhorse_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query an existing Happy Horse task without generating another video.

        Args:
            task_id(string): Exact task ID returned by happyhorse_generate_video.

        Returns:
            JSON task status and final video URLs only after terminal success.
        """
        try:
            result = await HappyHorseClient(self.config.get("api_key", "")).query(
                task_id
            )
        except HappyHorseError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)

    @filter.command("happyhorse_ace")
    async def happyhorse_ace_help(self, event: AstrMessageEvent):
        """Show Happy Horse setup and existing-task help without an API call."""
        yield event.plain_result(
            "Happy Horse by Ace Data Cloud / Ace Data Cloud 提供的 Happy Horse 集成\nSetup / 配置：Plugins → Plugins → Installed → plugin gear / 插件 → 插件 → 已安装 → 齿轮。\nRegister/sign in / 注册登录：https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorseastrbot_command_help\nGeneral application → Manage Keys → Create；首次先初始化通用应用。\nAllow APIs / 允许接口：/happyhorse/videos + /happyhorse/tasks。检查当前权限、余额和价格。\nPaste the API Key in plugin settings only, never in chat. / 只在插件设置填 Key，不在聊天发送密钥。\nAdmin existing-task lookup / 管理员查已有任务：/happyhorse_ace_task <task_id>\nAgent lookup tool / Agent 查询工具：happyhorse_get_task；生成只调用一次，pending 时继续查同一 ID。\nGuide / 指南：https://github.com/AceDataCloud/HappyHorseAstrBot#readme"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("happyhorse_ace_task")
    async def happyhorse_ace_task(self, event: AstrMessageEvent, task_id: str):
        """Let administrators retrieve one existing task without an LLM or generation."""
        try:
            result = await HappyHorseClient(self.config.get("api_key", "")).query(
                task_id
            )
        except HappyHorseError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        yield event.plain_result(json.dumps(result, ensure_ascii=False))
