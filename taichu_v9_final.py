#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太初V9 智能升级版 - 最终完整版
- 自生长 + 自我构建 + 自创造（熵值驱动范式跃迁）
- 优胜劣汰、自适应阈值、协议交叉、情景记忆、自调整目标
- 外部事件注入 + 事件分类 + 熵值扰动（扰动真正融入熵监控链路）
- 集成云端大模型 API 桥接（CloudLLMBridge）
- 所有已知 bug 已修复
"""
import time
import random
import math
import json
import os
from datetime import datetime
from collections import deque

from cloud_llm_bridge import CloudLLMBridge

try:
    from pan import OllamaBridge
    PAN_AVAILABLE = True
except ImportError:
    PAN_AVAILABLE = False


def histogram(data, bins=10, range_min=0, range_max=1):
    counts = [0] * bins
    width = (range_max - range_min) / bins
    for val in data:
        if val < range_min or val > range_max:
            continue
        idx = int((val - range_min) / width)
        if idx == bins:
            idx = bins - 1
        counts[idx] += 1
    return counts


class EntropyMonitor:
    def __init__(self, window_size=10, base_threshold=0.6):
        self.state_history = deque(maxlen=window_size)
        self.current_entropy = 0.0
        self.base_threshold = base_threshold
        self.entropy_threshold = base_threshold
        self.external_entropy_bias = 0.0

    def update(self, system_state_value):
        self.state_history.append(system_state_value)
        bias = self.external_entropy_bias
        if len(self.state_history) < 2:
            self.current_entropy = min(1.0, 0.0 + bias)
            return self.current_entropy
        diffs = [abs(self.state_history[i] - self.state_history[i - 1])
                 for i in range(1, len(self.state_history))]
        if not diffs:
            self.current_entropy = min(1.0, 0.0 + bias)
            return self.current_entropy
        max_diff = max(diffs) if max(diffs) > 0 else 1
        normalized = [d / max_diff for d in diffs]
        counts = histogram(normalized, bins=10, range_min=0, range_max=1)
        total = sum(counts)
        if total == 0:
            self.current_entropy = min(1.0, 0.0 + bias)
            return self.current_entropy
        probs = [c / total for c in counts if c > 0]
        entropy = -sum(p * math.log(p + 1e-9) for p in probs)
        max_entropy = math.log(10)
        self.current_entropy = min(1.0, entropy / max_entropy + bias)
        return self.current_entropy

    def adjust_threshold(self, health):
        new_threshold = 0.8 - 0.4 * health
        self.entropy_threshold = max(0.4, min(0.8, new_threshold))
        return self.entropy_threshold

    def should_transition(self):
        return self.current_entropy >= self.entropy_threshold


class Protocol:
    def __init__(self, name, code, performance_score=0.5):
        self.name = name
        self.code = code
        self.performance = performance_score
        self.usage_count = 0

    def execute(self, input_data):
        try:
            result = self.code(input_data)
            self.usage_count += 1
            return result
        except Exception as e:
            print(f"[协议 {self.name}] 执行失败: {e}")
            self.performance = max(0.0, self.performance - 0.1)
            return None


class ParadigmManager:
    def __init__(self, max_protocols=20, min_performance=0.2):
        self.protocols = {}
        self.current_protocol_name = None
        self.max_protocols = max_protocols
        self.min_performance = min_performance

    def register_protocol(self, protocol):
        self.protocols[protocol.name] = protocol
        if self.current_protocol_name is None:
            self.current_protocol_name = protocol.name

    def select_best_protocol(self):
        if not self.protocols:
            return None
        best = max(self.protocols.values(), key=lambda p: p.performance)
        self.current_protocol_name = best.name
        return best

    def get_current_protocol(self):
        return self.protocols.get(self.current_protocol_name)

    def update_performance(self, protocol_name, delta):
        if protocol_name in self.protocols:
            new_score = self.protocols[protocol_name].performance + delta
            self.protocols[protocol_name].performance = max(0.0, min(1.0, new_score))

    def list_protocols(self):
        return {name: p.performance for name, p in self.protocols.items()}

    def cull_protocols(self):
        if len(self.protocols) <= self.max_protocols:
            return
        sorted_items = sorted(self.protocols.items(), key=lambda x: x[1].performance, reverse=True)
        to_keep = dict(sorted_items[:self.max_protocols])
        if self.current_protocol_name not in to_keep:
            self.current_protocol_name = next(iter(to_keep.keys())) if to_keep else None
        self.protocols = to_keep


class ExperienceMemory:
    def __init__(self, num_buckets=10):
        self.memory = {}
        self.num_buckets = num_buckets

    def _bucket(self, entropy):
        return min(self.num_buckets - 1, int(entropy * self.num_buckets))

    def update(self, entropy, proto_name, performance):
        bucket = self._bucket(entropy)
        if bucket not in self.memory:
            self.memory[bucket] = {}
        if proto_name not in self.memory[bucket]:
            self.memory[bucket][proto_name] = [0.0, 0]
        self.memory[bucket][proto_name][0] += performance
        self.memory[bucket][proto_name][1] += 1

    def recommend(self, entropy):
        bucket = self._bucket(entropy)
        if bucket not in self.memory:
            return None
        best_proto = None
        best_avg = -1.0
        for proto, (total, cnt) in self.memory[bucket].items():
            avg = total / cnt if cnt > 0 else 0
            if avg > best_avg:
                best_avg = avg
                best_proto = proto
        return best_proto

    def get_stats(self):
        return {
            b: {p: f"{total / cnt:.3f}" for p, (total, cnt) in data.items()}
            for b, data in self.memory.items()
        }


class SelfCreationModule:
    def __init__(self, paradigm_manager, entropy_monitor, experience_memory):
        self.pm = paradigm_manager
        self.em = entropy_monitor
        self.exp_mem = experience_memory
        self.generation_counter = 0
        self.mutation_rate = 0.3
        self.crossover_rate = 0.4

    def create_new_paradigm(self, trigger_reason="entropy_exceed"):
        self.generation_counter += 1
        current_best = self.pm.select_best_protocol()
        if not current_best:
            default_code = lambda x: x * 0.5
            new_proto = Protocol("DefaultProto", default_code, 0.5)
            self.pm.register_protocol(new_proto)
            return new_proto
        use_crossover = (random.random() < self.crossover_rate and
                         len(self.pm.protocols) >= 2)
        if use_crossover:
            sorted_protos = sorted(self.pm.protocols.values(), key=lambda p: p.performance, reverse=True)
            top_candidates = sorted_protos[:min(3, len(sorted_protos))]
            if len(top_candidates) >= 2:
                parent_a, parent_b = random.sample(top_candidates, 2)
                new_proto = self._crossover(parent_a, parent_b)
            else:
                new_proto = self._mutate(current_best)
        else:
            new_proto = self._mutate(current_best)
        self.pm.register_protocol(new_proto)
        self._log_creation(new_proto.name, trigger_reason)
        return new_proto

    def _mutate(self, parent_proto):
        base_name = parent_proto.name
        new_name = f"Evo_{base_name}_v{self.generation_counter}"
        original_code = parent_proto.code
        gen = self.generation_counter

        def variant_code(x):
            orig = original_code(x)
            variant = orig + 0.1 * math.sin(x * gen) + random.uniform(-0.05, 0.05)
            return max(0.0, min(1.0, variant))

        init_perf = max(0.05, parent_proto.performance - 0.1)
        return Protocol(new_name, variant_code, init_perf)

    def _crossover(self, proto_a, proto_b):
        new_name = f"Cross_{proto_a.name}_{proto_b.name}_v{self.generation_counter}"
        code_a = proto_a.code
        code_b = proto_b.code
        if proto_a.performance > proto_b.performance:
            weight_a = 0.7
        elif proto_b.performance > proto_a.performance:
            weight_a = 0.3
        else:
            weight_a = 0.5

        def hybrid_code(x):
            result = weight_a * code_a(x) + (1 - weight_a) * code_b(x)
            return max(0.0, min(1.0, result))

        init_perf = (proto_a.performance + proto_b.performance) / 2 - 0.05
        init_perf = max(0.05, init_perf)
        return Protocol(new_name, hybrid_code, init_perf)

    def _log_creation(self, protocol_name, reason):
        try:
            with open("taichu_creations.log", "a") as f:
                f.write(f"{datetime.now()} | CREATE | {protocol_name} | reason={reason}\n")
        except Exception:
            pass
        print(f"[自创造] 新范式生成: {protocol_name} (原因: {reason})")


class FEMDAKernel:
    def __init__(self, target_range=(0.3, 0.95), adaptation_rate=0.05):
        self.performance_history = deque(maxlen=20)
        self.error_history = deque(maxlen=10)
        self.stability_score = 1.0
        self.target_value = 0.7
        self.target_range = target_range
        self.adaptation_rate = adaptation_rate

    def collect_metrics(self, protocol, execution_result, target_value=None):
        if target_value is None:
            target_value = self.target_value
        if execution_result is not None:
            error = abs(execution_result - target_value)
            self.error_history.append(error)
            perf_delta = max(-0.2, min(0.2, 0.2 - error * 0.5))
            self.performance_history.append(perf_delta)
            return perf_delta
        else:
            return random.uniform(-0.05, 0.05)

    def update_stability(self, entropy_value):
        self.stability_score = max(0.0, min(1.0, 1.0 - entropy_value))
        return self.stability_score

    def get_overall_health(self):
        avg_perf = sum(self.performance_history) / len(self.performance_history) if self.performance_history else 0.5
        clamped_perf = max(0.0, min(1.0, avg_perf + 0.5))
        health = 0.6 * self.stability_score + 0.4 * clamped_perf
        return max(0.0, min(1.0, health))

    def adjust_target(self):
        if len(self.error_history) < 5:
            return self.target_value
        avg_error = sum(self.error_history) / len(self.error_history)
        if avg_error < 0.05:
            new_target = self.target_value + self.adaptation_rate
        elif avg_error > 0.2:
            new_target = self.target_value - self.adaptation_rate
        else:
            new_target = self.target_value
        self.target_value = max(self.target_range[0], min(self.target_range[1], new_target))
        return self.target_value


class TaichuCore:
    """太初V9 主内核 - 供 Kivy GUI 通过 step() 逐帧驱动"""

    def __init__(self):
        self.entropy_monitor = EntropyMonitor(window_size=8, base_threshold=0.6)
        self.paradigm_manager = ParadigmManager(max_protocols=20, min_performance=0.2)
        self.experience_memory = ExperienceMemory(num_buckets=10)
        self.creation_module = SelfCreationModule(
            self.paradigm_manager,
            self.entropy_monitor,
            self.experience_memory,
        )
        self.femda = FEMDAKernel(target_range=(0.3, 0.95), adaptation_rate=0.03)

        # 云端大模型 API 桥接（密钥运行时填写，不硬编码）
        self.cloud_bridge = CloudLLMBridge(config_path="./cloud_config.json")

        # Ollama 本地桥接（可选）
        self.ollama = None
        self.ollama_available = False
        if PAN_AVAILABLE:
            self.ollama = OllamaBridge(model="qwen2:7b")
            self.ollama_available = self.ollama.is_available()

        self.iteration = 0
        self.system_state = 0.5
        self.last_cull_iteration = 0
        self.external_events = []
        self.accumulated_disturbance = 0.0
        self._init_base_protocols()

    def _init_base_protocols(self):
        proto1 = Protocol("Conservative", lambda x: x * 0.3, 0.6)
        proto2 = Protocol("Aggressive", lambda x: min(1.0, x * 1.5), 0.4)
        proto3 = Protocol("Balanced", lambda x: x * 0.8 + 0.1, 0.7)
        self.paradigm_manager.register_protocol(proto1)
        self.paradigm_manager.register_protocol(proto2)
        self.paradigm_manager.register_protocol(proto3)
        self.paradigm_manager.select_best_protocol()

    def _classify_event(self, content):
        c = content.lower()
        alert_kw = ["警告", "告警", "危险", "异常", "错误", "失败", "崩溃",
                     "alert", "warning", "error", "danger", "crash"]
        command_kw = ["执行", "强制", "立即", "创造", "演化", "跃迁", "重启",
                      "指令", "command", "execute", "force", "evolve"]
        query_kw = ["?", "？", "什么", "怎么", "为什么", "如何", "查询", "状态",
                    "what", "how", "why", "status"]
        for kw in alert_kw:
            if kw in c:
                return "alert"
        for kw in command_kw:
            if kw in c:
                return "command"
        for kw in query_kw:
            if kw in c:
                return "query"
        return "normal"

    def _apply_external_disturbance(self, entropy):
        round_disturb = 0.0
        for evt in self.external_events:
            if not evt.get("consumed", False):
                evt_type = evt.get("type", "normal")
                base = {"normal": 0.05, "alert": 0.15, "command": 0.25, "query": 0.08}.get(evt_type, 0.05)
                length_factor = min(len(evt["content"]) / 300, 0.2)
                disturb = base + length_factor
                round_disturb += disturb
                evt["consumed"] = True
                evt["disturbance"] = disturb
                if evt_type == "command":
                    self.creation_module.create_new_paradigm(trigger_reason="external_command")
                    self.paradigm_manager.select_best_protocol()

        self.accumulated_disturbance = max(0.0, self.accumulated_disturbance - 0.03)
        self.accumulated_disturbance += round_disturb
        self.entropy_monitor.external_entropy_bias = self.accumulated_disturbance
        final_entropy = min(1.0, entropy + self.accumulated_disturbance)
        return final_entropy

    def compute_system_state(self):
        noise = random.uniform(-0.1, 0.1)
        self.system_state = max(0.0, min(1.0, self.system_state + noise))
        periodic = 0.1 * math.sin(self.iteration * 0.1)
        return max(0.0, min(1.0, self.system_state + periodic))

    def step(self):
        """执行一轮演化，返回日志字符串列表（供 GUI 显示）"""
        logs = []
        self.iteration += 1
        current_state = self.compute_system_state()
        entropy = self.entropy_monitor.update(current_state)
        entropy = self._apply_external_disturbance(entropy)

        temp_health = self.femda.get_overall_health()
        self.entropy_monitor.adjust_threshold(temp_health)

        recommended = self.experience_memory.recommend(entropy)
        current_proto = self.paradigm_manager.get_current_protocol()
        if recommended and recommended != self.paradigm_manager.current_protocol_name:
            rec_proto = self.paradigm_manager.protocols.get(recommended)
            current_perf = current_proto.performance if current_proto else 0
            if rec_proto and rec_proto.performance > current_perf:
                self.paradigm_manager.current_protocol_name = recommended
                logs.append(f"[记忆推荐] 切换到 {recommended}")

        if self.entropy_monitor.should_transition():
            logs.append(f"[跃迁触发] 熵值={entropy:.3f} >= {self.entropy_monitor.entropy_threshold:.3f}")
            self.creation_module.create_new_paradigm(trigger_reason="high_entropy")
            self.paradigm_manager.select_best_protocol()

        current_proto = self.paradigm_manager.get_current_protocol()
        if not current_proto:
            current_proto = self.paradigm_manager.select_best_protocol()

        output = None
        if current_proto:
            output = current_proto.execute(current_state)
            target = self.femda.target_value
            perf_delta = self.femda.collect_metrics(current_proto, output, target)
            self.paradigm_manager.update_performance(current_proto.name, perf_delta)
            self.experience_memory.update(entropy, current_proto.name, current_proto.performance)

        self.femda.update_stability(entropy)
        health = self.femda.get_overall_health()
        new_target = self.femda.adjust_target()

        if self.iteration - self.last_cull_iteration >= 10:
            self.paradigm_manager.cull_protocols()
            self.last_cull_iteration = self.iteration

        if health < 0.3:
            logs.append("[紧急] 健康度过低，强制创造新范式")
            self.creation_module.create_new_paradigm(trigger_reason="low_health")
            self.paradigm_manager.select_best_protocol()

        proto_name = current_proto.name if current_proto else "None"
        log_line = (
            f"Iter={self.iteration:4d} | Entropy={entropy:.3f} | "
            f"Active={proto_name[:18]:18s} | Health={health:.3f} | "
            f"Target={new_target:.3f} | Protocols={len(self.paradigm_manager.protocols)} | "
            f"Disturb={self.accumulated_disturbance:.3f}"
        )
        logs.append(log_line)
        return logs

    def inject_external_event(self, content):
        """外部注入事件（供 GUI 调用）"""
        evt_type = self._classify_event(content)
        evt_item = {
            "ts": time.time(),
            "content": content,
            "type": evt_type,
            "consumed": False,
        }
        self.external_events.append(evt_item)
        return evt_type

    def call_cloud_llm(self, prompt, system_prompt="", callback=None):
        """异步调用云端大模型，结果通过 callback 返回"""
        if not self.cloud_bridge.enabled:
            if callback:
                callback({"ok": False, "msg": "云端API未启用", "content": ""})
            return
        self.cloud_bridge.call_llm_async(prompt, system_prompt, callback)
