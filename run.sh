#!/usr/bin/env bash

# 默认读取 access.log，或使用第一个参数作为日志文件
LOG="${1:-access.log}"

if [ ! -f "$LOG" ]; then
  echo "日志文件不存在: $LOG" >&2
  exit 1
fi

python log_summarysimple.py "$LOG"
