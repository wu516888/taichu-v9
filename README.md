# 太初 V9 · Android 版

自生长智能内核，熵值驱动范式跃迁，外部事件可扰动内部演化，支持云端大模型 API 接入。

## 功能

- **自演化内核**：熵值监控 → 范式跃迁 → 协议变异/交叉 → 优胜劣汰 → 情景记忆 → 自适应目标
- **外部事件扰动**：注入消息 → 自动分类（normal/alert/command/query）→ 叠加熵值偏移 → 改变演化走向
- **指令型事件**：含"执行/强制/演化/跃迁"等关键词，直接触发热创造新范式
- **云端大模型 API**：兼容 OpenAI 格式（DeepSeek、千问、OpenRouter、智谱等），密钥运行时填写，本地保存
- **Kivy GUI**：启动/停止、实时日志、事件注入、状态面板、API 配置
- **三种运行模式**：纯内核离线 / Ollama 本地推理 / 云端 API 增强

## 文件结构

```
taichu_final/
├── main.py                     # Kivy GUI 入口（Android 启动页）
├── taichu_v9_final.py          # 太初内核（所有 bug 已修复）
├── pan.py                      # Ollama 本地桥接
├── cloud_llm_bridge.py         # 云端大模型 API 桥接
├── buildozer.spec              # Buildozer APK 打包配置
├── requirements.txt            # Python 依赖
├── .github/workflows/build.yml # GitHub Actions 云端编译
└── README.md
```

## 一键云端编译成 APK

### 第一步：创建 GitHub 仓库

1. 注册/登录 [GitHub](https://github.com)
2. 点右上角 `+` → `New repository`
3. 仓库名随便填（如 `taichu-v9-android`），选 Public，点 Create

### 第二步：上传所有文件

把本目录下的**全部文件**（包括 `.github` 文件夹）上传到仓库：

- 网页上传：仓库页面点 `Add file` → `Upload files`，拖入所有文件，点 `Commit changes`
- 命令行：
  ```bash
  git init
  git add .
  git commit -m "太初V9 Android 初始版本"
  git branch -M main
  git remote add origin https://github.com/你的用户名/仓库名.git
  git push -u origin main
  ```

### 第三步：等云端编译

- 上传后自动开始编译，点仓库顶部 `Actions` 标签看进度
- 第一次编译约 15-30 分钟（Buildozer 下载 Android SDK/NDK）
- 状态变成绿色 ✓ 即编译成功

### 第四步：下载安装

1. 点进那次绿色的构建记录
2. 页面最下方 `Artifacts` → 点 `taichu-v9-apk` 下载
3. 解压得到 `.apk`，传到手机点击安装（允许未知来源）

## 使用说明

1. 安装后打开 App
2. （可选）在云端API配置面板填写：接口地址、API Key、模型名，点「保存云端API配置」
   - DeepSeek 示例：BaseUrl=`https://api.deepseek.com/v1`，模型=`deepseek-chat`
   - 千问示例：BaseUrl=`https://dashscope.aliyuncs.com/compatible-mode/v1`，模型=`qwen-turbo`
   - 不填则纯内核离线运行
3. 点「启动太初」，内核开始自演化，日志区实时滚动
4. 在输入框输入外部事件，点「注入事件」：
   - 普通文本 → 低扰动
   - 含"警告/异常/错误" → 中扰动
   - 含"执行/强制/演化/跃迁" → 高扰动 + 强制创造新范式
5. 状态面板实时显示：迭代数 / 熵值 / 健康度 / 协议数 / 当前协议 / 扰动值
6. 点「停止」结束运行

## 安全说明

- **API Key 不硬编码**：不在源码中，运行时在手机界面填写，保存到手机本地 `cloud_config.json`
- **`cloud_config.json` 不要上传 GitHub**：这个文件是手机运行后才生成的，包含你的密钥
- 知识库/记忆数据全程保留手机本地，只有调用云端 API 时才把 prompt 发出去

## 已修复的 Bug

1. `ExperienceMemory.recommend()` 中 `best_proto` 未初始化，空记忆桶时崩溃 → 已加 `best_proto = None`
2. `SelfCreationModule._mutate()` 中 `init_perf` 括号不完整 → 已修复
3. 外部事件扰动只改临时变量，下一轮熵计算被覆盖 → 扰动写入 `entropy_monitor.external_entropy_bias`，每轮叠加
4. `buildozer.spec` 中 `source.exclude_dirs` 排除了 `.github` 导致 Actions 失效 → 已移除
5. `requirements` 缺少 `requests` 导致云端 API 无法打包 → 已添加

## 技术栈

- Python 3 + Kivy（GUI）
- Flask（内置 HTTP API，可选）
- requests（云端 API 调用）
- Buildozer（打包 Android APK）
- GitHub Actions（云端编译）
