import os, random, string, json, zlib, base64, time

def generate_charset():
    base = string.ascii_letters + string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/`~"
    extra = [chr(i) for i in range(0x2500, 0x257F)] + \
            [chr(i) for i in range(0x2600, 0x26FF)] + \
            [chr(i) for i in range(0x1F300, 0x1F64F)]
    charset = list(set(base + symbols) | set(extra))
    return charset

def xor_bytes(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def generate_mapping(charset):
    mapping = {}
    used = set()
    # 500,000 characters per byte mapping — insane memory/time cost
    for b in range(256):
        while True:
            s = ''.join(random.choices(charset, k=500_000))
            if s not in used:
                mapping[b] = s
                used.add(s)
                break
    return mapping

def insert_noise(encoded, charset):
    total_real = len(encoded)
    noise_ratio = 50_000  # 50,000x noise — absolutely brutal
    noise_count = total_real * noise_ratio
    positions = list(range(total_real + noise_count))
    random.shuffle(positions)
    real_positions = sorted(positions[:total_real])
    noise_positions = sorted(positions[total_real:])
    noisy_encoded = []
    real_iter = iter(encoded)
    noise_len = 500_000  # same length for noise strings

    for i in range(total_real + noise_count):
        if i in noise_positions:
            noisy_encoded.append(''.join(random.choices(charset, k=noise_len)))
        else:
            noisy_encoded.append(next(real_iter))
    return noisy_encoded, noise_positions

def encrypt_mapping(mapping, key):
    raw = json.dumps(mapping).encode()
    encrypted = xor_bytes(raw, key)
    return base64.b64encode(encrypted).decode()

def build_layer(code_bytes, charset, key, layer_num, total_layers):
    print(f"[!] Building layer {layer_num} of {total_layers} (prepare to wait hours/days)...")
    mapping = generate_mapping(charset)
    encoded = [mapping[b] for b in code_bytes]
    noisy_encoded, noise_positions = insert_noise(encoded, charset)
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

    runner_code = f'''
import zlib, base64, json, sys

def xor_bytes(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def decrypt_mapping(enc_mapping, key):
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

b64_payload = "{b64_data}"
key = {list(key)}
decoded_bytes, layer, total = decode_layer(b64_payload, key)

if layer < total:
    exec(decoded_bytes, globals())
else:
    exec(decoded_bytes, globals())
'''

    return runner_code.encode()

def generate_recursive_layers(original_code_bytes, charset, layers):
    key = [random.randint(1, 255) for _ in range(64)]  # larger key
    code = original_code_bytes
    for i in range(layers, 0, -1):
        code = build_layer(code, charset, key, i, layers)
    return code

def main():
    out_path = input("Enter output filename (e.g. mega_obf.py): ").strip()
    if not out_path.endswith(".py"):
        out_path += ".py"

    src_path = input("Enter path to script to obfuscate: ").strip()
    if not os.path.isfile(src_path):
        print("[x] File not found.")
        return

    if os.path.abspath(src_path) == os.path.abspath(out_path):
        print("[x] Output file cannot overwrite input file!")
        return

    with open(src_path, "rb") as f:
        original_code = f.read()

    charset = generate_charset()
    layers = 1000  # insane recursion depth

    print(f"[!] Starting insane obfuscation: {layers} layers, 500k chars/byte mapping, 50k noise ratio...")
    start = time.time()
    hyper_code = generate_recursive_layers(original_code, charset, layers)
    elapsed = time.time() - start
    print(f"[!] Finished obfuscation in {elapsed / 3600:.2f} hours")

    with open(out_path, "wb") as f:
        f.write(hyper_code)

    print(f"[✓] Obfuscated script saved to: {out_path}")

if __name__ == "__main__":
    main()
