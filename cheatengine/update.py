import os
import re
import shutil
import subprocess

from packaging import version
import requests

DEBUG = True

if DEBUG:
    import time

REGEX_URL = r"(https://d2oq4dwfbh6gxl.cloudfront.net/f/CheatEngine/(?:(?:[\w.~-]*|%[\da-f]{2})/)+CheatEngine\d{2}.exe)\x02\x1c\x04\x01\x14\x13([/A-Z0-9 ]+)"
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
    if DEBUG:
        print("DEBUG: Decompiling the installer...")
    basename = ".".join(filename.split(".")[0:-1])
    subprocess.run(["utils\innounp.exe", "-x", "-m", f"-d{basename}", "-q", "-b", "-y", f"{filename}"])
    if os.path.exists(f"{basename}\\{{app}}"):
        return "Original"
    with open(f"{basename}\\embedded\\CompiledCode.bin", "rb") as f:
        content = f.read().decode("utf-8", "ignore")
    shutil.rmtree(basename)

    return content


def get_real_file(version: str, filename: str):
    version_short = version.replace(".", "")
    basename = ".".join(filename.split(".")[0:-1])
    if DEBUG:
        print("DEBUG: Downloading the installer...")
    if not os.path.exists(f"tmp\{filename}"):
        base_URL = f"https://github.com/cheat-engine/cheat-engine/releases/download/{version}/CheatEngine{version_short}.exe"
        out = requests.get(base_URL, stream=True).content
        if DEBUG:
            print("DEBUG: Downloaded the installer.")
        with open(f"tmp\{filename}", "wb") as f:
            f.write(out)
    elif DEBUG:
        print("DEBUG: Installer already exists.")

    content = get_content(f"tmp\{filename}")
    if os.path.exists(f"tmp\\{basename}\\{{app}}"):
        result = {
            "url": f"https://github.com/cheat-engine/cheat-engine/releases/download/{version}/CheatEngine{version_short}.exe",
            "silent_args": "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /CLOSEAPPLICATIONS /NOCANCEL /DIR=\"C:\\\\Program Files\\\\Cheat Engine {0}\"".format(version),
        }
        if not os.path.exists(f"tmp\CheatEngine{version_short}-real.exe"):
            shutil.copyfile(f"tmp\CheatEngine{version_short}.exe", f"tmp\CheatEngine{version_short}-real.exe")
        shutil.rmtree(f"tmp\\{basename}")
        return result
    content = content.replace("\x00", "")

    url = re.search(REGEX_URL, content)

    if url:
        if DEBUG:
            print("DEBUG: Found match. Downloading the real file...")
        if not os.path.exists(f"tmp\{basename}-real.exe"):
            file_content = requests.get(url.group(1), stream=True).content
            if DEBUG:
                print("DEBUG: Downloaded the real file.")

            with open(f"tmp\{basename}-real.exe", "wb") as f:
                f.write(file_content)
        elif DEBUG:
            print("DEBUG: Real file already exists.")
        result = {
            "url": url.group(1),
            "silent_args": url.group(2),
        }
        return result
    return None


def main(new_version: str, force: bool = False):
    if DEBUG:
        print("DEBUG: Starting the script...")
        # time.sleep(2)
    with open("cheatengine.nuspec", "r+", encoding="utf-8") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            line = lines[i]
            result = re.search(REGEX_VERSION, line)
            if result:
                old_version = version.parse(result.group(1))
                if version.parse(new_version) > old_version or force:
                    lines[i] = line.replace(result.group(1), new_version)
                    break
                return

        file.seek(0)
        file.truncate()
        file.writelines(lines)

    if DEBUG:
        print("DEBUG: Updating the script...")

    version_short = new_version.replace(".", "")
    
    _result = get_real_file(new_version, f"CheatEngine{version_short}.exe")

    if not _result:
        return

    sha256_hash = subprocess.run(["utils\checksum.exe", "-t=sha256",
                                 f"-f=tmp\CheatEngine{version_short}-real.exe"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\r")[0]
    _result["checksum"] = sha256_hash

    if DEBUG:
        print(_result)
        time.sleep(2)

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


def test():
    result = main("6.4", True)
    print(result)


if __name__ == "__main__":
    VERSIONS = ["7.3", "7.4", "7.5"]
    
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    # test()
    for _version in VERSIONS:
        main(_version, True)
        subprocess.run(["choco", "pack"])
        subprocess.run(["choco", "push", f"cheatengine.{_version}.nupkg"])
    shutil.rmtree("tmp")
