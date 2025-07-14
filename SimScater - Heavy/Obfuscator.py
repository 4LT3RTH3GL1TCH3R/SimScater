import os
import random
import string
import zlib
import base64
import json
import time

def generate_charset():
    base = string.ascii_letters + string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/`~" + \
        "¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿" + \
        "αβγδεζηθικλμνξοπρστυφχψωΩΣΦΠΨΔΛΞ"
    charset = list(set(base + symbols))
    charset += [chr(i) for i in range(0x2600, 0x26FF)]
    charset = list(set(charset))
    return charset

def random_string(length, charset):
    return ''.join(random.choices(charset, k=length))

def xor_bytes(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def generate_mapping(charset):
    mapping = {}
    used = set()
    for b in range(256):
        while True:
            length = random.randint(300, 400)
            s = ''.join(random.choices(charset, k=length))
            if s not in used:
                mapping[b] = s
                used.add(s)
                break
    return mapping

def insert_noise(encoded, charset, ratio=3.0):
    total_real = len(encoded)
    noise_count = int(total_real * ratio)
    positions = list(range(total_real + noise_count))
    random.shuffle(positions)
    real_positions = sorted(positions[:total_real])
    noise_positions = sorted(positions[total_real:])
    noisy_encoded = []
    real_iter = iter(encoded)

    for i in range(total_real + noise_count):
        if i in noise_positions:
            noise_len = random.randint(300, 400)
            noisy_encoded.append(''.join(random.choices(charset, k=noise_len)))
        else:
            noisy_encoded.append(next(real_iter))
    return noisy_encoded, noise_positions

def encrypt_mapping(mapping, key):
    raw = json.dumps(mapping).encode()
    encrypted = xor_bytes(raw, key)
    return base64.b64encode(encrypted).decode()

def decrypt_mapping(enc_mapping, key):
    encrypted = base64.b64decode(enc_mapping)
    raw = xor_bytes(encrypted, key)
    return json.loads(raw.decode())

def build_layer(code_bytes, charset, key, layer_num, total_layers):
    mapping = generate_mapping(charset)
    encoded = [mapping[b] for b in code_bytes]
    noisy_encoded, noise_positions = insert_noise(encoded, charset, ratio=3.0)
    enc_mapping = encrypt_mapping(mapping, key)

    payload = {
        "mapping": enc_mapping,
        "encoded": noisy_encoded,
        "noise_positions": noise_positions,
        "layer": layer_num,
        "total_layers": total_layers
    }

    compressed = zlib.compress(json.dumps(payload).encode())
    b64_data = base64.b64encode(compressed).decode()

    junk_funcs = ""
    for i in range(10):
        junk_funcs += f"""
def junk_func_{layer_num}_{i}():
    s = "{random_string(random.randint(50, 100), charset)}"
    for c in s:
        if c == "{random.choice(charset)}":
            return False
    return True
"""

    env_check = f"""
import datetime
def check_env_layer_{layer_num}():
    now = datetime.datetime.now()
    if now.minute % 7 != {layer_num % 7}:
        raise Exception("Environment check failed at layer {layer_num}")
"""

    fake_decoder = f"""
def fake_decoder_{layer_num}(data):
    s = "{random_string(random.randint(200, 300), charset)}"
    if "{random.choice(charset)}" in s:
        return "fake"
    return "real"
"""

    runner_code = f'''
import zlib, base64, json
import sys

{junk_funcs}
{env_check}
{fake_decoder}

def xor_bytes(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def decrypt_mapping(enc_mapping, key):
    import base64, json
    encrypted = base64.b64decode(enc_mapping)
    raw = xor_bytes(encrypted, key)
    return json.loads(raw.decode())

def decode_layer(b64_payload, key):
    compressed = base64.b64decode(b64_payload)
    payload = json.loads(zlib.decompress(compressed).decode())
    mapping_enc = payload["mapping"]
    encoded = payload["encoded"]
    noise_pos = set(payload["noise_positions"])
    mapping = decrypt_mapping(mapping_enc, key)
    inv_map = {{v: int(k) for k,v in mapping.items()}}

    filtered = [w for i,w in enumerate(encoded) if i not in noise_pos]
    decoded_bytes = bytes([inv_map[w] for w in filtered])

    return decoded_bytes, payload.get("layer"), payload.get("total_layers")

try:
    check_env_layer_{layer_num}()
except Exception as e:
    print("[!] Layer {layer_num} environment check failed:", e)
    sys.exit(1)

b64_payload = "{b64_data}"
key = {list(key)}
decoded_bytes, layer, total = decode_layer(b64_payload, key)

if layer < total:
    exec(decoded_bytes, globals())
else:
    exec(decoded_bytes, globals())
'''

    return runner_code.encode()

def generate_recursive_layers(original_code_bytes, charset, layers=10):
    key = [random.randint(1, 255) for _ in range(32)]
    code = original_code_bytes
    for i in range(layers, 0, -1):
        code = build_layer(code, charset, key, i, layers)
    return code

def main():
    print("[*] Hyper Obfuscator - Max Complexity Runner")
    out_path = input("Enter output filename (e.g. hyper_obf.py): ").strip()
    if not out_path.endswith(".py"):
        out_path += ".py"

    src_path = input("Enter path to Python script to obfuscate: ").strip()
    if not os.path.isfile(src_path):
        print("[x] File not found.")
        return

    # Prevent overwriting input file
    if os.path.abspath(src_path) == os.path.abspath(out_path):
        print("[x] Output file cannot overwrite the input file!")
        return

    with open(src_path, "rb") as f:
        original_code = f.read()

    charset = generate_charset()
    layers = 10

    print(f"[*] Generating {layers} recursive layers of obfuscation...")
    hyper_code = generate_recursive_layers(original_code, charset, layers)

    with open(out_path, "wb") as f:
        f.write(hyper_code)

    print(f"[✓] Hyper obfuscated runner saved to: {out_path}")
    print("[!] Warning: File size will be large and startup slow.")

if __name__ == "__main__":
    main()
