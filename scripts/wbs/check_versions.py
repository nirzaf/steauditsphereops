#!/usr/bin/env python3
"""Validate pinned toolchain metadata without downloading or executing code."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path


REPOSITORIES = {"frappe", "erpnext", "bench"}
IMAGES = {"frappe/erpnext", "python", "node", "mariadb", "redis"}
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
SEMVER_REF = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
FLOATING = {"latest", "develop", "main", "master", "head", "*"}


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if data.get("schema") != "steauditsphereops/production-versions@1":
        errors.append("schema must be steauditsphereops/production-versions@1")
    if not isinstance(data.get("version"), str) or not data["version"]:
        errors.append("version must be a non-empty string")
    support = data.get("support_basis")
    if not isinstance(support, dict) or not all(isinstance(support.get(key), str) and support[key] for key in ("documentation", "framework_source", "erpnext_source", "verified_at")):
        errors.append("support_basis must include documentation, source URLs, and verified_at")

    repositories = data.get("repositories")
    if not isinstance(repositories, list):
        errors.append("repositories must be a list")
        repositories = []
    seen: set[str] = set()
    for repo in repositories:
        if not isinstance(repo, dict):
            errors.append("each repository must be an object")
            continue
        name = repo.get("name")
        if name in seen:
            errors.append(f"repository {name}: duplicate")
        seen.add(name)
        if name not in REPOSITORIES:
            errors.append(f"repository {name}: unexpected name")
        for field in ("name", "url", "ref", "commit"):
            if field not in repo or not isinstance(repo[field], str) or not repo[field]:
                errors.append(f"repository {name}: missing {field}")
        ref = repo.get("ref")
        if isinstance(ref, str) and (ref.casefold() in FLOATING or not SEMVER_REF.fullmatch(ref)):
            errors.append(f"repository {name}: ref must be an immutable semver tag, got {ref!r}")
        commit = repo.get("commit")
        if isinstance(commit, str) and not SHA.fullmatch(commit):
            errors.append(f"repository {name}: commit must be a full 40-character SHA")
    if seen != REPOSITORIES:
        errors.append(f"repositories must contain exactly {sorted(REPOSITORIES)}")

    runtime = data.get("runtime")
    required_runtime = {"python", "node", "npm", "yarn", "pip", "bench", "mariadb", "redis", "wkhtmltopdf"}
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
        runtime = {}
    if set(runtime) != required_runtime:
        errors.append(f"runtime must contain exactly {sorted(required_runtime)}")
    for name in required_runtime:
        item = runtime.get(name)
        if not isinstance(item, dict) or not isinstance(item.get("version"), str) or not item["version"]:
            errors.append(f"runtime {name}: exact version is required")
            continue
        if item["version"].casefold() in FLOATING or any(token in item["version"] for token in (">", "<", "^", "~", "*")):
            errors.append(f"runtime {name}: floating/ranged version is not allowed")

    images = data.get("images")
    if not isinstance(images, list):
        errors.append("images must be a list")
        images = []
    image_names: set[str] = set()
    for image in images:
        if not isinstance(image, dict):
            errors.append("each image must be an object")
            continue
        name = image.get("name")
        image_names.add(name)
        for field in ("name", "tag", "reference", "digest", "source"):
            if field not in image or not isinstance(image[field], str) or not image[field]:
                errors.append(f"image {name}: missing {field}")
        tag = image.get("tag")
        if isinstance(tag, str) and tag.casefold() in FLOATING:
            errors.append(f"image {name}: floating tag is not allowed")
        digest = image.get("digest")
        if isinstance(digest, str) and not DIGEST.fullmatch(digest):
            errors.append(f"image {name}: digest must be sha256 plus 64 hex characters")
        reference = image.get("reference")
        if isinstance(reference, str) and digest and not reference.endswith(f"@{digest}"):
            errors.append(f"image {name}: reference must end with its digest")
    if image_names != IMAGES:
        errors.append(f"images must contain exactly {sorted(IMAGES)}")

    policy = data.get("policy")
    if not isinstance(policy, dict) or policy.get("floating_refs_forbidden") is not True or policy.get("image_digests_required") is not True:
        errors.append("policy must forbid floating refs and require image digests")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--negative-fixture", action="store_true", help="verify that a floating ref is rejected")
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"VERSION CHECK: FAIL\n- {exc}")
        return 1
    errors = validate(data)
    if args.negative_fixture:
        fixture = copy.deepcopy(data)
        if isinstance(fixture, dict) and isinstance(fixture.get("repositories"), list) and fixture["repositories"]:
            fixture["repositories"][0]["ref"] = "develop"
        if not any("floating" in error or "immutable semver" in error for error in validate(fixture)):
            errors.append("negative fixture: floating ref was not rejected")
    if errors:
        print("VERSION CHECK: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VERSION CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
