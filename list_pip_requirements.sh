#!/bin/bash
pip list --not-required -l --format freeze  2>/dev/null | grep -ve '^wheel==' \
    | grep -ve '^pip==' | grep -ve '^pkg-resources==' | grep -ve '^pylint=='
