import os
import random
import string
import json

def generate_mapping():
    charset = string.ascii_letters + string.digits
    mapping = {}
    reverse = {}

    for i in range(256):
        while True:
            fake = ''.join(random.choices(charset, k=8))
            if fake not in reverse:
                break
        mapping[i] = fake
        reverse[fake] = i

    return mapping, reverse

def encode_script(data: bytes, mapping: dict):
    return [mapping[b] for b in data]

def obfuscate_script(input_path, output_path):
    with open(input_path, 'rb') as f:
        raw = f.read()

    map_forward, _ = generate_mapping()
    encoded = encode_script(raw, map_forward)

    payload = {
        "map": map_forward,
        "data": encoded
    }

    with open(output_path, 'w') as f:
        json.dump(payload, f)

    print(f"[+] Obfuscated code saved to {output_path}")

def main():
    input_path = input("Enter path to Python script to obfuscate: ").strip()
    if not os.path.isfile(input_path):
        print("[!] File not found.")
        return

    output_path = input("Enter output file name (e.g. obf.txt): ").strip()
    if not output_path.endswith(".txt"):
        output_path += ".txt"

    obfuscate_script(input_path, output_path)

if __name__ == "__main__":
    main()
