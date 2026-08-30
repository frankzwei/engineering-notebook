from argparse import HelpFormatter, Namespace
from pathlib import Path
from typing import Any

import argparse
import yaml


TOKENS = {
    '$FILES_BASE_URL': 'files',
    '$ASSETS_BASE_URL': 'assets'
}

def _validate_path(path: str | Path) -> Path:
    if not (path_obj := Path(path).expanduser().resolve()).exists():
        raise FileNotFoundError(f'Missing file or directory in path: {path_obj}')

    return path_obj

def parse_cli_args(argv: list[str] | None = None) -> Namespace:
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

    parser.add_argument(
        '--config-path',
        dest='config_path',
        type=str,
        help='path to the base URL configuration file (default: %(default)s)',
        default='_config/base-urls.yml'
    )

    return parser.parse_args(argv)

def load_placeholders(mode: str, config_path: Path) -> dict[str, str]:
    with open(config_path, 'r', encoding='utf-8') as f:
        config: dict[str, Any] = yaml.safe_load(f)

    if (mode := mode.lower()) not in config:
        raise ValueError(f'Received an unknown deployment mode: {mode}. The valid deployment modes are: production and local')

    base_urls: dict[str, Any] = config[mode]
    for key in ('files', 'assets'):
        if key not in base_urls:
            raise ValueError(f'Missing \'{mode}.{key}\' in {config_path}')

        if not isinstance(base_urls.get(key), str):
            raise TypeError(f'Entry \'{mode}.{key}\' must be a string')

        base_urls[key] = base_urls[key].rstrip('/')

    return base_urls

def replace_placeholders(args: Namespace) -> int:
    config_path: Path = _validate_path(args.config_path)
    output_path: Path = _validate_path(args.output_dir)

    base_urls: dict[str, str] = load_placeholders(args.mode, config_path)

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
    print(f'Finished replacing all base URLs ({args.mode.lower()}: {count} HTML file(s) updated)')

if __name__ == '__main__':
    main()