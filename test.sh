#!/bin/bash

readonly args=(
  python
  -m
  unittest
  *.py
  "$@"
)

echo "${args[*]}"
"${args[@]}"
