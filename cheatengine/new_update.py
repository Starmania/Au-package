"""Update the chocolatey package for Cheat Engine.

The download button on cheatengine.org points at a stub installer whose file name
is randomized on every page load and which bundles third-party offers. That stub
is only used here as a source of information: it is unpacked and its compiled
Inno Setup code is searched for the URL of the clean installer (the one the stub
itself downloads when run with /ZBDIST). Only the clean installer is ever
downloaded, checksummed and referenced by the chocolatey package.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys

from packaging import version
import requests

HOME_PAGE = "https://www.cheatengine.org/index.php"

# The download button on the home page, e.g. https://<cdn>.cloudfront.net/TroCUaDmA.exe
REGEX_STUB_URL = r'href="(https://[\w-]+\.cloudfront\.net/[\w-]+\.exe)"'
# Inside the stub's CompiledCode.bin: the clean installer URL followed by its silent args.
REGEX_URL = r"(https://[\w-]+\.cloudfront\.net/f/CheatEngine/(?:(?:[\w.~-]*|%[\da-f]{2})/)+CheatEngine(\d{2}).exe)\x02....\x13([/A-Z0-9 ]+)"
REGEX_VERSION = r"<version>(\d+\.\d+)</version>"
REGEX_SCRIPT = {
    "url": r"-Url '(.*)'",
    "silent_args": r"-Silent '(.*)'",
    "checksum": r"-Checksum '(.*)'",
    "sub": {
        "url": "-Url '{0}'",
        "silent_args": "-Silent '{0}'",
        "checksum": "-Checksum '{0}'"
    }
}

TMP_DIR = "tmp"
STUB_FILE = os.path.join(TMP_DIR, "stub.exe")


def wine_wrap(command: list) -> list:
    """Prefix a Windows command with wine when not running on Windows."""
    if sys.platform == "win32":
        return command
    wine = shutil.which("wine")
    if wine is None:
        raise RuntimeError(
            "wine is required to run innounp as no unix edition exists.")
    return [wine] + command


def download(url: str, destination: str):
    """Download url to destination, skipping the transfer if it is already there."""
    if os.path.exists(destination):
        print(f"{destination} already exists.")
        return
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=1 << 16):
            file.write(chunk)


def get_stub_url() -> str:
    """Return the (randomized) URL of the stub installer advertised on the home page."""
    page = requests.get(HOME_PAGE, timeout=30)
    page.raise_for_status()
    match = re.search(REGEX_STUB_URL, page.text)
    if not match:
        raise ValueError("Could not find the download link on the home page.")
    return match.group(1)


def get_compiled_code(filename: str) -> str:
    """Unpack an Inno Setup installer and return its compiled code as text."""
    print("Decompiling the installer...")
    basename = os.path.splitext(filename)[0]
    if os.path.exists(basename):
        shutil.rmtree(basename)

    subprocess.run(wine_wrap([os.path.join("utils", "innounp.exe"), "-x", "-m",
                              f"-d{basename}", "-q", "-b", "-y", filename]), check=True)

    compiled_code_path = os.path.join(basename, "embedded", "CompiledCode.bin")
    if not os.path.exists(compiled_code_path):
        raise ValueError(f"{filename} does not look like the expected stub installer.")
    with open(compiled_code_path, "rb") as file:
        content = file.read().decode("utf-8", "ignore")
    shutil.rmtree(basename)

    return content.replace("\x00", "")


def get_real_installer() -> dict:
    """Return the URL, version and silent args of the clean installer."""
    download(get_stub_url(), STUB_FILE)

    match = re.search(REGEX_URL, get_compiled_code(STUB_FILE))
    if not match:
        raise ValueError("Could not find the clean installer URL inside the stub.")

    short_version = match.group(2)
    return {
        "url": match.group(1),
        "version": f"{short_version[0]}.{short_version[1:]}",
        "silent_args": match.group(3),
    }


def sha256(filename: str) -> str:
    with open(filename, "rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest().upper()


def read_nuspec_version() -> str:
    with open("cheatengine.nuspec", "r", encoding="utf-8") as file:
        match = re.search(REGEX_VERSION, file.read())
    if not match:
        raise ValueError("Could not find the version in cheatengine.nuspec.")
    return match.group(1)


def write_nuspec_version(new_version: str):
    with open("cheatengine.nuspec", "r+", encoding="utf-8") as file:
        content = re.sub(REGEX_VERSION, f"<version>{new_version}</version>", file.read())
        file.seek(0)
        file.truncate()
        file.write(content)


def write_scripts(result: dict, new_version: str):
    install_path = os.path.join("tools", "chocolateyInstall.ps1")
    with open(install_path, "r+", encoding="utf-8") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            for key in ("url", "silent_args", "checksum"):
                line = re.sub(REGEX_SCRIPT[key],
                              REGEX_SCRIPT["sub"][key].format(result[key]), line)
            lines[i] = line

        file.seek(0)
        file.truncate()
        file.writelines(lines)

    uninstall_path = os.path.join("tools", "chocolateyUninstall.ps1")
    with open(uninstall_path, "r+", encoding="utf-8") as file:
        content = re.sub(r"Cheat Engine \d+\.\d+", f"Cheat Engine {new_version}", file.read())
        file.seek(0)
        file.truncate()
        file.write(content)


def main(force: bool = False) -> str:
    os.makedirs(TMP_DIR, exist_ok=True)

    result = get_real_installer()
    new_version = result["version"]
    old_version = read_nuspec_version()

    if version.parse(new_version) <= version.parse(old_version) and not force:
        print(f"Already up to date ({old_version}).")
        return ""

    print(f"Updating {old_version} -> {new_version}...")

    installer = os.path.join(TMP_DIR, f"CheatEngine{new_version.replace('.', '')}-real.exe")
    download(result["url"], installer)
    result["checksum"] = sha256(installer)

    print(result)

    write_nuspec_version(new_version)
    write_scripts(result, new_version)

    return new_version


if __name__ == "__main__":
    force_update = "--force" in sys.argv
    updated_version = main(force_update)

    if updated_version:
        subprocess.run(["choco", "pack"], check=True)
        if "--push" in sys.argv:
            subprocess.run(["choco", "push", f"cheatengine.{updated_version}.nupkg"], check=True)

    shutil.rmtree(TMP_DIR, ignore_errors=True)
