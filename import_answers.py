#!/usr/bin/env python3
"""Import a study_answers.json (or pasted JSON text) into the Google Sheet
by replaying it against the same Apps Script endpoint the web form uses.

Usage:
  python3 import_answers.py study_answers.json      # from a file
  python3 import_answers.py -                        # paste JSON, then Ctrl-D
"""
import json, sys, urllib.request

ENDPOINT = "https://script.google.com/macros/s/AKfycbxL7cfl-touLGM1Ky0DHJ17KO2hrir0PKTxYLijyE0p5aGy6XuvykSijAoFnHwr89hGYQ/exec"

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8").read()
    raw = raw.strip()
    # tolerate chat apps wrapping / smart quotes around the payload
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        sys.exit("No JSON object found in input.")
    payload = json.loads(raw[start:end + 1])

    for key in ("version", "nickname", "answers"):
        if key not in payload:
            sys.exit(f"Missing key: {key} — is this really study_answers.json?")
    payload["nickname"] = f"{payload['nickname']} (imported)"
    print(f"Importing: version={payload['version']} nickname={payload['nickname']!r} "
          f"answers={len(payload['answers'])}")

    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "text/plain"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode(errors="replace")
    print(f"HTTP {r.status}: {body[:200]}")
    print("Done — check the sheet tab for this version.")

if __name__ == "__main__":
    main()
