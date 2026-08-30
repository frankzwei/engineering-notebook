"""
Post-render script to replace all URL placeholders as specified with the associated base URL in ``base-urls.yaml``.

Each placeholder to be replaced must be unique and have an entry in the ``TOKENS`` dictionary. The script reads in the
key-value pair to determine the field name in ``base-urls.yaml``. Depending on the build mode, either production or
local, the respective base URL is pulled.
"""

from argparse import HelpFormatter, Namespace
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

import argparse
import yaml


TOKENS = {
    '$FILES_BASE_URL': 'files',
    '$ASSETS_BASE_URL': 'assets'
}

def _validate_path(path: str | Path) -> Path:
    """Validate whether the directory or file the path points to exists.

    This method makes no further check that the path points to a file or a directory.

    :param path: The relative or absolute path to the file system object.
    :raises FileNotFoundError: If the object the path points to is missing.
    :return: The absolute path pointing to the file system object.
    """
    if not (path_obj := Path(path).expanduser().resolve()).exists():
        raise FileNotFoundError(f'Missing file or directory in path: {path_obj}')

    return path_obj

def parse_cli_args(argv: list[str] | None = None) -> Namespace:
    """Parse the CLI arguments.

    :param argv: The arguments passed to the script from the CLI, defaults to None
    :return: The CLI arguments as a namespace object.
    """
    parser = argparse.ArgumentParser(
        description='Updates all external file and asset URL placeholders with their run time values.',
        formatter_class=lambda prog: HelpFormatter(prog, width=120)
    )

    parser.add_argument(
        '--mode',
        dest='mode',
        nargs='?',
        choices=('local', 'production'),
        type=str,
        help='the build mode used for the program (default: %(default)s)',
        default='local',
        const='local'
    )

    parser.add_argument(
        '--output-dir',
        dest='output_dir',
        type=str,
        help='the build output directory relative to the project root (default: %(default)s)',
        default='_site'
    )

    return parser.parse_args(argv)

def _load_placeholders(mode: str, config_path: Path) -> dict[str, str]:
    """Load the registered URL placeholder and base URLs into memory from the configuration file.

    :param mode: The build mode for the website, must be either 'mode' or 'production'
    :param config_path: The path to the base URL configuration file.
    :raises ValueError: If an invalid build mode is entered.
    :raises TypeError: If the URL the placeholder maps to is not a String.
    :return: A dictionary of the placeholder type and the base URL to replace.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config: dict[str, Any] = yaml.safe_load(f)

    if (mode := mode.lower()) not in config:
        raise ValueError(
            f'Received an unknown deployment mode: {mode}. The valid deployment modes are: production and local'
        )

    base_urls: dict[str, Any] = config[mode]
    for placeholder_type, base_url in base_urls.items():
        if not isinstance(base_url, str):
            raise TypeError(f'The placeholder {placeholder_type} does not map to a URL, got {base_url}')

        base_urls[placeholder_type] = base_url.rstrip('/')

    return base_urls

def replace_placeholders(args: Namespace) -> int:
    """Replace all registered URL placeholders with the mapped base URL.

    :param args: The CLI arguments as a namespace object.
    :return: The number of HTML files updated.
    """
    config_resource: Traversable = files('engineering_notebook.config').joinpath('base-urls.yaml')
    output_path: Path = _validate_path(args.output_dir)

    with as_file(config_resource) as resource_path:
        config_path: Path = _validate_path(resource_path)
        base_urls: dict[str, str] = _load_placeholders(args.mode, config_path)

    counter: int = 0
    for html_path in output_path.rglob('*.html'):
        content: str = html_path.read_text(encoding='utf-8')
        updated: str = content
        for token, key in TOKENS.items():
            updated = updated.replace(token, base_urls[key])

        if updated != content:
            html_path.write_text(updated, encoding='utf-8')
            counter += 1

    return counter

def main(argv: list[str] | None = None):
    args: Namespace = parse_cli_args(argv)
    count: int = replace_placeholders(args)
    print(
        f'Finished replacing all base URLs ({args.mode.lower()}: {count} HTML file{'' if count == 1 else 's'} updated)'
    )

if __name__ == '__main__':
    main()