import os
import random
import string
import zlib
import base64
import json

def generate_mapping():
    charset = string.ascii_letters + string.digits
    mapping = {}
    used = set()

    for b in range(256):
        while True:
            length = random.randint(6, 20)
            candidate = ''.join(random.choices(charset, k=length))
            if candidate not in used:
                used.add(candidate)
                mapping[b] = candidate
                break
    return mapping

def insert_noise(encoded, noise_ratio=0.5):
    charset = string.ascii_letters + string.digits
    noisy_encoded = []
    noise_positions = []
    total_real = len(encoded)
    noise_count = int(total_real * noise_ratio)

    # Shuffle positions for real and noise tokens
    positions = list(range(total_real + noise_count))
    random.shuffle(positions)
    real_positions = sorted(positions[:total_real])
    noise_positions = sorted(positions[total_real:])

    real_iter = iter(encoded)
    for i in range(total_real + noise_count):
        if i in noise_positions:
            length = random.randint(6, 20)
            noise_word = ''.join(random.choices(charset, k=length))
            noisy_encoded.append(noise_word)
        else:
            noisy_encoded.append(next(real_iter))

    return noisy_encoded, noise_positions

def obfuscate_script(input_path, output_path):
    with open(input_path, "rb") as f:
        raw = f.read()

    mapping = generate_mapping()
    encoded = [mapping[b] for b in raw]

    noisy_encoded, noise_positions = insert_noise(encoded, noise_ratio=0.5)

    payload = {
        "mapping": mapping,
        "encoded": noisy_encoded,
        "noise_positions": noise_positions
    }

    json_payload = json.dumps(payload).encode()
    compressed = zlib.compress(json_payload)
    b64_data = base64.b64encode(compressed).decode()

    runner_code = f'''
import sys
import zlib
import base64
import json

_data_b64 = "{b64_data}"

def decode_payload(data_b64):
    decoded = base64.b64decode(data_b64)
    decompressed = zlib.decompress(decoded)
    return json.loads(decompressed)

payload = decode_payload(_data_b64)

mapping = payload["mapping"]
encoded = payload["encoded"]
noise_positions = set(payload["noise_positions"])

reverse_map = {{v: int(k) for k, v in mapping.items()}}

def decode_heavy(encoded_list, noise_pos_set, reverse):
    result = []
    for idx, word in enumerate(encoded_list):
        if idx in noise_pos_set:
            continue
        if word not in reverse:
            print(f"[!] Unknown word at position {{idx}}: {{word}}. Exiting.")
            sys.exit(1)
        result.append(reverse[word])
    return bytes(result)

try:
    decoded_bytes = decode_heavy(encoded, noise_positions, reverse_map)
    code = decoded_bytes.decode("utf-8")
except Exception as e:
    print("[!] Deobfuscation failed:", e)
    sys.exit(1)

exec(code, globals())
'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(runner_code)

    print(f"[+] Heavy obfuscated script created at {output_path}")

def main():
    input_path = input("Path to Python script to obfuscate: ").strip()
    if not os.path.isfile(input_path):
        print("[!] File not found.")
        return

    output_path = input("Output filename for obfuscated script (e.g. obf.py): ").strip()
    if not output_path.endswith(".py"):
        output_path += ".py"

    obfuscate_script(input_path, output_path)

if __name__ == "__main__":
    main()
