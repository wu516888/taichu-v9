#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_llm_bridge.py - 云端大模型 API 桥接
兼容 OpenAI 格式接口：DeepSeek、千问、OpenRouter、智谱等
密钥不硬编码，运行时由 GUI 填写并保存到本地 json
"""
import json
import threading

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CloudLLMBridge:
    def __init__(self, config_path="./cloud_config.json"):
        self.config_path = config_path
        self.api_key = ""
        self.base_url = ""
        self.model_name = ""
        self.timeout = 45
        self.enabled = False
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.api_key = cfg.get("api_key", "")
            self.base_url = cfg.get("base_url", "")
            self.model_name = cfg.get("model_name", "")
            self.enabled = bool(self.api_key and self.base_url)
        except Exception:
            self.enabled = False

    def save_config(self, api_key, base_url, model_name):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model_name = model_name.strip()
        cfg = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model_name": self.model_name,
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        self.enabled = bool(self.api_key and self.base_url)
        return self.enabled

    def call_llm_sync(self, prompt, system_prompt=""):
        """同步调用，必须在子线程中执行，禁止 UI 主线程调用"""
        if not self.enabled:
            return {"ok": False, "msg": "云端API未启用，请先填写密钥和接口地址", "content": ""}
        if not REQUESTS_AVAILABLE:
            return {"ok": False, "msg": "requests库未安装", "content": ""}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"ok": True, "content": content, "msg": "success"}
        except Exception as e:
            return {"ok": False, "msg": str(e), "content": ""}

    def call_llm_async(self, prompt, system_prompt, callback):
        """异步子线程调用，回调函数接收结果字典"""
        def worker():
            res = self.call_llm_sync(prompt, system_prompt)
            if callback:
                callback(res)
        t = threading.Thread(target=worker, daemon=True)
        t.start()
