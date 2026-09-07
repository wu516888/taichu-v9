#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太初V9 Android 主入口（Kivy GUI）
- 启动/停止太初自演化内核
- 实时显示运行日志
- 外部事件注入（扰动内部熵值）
- 云端大模型 API 配置面板（密钥本地保存，不硬编码）
- 状态面板：迭代数 / 熵值 / 健康度 / 协议数 / 扰动值
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock, mainthread
from kivy.core.window import Window

from taichu_v9_final import TaichuCore


class LogView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)

    @mainthread
    def add_log(self, text):
        lab = Label(text=text, size_hint_y=None, height=28, font_size='11sp')
        self.layout.add_widget(lab)
        if len(self.layout.children) > 300:
            self.layout.remove_widget(self.layout.children[-1])
        self.scroll_y = 0


class MainRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 6
        self.padding = 8

        self.core = TaichuCore()
        self.cloud_bridge = self.core.cloud_bridge
        self.running = False
        self.core_tick = None

        # ===== 标题 =====
        self.title = Label(
            text='太初 V9 · 自生长智能内核',
            size_hint_y=0.05,
            font_size='18sp',
            bold=True,
        )
        self.add_widget(self.title)

        # ===== 状态面板 =====
        self.status_label = Label(
            text='状态：未启动',
            size_hint_y=0.10,
            font_size='12sp',
            markup=True,
        )
        self.add_widget(self.status_label)

        # ===== 云端API配置面板 =====
        cfg_box = BoxLayout(orientation="vertical", size_hint_y=None, height=170, spacing=3)
        cfg_title = Label(text="云端API配置（运行时填写，密钥保存在手机本地）",
                          size_hint_y=None, height=22, font_size='11sp')
        cfg_box.add_widget(cfg_title)

        self.api_base_input = TextInput(
            hint_text="API BaseUrl  例: https://api.deepseek.com/v1",
            size_hint_y=None, height=36, font_size='12sp', multiline=False,
        )
        cfg_box.add_widget(self.api_base_input)

        self.api_key_input = TextInput(
            hint_text="API Key",
            size_hint_y=None, height=36, font_size='12sp', multiline=False, password=True,
        )
        cfg_box.add_widget(self.api_key_input)

        self.api_model_input = TextInput(
            hint_text="模型名  例: deepseek-chat",
            size_hint_y=None, height=36, font_size='12sp', multiline=False,
        )
        cfg_box.add_widget(self.api_model_input)

        btn_save_cfg = Button(text="保存云端API配置", size_hint_y=None, height=38, font_size='13sp')
        btn_save_cfg.bind(on_press=self.save_cloud_config)
        cfg_box.add_widget(btn_save_cfg)
        self.add_widget(cfg_box)

        # ===== 事件输入 =====
        self.event_input = TextInput(
            hint_text='输入外部事件（如：执行强制演化 / 警告系统异常），点【注入事件】送入内核',
            size_hint_y=None, height=60, font_size='12sp',
        )
        self.add_widget(self.event_input)

        # ===== 功能按钮 =====
        btn_box = BoxLayout(spacing=6, size_hint_y=None, height=44)
        self.btn_start = Button(text="启动太初", font_size='14sp')
        self.btn_start.bind(on_press=self.start_core)
        btn_box.add_widget(self.btn_start)

        self.btn_stop = Button(text="停止", font_size='14sp', disabled=True)
        self.btn_stop.bind(on_press=self.stop_core)
        btn_box.add_widget(self.btn_stop)

        self.btn_inject = Button(text="注入事件", font_size='14sp')
        self.btn_inject.bind(on_press=self.inject_event)
        btn_box.add_widget(self.btn_inject)
        self.add_widget(btn_box)

        # ===== 日志区 =====
        self.log_view = LogView(size_hint_y=0.55)
        self.add_widget(self.log_view)

        # 定时刷新状态面板
        Clock.schedule_interval(self.refresh_status, 0.5)

    def append_log(self, txt):
        self.log_view.add_log(txt)

    def save_cloud_config(self, inst):
        base = self.api_base_input.text.strip()
        key = self.api_key_input.text.strip()
        model = self.api_model_input.text.strip()
        enabled = self.cloud_bridge.save_config(api_key=key, base_url=base, model_name=model)
        self.append_log(f"[API配置] 已保存，启用状态: {enabled}")

    def start_core(self, inst):
        if self.running:
            self.append_log("[系统] 内核已经在运行")
            return
        self.running = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.append_log("[系统] 太初V9内核启动")
        self.append_log(f"[系统] 云端API: {'已启用' if self.cloud_bridge.enabled else '未启用（纯内核模式）'}")
        self.core_tick = Clock.schedule_interval(self.core_loop_tick, 0.8)

    def stop_core(self, inst):
        if not self.running:
            return
        self.running = False
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        if self.core_tick:
            self.core_tick.cancel()
        self.append_log("[系统] 太初内核已停止")

    def core_loop_tick(self, dt):
        try:
            log_items = self.core.step()
            for line in log_items:
                self.append_log(line)
        except Exception as e:
            self.append_log(f"[内核异常] {e}")

    def inject_event(self, inst):
        content = self.event_input.text.strip()
        if not content:
            self.append_log("[警告] 事件内容为空")
            return
        evt_type = self.core.inject_external_event(content)
        self.append_log(f"[注入事件] 类型={evt_type} | {content[:50]}")
        self.event_input.text = ""

    def refresh_status(self, dt):
        if self.core and self.running:
            s = self.core
            proto_name = s.paradigm_manager.current_protocol_name or "None"
            self.status_label.text = (
                f"[b]状态：运行中[/b]\n"
                f"迭代={s.iteration} | 熵值={s.entropy_monitor.current_entropy:.3f} | "
                f"健康={s.femda.get_overall_health():.3f}\n"
                f"协议={len(s.paradigm_manager.protocols)} | "
                f"当前={proto_name[:14]} | 扰动={s.accumulated_disturbance:.3f}"
            )
        elif not self.running:
            self.status_label.text = "状态：未启动"


class TaichuApp(App):
    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.12, 1)
        self.title = "太初 V9"
        return MainRoot()

    def on_stop(self):
        if self.root and self.root.core:
            self.root.stop_core(None)


if __name__ == "__main__":
    TaichuApp().run()
