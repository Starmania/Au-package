import os
import re
import shutil
import subprocess

from packaging import version
import requests
# bar
from alive_progress import alive_bar

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


def get_content(filename: str, bar) -> str:
    bar()
    print("Decompiling the installer...")
    basename = ".".join(filename.split(".")[0:-1])
    subprocess.run(
        ["utils\innounp.exe", "-x", "-m", f"-d{basename}",
         "-q", "-b", "-y", f"{filename}"]
    )
    if os.path.exists(f"{basename}\\{{app}}"):
        return "Original"
    with open(f"{basename}\\embedded\\CompiledCode.bin", "rb") as f:
        content = f.read().decode("utf-8", "ignore")
    shutil.rmtree(basename)

    return content


def get_real_file(new_version: str, filename: str, bar):
    new_version_short = new_version.replace(".", "")
    basename = ".".join(filename.split(".")[0:-1])
    bar()
    print("Downloading the installer...")
    if not os.path.exists(f"tmp\{filename}"):
        base_URL = f"https://github.com/cheat-engine/cheat-engine/releases/download/{new_version}/CheatEngine{new_version_short}.exe"
        out = requests.get(base_URL, stream=True).content
        bar()
        print("Downloaded the installer.")
        with open(f"tmp\{filename}", "wb") as f:
            f.write(out)
    else:
        bar()
        print("Installer already exists.")

    content = get_content(f"tmp\{filename}", bar)
    if os.path.exists(f"tmp\\{basename}\\{{app}}"):
        result = {
            "url": f"https://github.com/cheat-engine/cheat-engine/releases/download/{new_version}/CheatEngine{new_version_short}.exe",
            "silent_args": "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /CLOSEAPPLICATIONS /NOCANCEL /DIR=\"C:\\\\Program Files\\\\Cheat Engine {0}\"".format(new_version),
        }
        if not os.path.exists(f"tmp\CheatEngine{new_version_short}-real.exe"):
            shutil.copyfile(f"tmp\CheatEngine{new_version_short}.exe", f"tmp\CheatEngine{new_version_short}-real.exe")
        shutil.rmtree(f"tmp\\{basename}")
        bar(2)
        return result
    content = content.replace("\x00", "")

    url = re.search(REGEX_URL, content)

    if not url:
        raise ValueError(f"Could not find the URL for version {new_version_short}.")
    
    bar()
    print("Found match. Downloading the real file...")
    if not os.path.exists(f"tmp\{basename}-real.exe"):
        file_content = requests.get(url.group(1), stream=True).content
        bar()
        print("Downloaded the real file.")

        with open(f"tmp\{basename}-real.exe", "wb") as f:
            f.write(file_content)
    else:
        bar()
        print("Real file already exists.")
    result = {
        "url": url.group(1),
        "silent_args": url.group(2),
    }
    return result


def main(new_version: str, force: bool = False):
    with alive_bar(7, title=f"Updating to {new_version}...") as bar:
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
                    bar(7)
                    return

            file.seek(0)
            file.truncate()
            file.writelines(lines)

        bar()
        print("Updating the script...")

        new_version_short = new_version.replace(".", "")

        _result = get_real_file(new_version, f"CheatEngine{new_version_short}.exe", bar)

        if not _result:
            return

        sha256_hash = subprocess.run(["utils\checksum.exe", "-t=sha256",
                                      f"-f=tmp\CheatEngine{new_version_short}-real.exe"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\r")[0]
        _result["checksum"] = sha256_hash

        bar()
        print("Printing the result...")
        print(_result)

        with open("tools\\chocolateyInstall.ps1", "r+", encoding="utf-8") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                # line = lines[i]
                for j in range(len(REGEX_SCRIPT)-1):
                    _key = list(REGEX_SCRIPT.keys())[j]
                    lines[i] = re.sub(REGEX_SCRIPT[_key], REGEX_SCRIPT["sub"][_key].format(_result[_key]), lines[i])

            file.seek(0)
            file.truncate()
            file.writelines(lines)

        with open("tools\\chocolateyUninstall.ps1", "r+", encoding="utf-8") as file:
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
    result = main("6.4", True)
    print(result)


if __name__ == "__main__":
    VERSIONS = check_for_updates()

    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    # test()
    for _version in VERSIONS:
        main(_version)
        subprocess.run(["choco", "pack"])
        subprocess.run(["choco", "push", f"cheatengine.{_version}.nupkg"])
    shutil.rmtree("tmp")
