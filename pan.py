#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pan.py - Ollama 本地推理桥接模块
纯标准库实现（urllib），不依赖 requests
"""
import json
import urllib.request


class OllamaBridge:
    def __init__(self, base_url="http://127.0.0.1:11434", model="qwen2:7b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self):
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_models(self):
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def generate(self, prompt, model=None, temperature=0.7, max_tokens=512):
        if model is None:
            model = self.model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode())
                return result.get("response", "").strip()
        except Exception as e:
            return f"[Ollama异常] {e}"

    def chat(self, messages, model=None, temperature=0.7, max_tokens=512):
        if model is None:
            model = self.model
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode())
                return result.get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"[Ollama对话异常] {e}"
