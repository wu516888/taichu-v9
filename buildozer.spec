[app]

# (str) 应用标题
title = 太初V9

# (str) 应用包名
package.name = taichuv9

# (str) 包域名（反向）
package.domain = org.taichu

# (str) 源代码目录（包含 main.py）
source.dir = .

# (list) 包含的源文件
source.include_exts = py,png,jpg,kv,atlas,json

# (list) 排除的文件/目录（注意：不要排除 .github，否则 Actions 工作流失效）
source.exclude_dirs = tests, bin, .git

# (list) 应用依赖的 Python 包（requests 用于云端 API）
requirements = python3,kivy==2.3.0,flask==3.0.0,requests

# (str) 应用版本
version = 1.0.0

# (list) 应用需要的 Android 权限
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) 最低 Android API 级别
android.minapi = 21

# (int) 目标 Android API 级别
android.api = 33

# (str) Android NDK 版本
android.ndk = 25b

# (list) 支持的 CPU 架构
android.archs = arm64-v8a, armeabi-v7a

# (bool) 是否启用 AndroidX
android.enable_androidx = True

# (str) 应用入口模块
entrypoint = main

# (bool) 全屏模式
fullscreen = 0

# (str) 应用方向
orientation = portrait

# (int) 日志级别
log_level = 2

# (bool) 允许备份
android.allow_backup = True

[buildozer]

# (int) 日志级别
log_level = 2

# (int) 警告级别
warn_on_root = 1

# (str) Buildozer 工作目录
build_dir = .buildozer

# (str) 二进制输出目录
bin_dir = bin
