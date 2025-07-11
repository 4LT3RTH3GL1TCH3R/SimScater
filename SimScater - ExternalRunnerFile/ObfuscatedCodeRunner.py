import json
import os

def decode_script(encoded: list, reverse_map: dict):
    return bytes([reverse_map[token] for token in encoded])

def main():
    input_path = input("Enter path to obfuscated .txt file: ").strip()
    if not os.path.isfile(input_path):
        print("[!] File not found.")
        return

    with open(input_path, 'r') as f:
        payload = json.load(f)

    encoded_data = payload["data"]
    reverse_map = {v: int(k) for k, v in payload["map"].items()}

    try:
        decoded_bytes = decode_script(encoded_data, reverse_map)
        code = decoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"[!] Deobfuscation failed: {e}")
        return

    print("[+] Executing deobfuscated code...\n")
    exec(code)
    os.system("clear")

if __name__ == "__main__":
    main()
