# Digital Notebook

This repository contains the raw files and folders for the personal digital notebook hosted on: https://frank-engineering-notebook.pages.dev/. The pages are hosted on a private Cloudflare server that is automatically re-build and re-generated each time changes are merged into `main`.

The website uses Quarto to generate the HTML files displayed statically. All files and folders are located in the `website` directory. This folder is treated as the root directory of the *website* when compiling. This is the location where Quarto creates `.quarto`. However, the complete website is compiled and placed in the `build/_site` relative to the project root directory. This is the folder referenced by Cloudflare when publishing to the public.

## Development

Contributions to the website must take the form of a pull request (PR).

### Deployment

The `build.sh` script is automatically executed by Cloudflare upon re-building the website. The script is responsible for installing the dependencies `uv` and `Quarto` prior to building. This process is automatic and is not handled by the developer.