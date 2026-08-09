#!/usr/bin/env python3
"""Run the repository simulation and write its runtime observation log."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SIMULATION_SRC = Path(__file__).resolve().parents[1] / "src"
if str(SIMULATION_SRC) not in sys.path:
    sys.path.insert(0, str(SIMULATION_SRC))

from app.simulation.mrl_runtime_scenario import create_simulation  # noqa: E402
from mrl_simulation_runtime.runner import SimulationRunner  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="write JSONL to this path; stdout by default")
    args = parser.parse_args()

    result = SimulationRunner().run(create_simulation())
    output = "".join(
        json.dumps(observation.to_record(), sort_keys=True) + "\n"
        for observation in result.observations.observations
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    failed_invariants = [
        observation
        for observation in result.observations.observations
        if observation.type == "invariant_result"
        and observation.payload.get("passed") is False
    ]
    if failed_invariants:
        print(
            f"{len(failed_invariants)} simulation invariant(s) failed",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
