#!/bin/bash

readonly pyflakes_args=(
  pyflakes
  *.py
  "$@"
)

echo "${pyflakes_args[*]}"
"${pyflakes_args[@]}"
