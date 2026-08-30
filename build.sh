#!/usr/bin/env bash
set -euo pipefail

quarto_version="1.10.18"
uv_version="0.12.7"

build_dir="build"
tools_dir="$build_dir/tools"
quarto_dir="$tools_dir/quarto"
uv_dir="$tools_dir/uv"

# Remove stale files and folders
if [ -d "$tools_dir" ]; then
    echo "Removing stale build directory files: $tools_dir"
    rm -rf "$tools_dir"
fi

mkdir -p "$quarto_dir" "$uv_dir"

echo
echo "Installing necessary website dependencies, this may take a minute..."
echo

# Install uv, adjust installation directory and use the unmanaged install environment variable for CI/CD
curl -LsSf "https://astral.sh/uv/${uv_version}/install.sh" \
    | env UV_UNMANAGED_INSTALL="$uv_dir" sh

# Install Quarto
wget -q \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${quarto_version}/quarto-${quarto_version}-linux-amd64.tar.gz" \
    -O /tmp/quarto.tar.gz

# Extract the Quarto installation to 'build/tools' and strip the top level directory. This is identical to directly extracting all
# subfolders under 'quarto-1.10.18' into 'build/tools/quarto' directly.
tar -xzf /tmp/quarto.tar.gz -C "$quarto_dir" --strip-components=1

# Export uv and Quarto commands to path
export PATH="${uv_dir}:${quarto_dir}/bin:$PATH"

# When syncing virtual environments, use '--locked' to ensure exact reproducibility with pyproject.toml
uv sync --locked
quarto render website --profile production