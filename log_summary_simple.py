#!/usr/bin/env python3
import sys
import json
from collections import Counter
from datetime import datetime, timezone

def hour_from_iso8601_z(s):
    try:
        # "2025-08-27T10:15:30Z" -> replace Z with +00:00 then fromisoformat
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        # 转为 UTC，取小时
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.hour
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python log_summary_simple.py /path/to/access.log", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    total_requests = 0
    sum_response = 0.0
    resp_count = 0
    status_counts = Counter()
    hour_counts = Counter()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue  # skip malformed

            total_requests += 1

            # response time
            rt = obj.get("response_time_ms")
            if rt is not None:
                try:
                    rv = float(rt)
                    sum_response += rv
                    resp_count += 1
                except Exception:
                    pass

            # status
            st = obj.get("http_status")
            if st is not None:
                status_counts[str(int(st))] += 1

            # hour
            ts = obj.get("timestamp")
            if ts:
                h = hour_from_iso8601_z(ts)
                if h is not None:
                    hour_counts[h] += 1

    avg_response = (sum_response / resp_count) if resp_count > 0 else 0.0

    busiest_hour = None
    if hour_counts:
        maxc = max(hour_counts.values())
        candidates = [h for h,c in hour_counts.items() if c == maxc]
        busiest_hour = min(candidates)
    # 构造输出
    out = {
        "total_requests": total_requests,
        "average_response_time_ms": avg_response,
        "status_code_counts": dict(status_counts),
        "busiest_hour": busiest_hour
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
