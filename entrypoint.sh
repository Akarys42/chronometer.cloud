#!/usr/bin/env bash
set -e

if [ -v USE_RELOADER ]; then
  extra_args=--reload
fi

uvicorn app.main:app --host 0.0.0.0 $extra_args
