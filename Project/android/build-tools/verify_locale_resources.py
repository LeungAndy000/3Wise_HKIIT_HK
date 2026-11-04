"""Read-only audit of complete UI translations, format arguments and locale wiring."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ANDROID = Path(__file__).resolve().parents[1]
RES = ANDROID / "app/src/main/res"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def audit():
    paths = {"en": "values", "zh-Hant": "values-b+zh+Hant", "zh-Hans": "values-b+zh+Hans"}
    catalogs = {}
    for language, directory in paths.items():
        rows = ET.parse(RES / directory / "strings.xml").getroot()
        catalogs[language] = {row.attrib["name"]: row.text or "" for row in rows if row.attrib.get("translatable") != "false"}
        if len(catalogs[language]) != len([row for row in rows if row.attrib.get("translatable") != "false"]):
            raise AssertionError(f"Duplicate string key in {language}")
    english = catalogs["en"]
    for language, catalog in catalogs.items():
        if set(catalog) != set(english):
            raise AssertionError(f"Incomplete translation: {language}")
        for key, value in catalog.items():
            if not value.strip():
                raise AssertionError(f"Empty UI string: {language}.{key}")
            if re.findall(r"%(?:\d+\$)?(?:\.\d+)?[dsf]", value) != re.findall(r"%(?:\d+\$)?(?:\.\d+)?[dsf]", english[key]):
                raise AssertionError(f"Format arguments differ: {language}.{key}")
    legacy = {row.attrib["name"]: row.text or "" for row in ET.parse(RES / "values-zh-rCN/strings.xml").getroot()}
    if legacy != catalogs["zh-Hans"]:
        raise AssertionError("Legacy Simplified resources do not match the script-qualified resources")
    configured = [row.attrib[ANDROID_NS + "name"] for row in ET.parse(RES / "xml/locales_config.xml").getroot()]
    if set(configured) != set(paths):
        raise AssertionError("System app-language choices differ from translated languages")
    manifest = ET.parse(ANDROID / "app/src/main/AndroidManifest.xml").getroot()
    if manifest.find("application").attrib.get(ANDROID_NS + "localeConfig") != "@xml/locales_config":
        raise AssertionError("Android system language configuration is not connected")
    permissions = [row.attrib[ANDROID_NS + "name"] for row in manifest.findall("uses-permission")]
    if "android.permission.INTERNET" in permissions:
        raise AssertionError("The local app must not request Internet permission")
    return {"passed": True, "translated_strings_per_language": len(english), "languages": list(paths),
            "format_arguments_match": True, "legacy_simplified_matches": True,
            "android_system_language_configured": True, "internet_permission": False,
            "scope": "UI localization only; no claim of English SMS model accuracy or physical-device execution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = audit()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
