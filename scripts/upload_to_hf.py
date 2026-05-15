#!/usr/bin/env python3
"""
Upload Tilavet Phonemizer to Hugging Face Hub

This script uploads the phonemizer package and model card to Hugging Face.
Requires: huggingface_hub package and HF_TOKEN environment variable.

Usage:
    export HF_TOKEN=your_huggingface_token
    python scripts/upload_to_hf.py --repo-id your-username/tilavet-phonemizer
"""

import argparse
import subprocess
from pathlib import Path

from huggingface_hub import HfApi


def build_package():
    """Build the package using python -m build."""
    print("Building package...")
    result = subprocess.run(
        ["python3", "-m", "build"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    print("Build successful")
    return True


def upload_to_hub(repo_id: str, create_repo: bool = True):
    """Upload to Hugging Face Hub."""
    api = HfApi()

    if create_repo:
        try:
            api.create_repo(repo_id, repo_type="model", exist_ok=True)
            print(f"Created repository: {repo_id}")
        except Exception as e:
            print(f"Error creating repository: {e}")
            return False

    # Upload files
    repo_path = Path(__file__).parent.parent

    # HuggingFace Hub uses README.md as the model card and REQUIRES YAML
    # frontmatter at the top of it (license, tags, language, library_name).
    # Our MODEL_CARD.md already carries that frontmatter, so we upload it
    # *as* README.md on the Hub. The GitHub-flavored README.md (with badges
    # and install instructions) is uploaded under its original name as a
    # secondary doc so the Hub repo still surfaces the developer-facing
    # quickstart.
    #
    # See: https://huggingface.co/docs/hub/model-cards#model-card-metadata
    files_to_upload: list[tuple[str, str]] = [
        ("MODEL_CARD.md", "README.md"),          # primary model card on HF
        ("README.md", "GITHUB_README.md"),       # GitHub README kept for reference
        ("LICENSE", "LICENSE"),
        ("CHANGELOG.md", "CHANGELOG.md"),
        ("CONTRIBUTING.md", "CONTRIBUTING.md"),
        ("docs/phoneme-spec.md", "docs/phoneme-spec.md"),
        ("docs/waqf-pause-decision.md", "docs/waqf-pause-decision.md"),
        ("docs/aligner-mvp.md", "docs/aligner-mvp.md"),
        ("data/ctc_classes.txt", "data/ctc_classes.txt"),
        ("data/ctc_classes.json", "data/ctc_classes.json"),
    ]

    for local_path, repo_relpath in files_to_upload:
        full_path = repo_path / local_path
        if full_path.exists():
            try:
                api.upload_file(
                    path_or_fileobj=str(full_path),
                    path_in_repo=repo_relpath,
                    repo_id=repo_id,
                    repo_type="model",
                )
                label = (
                    f"{local_path} → {repo_relpath}"
                    if local_path != repo_relpath
                    else local_path
                )
                print(f"Uploaded: {label}")
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")
        else:
            print(f"File not found: {local_path}")

    # Upload source code
    src_path = repo_path / "src"
    if src_path.exists():
        try:
            api.upload_folder(
                folder_path=str(src_path),
                path_in_repo="src",
                repo_id=repo_id,
                repo_type="model",
            )
            print("Uploaded: src/")
        except Exception as e:
            print(f"Error uploading src/: {e}")

    # Upload tests
    tests_path = repo_path / "tests"
    if tests_path.exists():
        try:
            api.upload_folder(
                folder_path=str(tests_path),
                path_in_repo="tests",
                repo_id=repo_id,
                repo_type="model",
            )
            print("Uploaded: tests/")
        except Exception as e:
            print(f"Error uploading tests/: {e}")

    print(f"\nUpload complete! View at: https://huggingface.co/{repo_id}")


def main():
    parser = argparse.ArgumentParser(description="Upload Tilavet Phonemizer to Hugging Face")
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Hugging Face repository ID (e.g., username/tilavet-phonemizer)",
    )
    parser.add_argument("--no-build", action="store_true", help="Skip building the package")
    parser.add_argument(
        "--no-create-repo",
        action="store_true",
        help="Skip creating the repository",
    )

    args = parser.parse_args()

    # Check if user is logged in
    try:
        api = HfApi()
        api.whoami()
    except Exception:
        print("Please login to Hugging Face first:")
        print("  huggingface-cli login")
        print("Or set HF_TOKEN environment variable")
        return

    if not args.no_build:
        if not build_package():
            return

    upload_to_hub(args.repo_id, create_repo=not args.no_create_repo)


if __name__ == "__main__":
    main()
