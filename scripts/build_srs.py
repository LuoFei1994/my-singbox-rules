#!/usr/bin/env python3
import os, json, subprocess, sys

UPSTREAM_DIR = "upstream"
OUTPUT_DIR = "output"
TEMP_DIR = "temp_json"

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

def read_list_file(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            lines.append(line)
    return lines

def build_source_json(ip_list):
    return {"rules": [{"ip_cidr": cidr} for cidr in ip_list]}

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)

def compile_to_srs(singbox_bin, src_json, out_srs):
    subprocess.check_call([singbox_bin, "rule-set", "compile", "-i", src_json, "-o", out_srs])

def main():
    singbox_bin = os.environ.get("SINGBOX_BIN", "sing-box")
    ensure_dirs()
    list_files = [f for f in os.listdir(UPSTREAM_DIR) if f.endswith(".list")]
    if not list_files:
        print("No .list files found", file=sys.stderr)
        sys.exit(0)
    for filename in list_files:
        base = os.path.splitext(filename)[0]
        src_path = os.path.join(UPSTREAM_DIR, filename)
        json_path = os.path.join(TEMP_DIR, base + ".json")
        srs_path = os.path.join(OUTPUT_DIR, base + ".srs")
        ip_list = read_list_file(src_path)
        source_obj = build_source_json(ip_list)
        write_json(json_path, source_obj)
        compile_to_srs(singbox_bin, json_path, srs_path)
        print(f"Built: {srs_path}")

if __name__ == "__main__":
    main()
