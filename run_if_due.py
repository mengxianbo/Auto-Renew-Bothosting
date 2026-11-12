
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 续期间隔：30小时
INTERVAL = timedelta(hours=30)

# 上次成功执行时间
STATE_FILE = Path("last_run.txt")


def main():
    now = datetime.now(timezone.utc)

    print("================================")
    print(" Bot-hosting 30小时自动续期监控")
    print("================================")
    print("当前UTC时间:", now.isoformat())

    # 检查历史执行记录
    if STATE_FILE.exists():
        try:
            last_run = datetime.fromisoformat(
                STATE_FILE.read_text().strip()
            )

            if last_run.tzinfo is None:
                last_run = last_run.replace(
                    tzinfo=timezone.utc
                )

        except Exception as e:
            print("读取历史时间失败:", e)
            sys.exit(1)

        elapsed = now - last_run

        print("上次成功时间:", last_run.isoformat())
        print(
            "已经过去:",
            round(elapsed.total_seconds() / 3600, 2),
            "小时"
        )

        if elapsed < INTERVAL:
            remaining = INTERVAL - elapsed

            print(
                "距离下次续期还需:",
                round(remaining.total_seconds() / 3600, 2),
                "小时"
            )

            print("未达到30小时，跳过本次续期。")
            return

    else:
        print("没有历史记录，首次运行，立即续期。")

    # 执行原有 app.py
    print("开始执行 Bot-hosting 续期程序...")

    result = subprocess.run([
        "xvfb-run",
        "--auto-servernum",
        "python3",
        "app.py"
    ])

    if result.returncode != 0:
        print("续期程序执行失败！")
        print("保留原有时间记录，等待下次重试。")
        sys.exit(result.returncode)

    # 续期脚本成功后才更新时间
    success_time = datetime.now(timezone.utc)

    STATE_FILE.write_text(
        success_time.isoformat() + "\n"
    )

    print("续期程序执行成功！")
    print("新的成功执行时间:", success_time.isoformat())


if __name__ == "__main__":
    main()
