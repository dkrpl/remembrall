#!/usr/bin/env bash
# Remembrall Handoff Sub-Skill Runner (Matt Pocock & Superpowers Spine)
# Extracts in-progress WIP tasks, state budget, and key findings for next session.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
bash "$DIR/scripts/handoff.sh"
