#!/usr/bin/env python3
import sys
import json
from collections import Counter
from datetime import datetime, timezone

def hour_from_iso8601_z(s):
    # 转换格式为可读取
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.hour
    except Exception:
        return None

def summarize(path):
    total = 0
    sum_rt = 0.0
    rt_count = 0
    status_counter = Counter()
    hour_counter = Counter()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            total += 1    # 统计总请求数

            rt = rec.get("response_time_ms")
            # 计算总响应时间
            if rt is not None:
                try:
                    sum_rt += float(rt)
                    rt_count += 1
                except Exception:
                    pass

            st = rec.get("http_status")
            # 统计 HTTP 状态码分布
            if st is not None:
                try:
                    status_counter[str(int(st))] += 1
                except Exception:
                    pass

            ts = rec.get("timestamp")
            if ts:
                h = hour_from_iso8601_z(ts)
                if h is not None:
                    # 统计每小时的请求数
                    hour_counter[h] += 1

    # 计算平均响应时间
    avg_rt = (sum_rt / rt_count) if rt_count > 0 else 0.0

    busiest = None
    # 选择最忙的小时，先取最大请求数，并列时选择最小值
    if hour_counter:
        maxc = max(hour_counter.values())
        busiest = min(h for h,c in hour_counter.items() if c == maxc)

    return {
        "total_requests": total,
        "average_response_time_ms": avg_rt,
        "status_code_counts": dict(status_counter),
        "busiest_hour": busiest
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python log_summary.py /path/to/access.log", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    print(json.dumps(summarize(path), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
