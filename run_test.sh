#!/usr/bin/env bash
# Run tests for the app (simple e2e)
python -u app.py &
APP_PID=$!
sleep 2
pytest -q
TEST_EXIT=$?
kill $APP_PID
exit $TEST_EXIT
