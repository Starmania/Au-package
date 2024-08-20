import os
import sys
import re
import shutil
import subprocess
from packaging import version
import requests
from pathlib import Path

REGEX_URL = r"(https://d2oq4dwfbh6gxl.cloudfront.net/f/CheatEngine/(?:(?:[\w.~-]*|%[\da-f]{2})/)+CheatEngine\d{2}.exe)\x02....\x13([/A-Z0-9 ]+)"
REGEX_VERSION = r"<version>(\d.\d)</version>"
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

def get_content(filename: str) -> str:
    print("Decompiling the installer...")
    basename = os.path.join(os.path.dirname(filename), ".".join(os.path.basename(filename).split(".")[0:-1]))

    command = [os.path.join("utils", "innounp.exe"), "-x", "-m", f"-d{basename}",
         "-q", "-b", "-y", f"{filename}"]

    if sys.platform != "win32":
        wine = shutil.which("wine")
        assert wine is not None or print("wine is required to rin innounp as no unix-edition exists...")
        command.insert(wine, 0)

    subprocess.run(command)
    app_path = os.path.join(basename, '{app}')
    if os.path.exists(app_path):
        return "Original"

    compiled_code_path = os.path.join(basename, 'embedded', 'CompiledCode.bin')
    with open(compiled_code_path, "rb") as f:
        content = f.read().decode("utf-8", "ignore")
    shutil.rmtree(basename)

    return content

def get_real_file(new_version: str, filename: str):
    new_version_short = new_version.replace(".", "")
    basename = os.path.join(os.path.dirname(filename), ".".join(os.path.basename(filename).split(".")[0:-1]))
    print("Downloading the installer...")
    tmp_dir = os.path.join("tmp", filename)
    if not os.path.exists(tmp_dir):
        base_URL = f"https://github.com/cheat-engine/cheat-engine/releases/download/{new_version}/CheatEngine{new_version_short}.exe"
        out = requests.get(base_URL, stream=True).content
        print("Downloaded the installer.")
        with open(tmp_dir, "wb") as f:
            f.write(out)
    else:
        print("Installer already exists.")

    content = get_content(tmp_dir)
    if os.path.exists(os.path.join("tmp", basename, '{app}')):
        result = {
            "url": f"https://github.com/cheat-engine/cheat-engine/releases/download/{new_version}/CheatEngine{new_version_short}.exe",
            "silent_args": "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /CLOSEAPPLICATIONS /NOCANCEL /DIR=\"C:\\\\Program Files\\\\Cheat Engine {0}\"".format(new_version),
        }
        real_file_path = os.path.join("tmp", f"CheatEngine{new_version_short}-real.exe")
        if not os.path.exists(real_file_path):
            shutil.copyfile(tmp_dir, real_file_path)
        shutil.rmtree(os.path.join("tmp", basename))
        return result

    content = content.replace("\x00", "")

    url = re.search(REGEX_URL, content)

    if not url:
        raise ValueError(f"Could not find the URL for version {new_version_short}.")

    print("Found match. Downloading the real file...")
    real_file_path = os.path.join("tmp", f"{basename}-real.exe")
    if not os.path.exists(real_file_path):
        file_content = requests.get(url.group(1), stream=True).content
        print("Downloaded the real file.")

        with open(real_file_path, "wb") as f:
            f.write(file_content)
    else:
        print("Real file already exists.")
    result = {
        "url": url.group(1),
        "silent_args": url.group(2),
    }
    return result

def main(new_version: str, force: bool = False):
    with open("cheatengine.nuspec", "r+", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            line = lines[i]
            result = re.search(REGEX_VERSION, line)
            if result:
                old_version = result.group(1)
                if version.parse(new_version) > version.parse(old_version) or force:
                    lines[i] = line.replace(old_version, new_version)
                    break
                return

        file.seek(0)
        file.truncate()
        file.writelines(lines)

    print("Updating the script...")

    new_version_short = new_version.replace(".", "")

    _result = get_real_file(new_version, f"CheatEngine{new_version_short}.exe")

    if not _result:
        return
    command = [os.path.join("utils", "checksum.exe"), "-t=sha256",
              f"-f=tmp/CheatEngine{new_version_short}-real.exe"]

    if sys.platform != "win32":
        wine = shutil.which("wine")
        assert wine is not None or print("wine is required to rin innounp as no unix-edition exists...")
        command.insert(wine, 0)

    sha256_hash = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8").split("\r")[0]
    _result["checksum"] = sha256_hash

    print("Printing the result...")
    print(_result)

    choco_install_path = os.path.join("tools", "chocolateyInstall.ps1")

    with open(choco_install_path, "r+", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            for j in range(len(REGEX_SCRIPT)-1):
                _key = list(REGEX_SCRIPT.keys())[j]
                lines[i] = re.sub(REGEX_SCRIPT[_key], REGEX_SCRIPT["sub"][_key].format(_result[_key]), lines[i])

        file.seek(0)
        file.truncate()
        file.writelines(lines)

    choco_uninstall_path = os.path.join("tools", "chocolateyUninstall.ps1")

    with open(choco_uninstall_path, "r+", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            lines[i] = re.sub(r"\d\.\d", new_version, lines[i])

        file.seek(0)
        file.truncate()
        file.writelines(lines)

def check_for_updates():
    releases = requests.get("https://api.github.com/repos/cheat-engine/cheat-engine/releases").json()
    assets = [release["assets"] for release in releases if release["assets"] != []]
    versions = [asset[0]["name"].split(".")[0].replace("CheatEngine", "") for asset in assets]    
    versions = [f"{version[0]}.{version[1]}" for version in versions]
    versions = versions[::-1]
    print(versions)
    return versions

def test():
    result = main("7.5", True)
    print(result)

if __name__ == "__main__":
    VERSIONS = check_for_updates()

    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    for _version in VERSIONS:
        main(_version)
        subprocess.run(["choco", "pack"])
        subprocess.run(["choco", "push", f"cheatengine.{_version}.nupkg"])
    shutil.rmtree("tmp")
