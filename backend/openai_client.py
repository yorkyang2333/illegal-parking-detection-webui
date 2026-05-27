"""
统一 OpenAI 兼容 API 客户端
通过 newapi 网关代理调用各种模型供应商，使用 OpenAI Chat Completions 格式。
"""

import json
import requests


class OpenAIClient:
    """OpenAI 兼容 API 客户端，支持流式对话、视觉识别、工具调用和模型列表。"""

    def __init__(self, base_url: str = "", api_key: str = "", default_model: str = ""):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.api_key = api_key or ""
        self.default_model = default_model or ""

    def update_config(self, base_url: str = None, api_key: str = None, default_model: str = None):
        """运行时动态更新配置"""
        if base_url is not None:
            self.base_url = base_url.rstrip("/")
        if api_key is not None:
            self.api_key = api_key
        if default_model is not None:
            self.default_model = default_model

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _check_config(self):
        if not self.base_url:
            raise ValueError("API Base URL 未配置，请在设置中填写供应商地址。")
        if not self.api_key:
            raise ValueError("API Key 未配置，请在设置中填写 API Key。")

    def _resolve_model(self, model: str = None) -> str:
        resolved = model or self.default_model
        if not resolved:
            raise ValueError("未指定模型，请在设置中配置默认模型或在请求中指定模型。")
        return resolved

    # ── 流式对话 ────────────────────────────────────────────────────

    def chat_stream(self, messages: list, model: str = None):
        """
        流式对话，返回生成器，每次 yield 一段文本 chunk。
        messages 格式同 OpenAI: [{"role": "user", "content": "..."}]
        """
        self._check_config()
        resolved_model = self._resolve_model(model)

        payload = {
            "model": resolved_model,
            "messages": messages,
            "stream": True,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            resp = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                stream=True,
                timeout=120,
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"无法连接到 API 服务器: {self.base_url}")
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时，请检查网络连接。")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 401:
                raise PermissionError("API Key 无效或已过期，请检查设置。")
            elif status == 404:
                raise ValueError(f"模型 {resolved_model} 不可用或 API 路径错误。")
            elif status == 429:
                raise RuntimeError("API 请求频率超限，请稍后再试。")
            else:
                raise RuntimeError(f"API 请求失败 (HTTP {status}): {e}")

        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue

    # ── 非流式对话 ──────────────────────────────────────────────────

    def chat(self, messages: list, model: str = None) -> str:
        """非流式对话，返回完整响应文本。"""
        self._check_config()
        resolved_model = self._resolve_model(model)

        payload = {
            "model": resolved_model,
            "messages": messages,
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            resp = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"无法连接到 API 服务器: {self.base_url}")
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时。")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            raise RuntimeError(f"API 请求失败 (HTTP {status})")

    # ── 工具调用 ────────────────────────────────────────────────────

    def chat_with_tools(self, messages: list, tools: list, model: str = None) -> dict:
        """
        带工具调用的对话（非流式）。
        返回 OpenAI 格式的完整响应 dict，包含 choices[0].message.tool_calls 等。
        """
        self._check_config()
        resolved_model = self._resolve_model(model)

        payload = {
            "model": resolved_model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            resp = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"无法连接到 API 服务器: {self.base_url}")
        except requests.exceptions.Timeout:
            raise TimeoutError("API 请求超时。")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            raise RuntimeError(f"API 请求失败 (HTTP {status})")

    # ── 视觉对话 ────────────────────────────────────────────────────

    def vision_chat(self, messages: list, model: str = None) -> str:
        """
        视觉模型对话（非流式）。
        messages 中的 content 使用 OpenAI Vision 格式:
        [
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
            {"type": "text", "text": "请识别..."}
        ]
        """
        return self.chat(messages, model=model)

    # ── 模型列表 ────────────────────────────────────────────────────

    def list_models(self) -> list:
        """获取可用模型列表，返回 [{"id": "...", "owned_by": "..."}]"""
        self._check_config()

        url = f"{self.base_url}/models"
        try:
            resp = requests.get(
                url,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            # OpenAI 格式: {"data": [{"id": "...", "owned_by": "..."}]}
            models = data.get("data", [])
            return [
                {"id": m.get("id", ""), "owned_by": m.get("owned_by", "")}
                for m in models
                if m.get("id")
            ]
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"无法连接到 API 服务器: {self.base_url}")
        except requests.exceptions.Timeout:
            raise TimeoutError("获取模型列表超时。")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            if status == 401:
                raise PermissionError("API Key 无效，无法获取模型列表。")
            raise RuntimeError(f"获取模型列表失败 (HTTP {status})")
