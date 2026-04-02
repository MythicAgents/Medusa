#!/usr/bin/env python3
import json
import os
import pathlib
import re
import sys


def discover_profiles(base_agent_path: pathlib.Path):
    py2_profiles = {
        re.match(r"transport_(.+)\.py2$", p.name).group(1)
        for p in base_agent_path.glob("transport_*.py2")
        if re.match(r"transport_(.+)\.py2$", p.name)
    }
    py3_profiles = {
        re.match(r"transport_(.+)\.py3$", p.name).group(1)
        for p in base_agent_path.glob("transport_*.py3")
        if re.match(r"transport_(.+)\.py3$", p.name)
    }
    return sorted(py2_profiles.intersection(py3_profiles))


def build_matrix(profiles):
    python_versions = ["Python 2.7", "Python 3.8"]
    crypto_impls = ["manual_crypto", "cryptography_lib"]
    return {
        "include": [
            {
                "profile": profile,
                "python_version": python_version,
                "crypto_impl": crypto_impl,
            }
            for profile in profiles
            for python_version in python_versions
            for crypto_impl in crypto_impls
        ]
    }


def main():
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    base_agent = repo_root / "Payload_Type" / "medusa" / "medusa" / "agent_code" / "base_agent"
    profiles = discover_profiles(base_agent)
    matrix = build_matrix(profiles)
    matrix_json = json.dumps(matrix)

    github_output = os.environ.get("GITHUB_OUTPUT", "").strip()
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"matrix={matrix_json}\n")
    else:
        sys.stdout.write(matrix_json + "\n")


if __name__ == "__main__":
    main()
