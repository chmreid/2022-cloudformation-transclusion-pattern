#!/usr/bin/env bash
set -eux

echo "{}" | npx mustache - ssm-automation-block-ip.yml.mustache -p block_ip.py > ssm-automation-block-ip.yml
