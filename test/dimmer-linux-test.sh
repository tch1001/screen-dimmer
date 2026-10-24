#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
test_dir="$(mktemp -d)"
log_file="$test_dir/xrandr.log"

ln -s "$project_dir/test/mock-xrandr" "$test_dir/xrandr"

MOCK_XRANDR_LOG="$log_file" DISPLAY=:99 XDG_SESSION_TYPE=x11 \
    PATH="$test_dir:/usr/bin:/bin" "$project_dir/dimmer-linux" 70 --output HDMI-1 \
    >"$test_dir/stdout" &
pid=$!

for _ in $(seq 1 50); do
    [[ -s "$log_file" ]] && break
    sleep 0.02
done

kill -TERM "$pid"
status=0
wait "$pid" || status=$?

[[ "$status" == 143 ]]
grep -Fx -- '--output HDMI-1 --brightness 0.30' "$log_file"
grep -Fx -- '--output HDMI-1 --brightness 1.00' "$log_file"
grep -Fq 'Dimmed HDMI-1 to 70% opacity.' "$test_dir/stdout"

echo "dimmer-linux test passed"
