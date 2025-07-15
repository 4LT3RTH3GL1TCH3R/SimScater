import os, random, string, json, zlib, base64, time

def generate_charset():
    return list(set(string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/`~"))

def xor_bytes(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def generate_mapping(charset, char_per_byte):
    mapping = {}
    used = set()
    for b in range(256):
        while True:
            s = ''.join(random.choices(charset, k=char_per_byte))
            if s not in used:
                mapping[b] = s
                used.add(s)
                break
    return mapping

def insert_noise(encoded, charset, ratio, char_per_byte):
    total_real = len(encoded)
    noise_count = int(total_real * ratio)
    positions = list(range(total_real + noise_count))
    random.shuffle(positions)
    real_pos = sorted(positions[:total_real])
    noise_pos = sorted(set(positions[total_real:]))
    result = []
    real_iter = iter(encoded)
    for i in range(total_real + noise_count):
        if i in noise_pos:
            result.append(''.join(random.choices(charset, k=char_per_byte)))
        else:
            result.append(next(real_iter))
    return result, noise_pos

def encrypt_mapping(mapping, key):
    raw = json.dumps(mapping).encode()
    enc = xor_bytes(raw, key)
    return base64.b64encode(enc).decode()

def build_layer(code_bytes, charset, key, layer_num, total_layers, noise_ratio, char_per_byte):
    print(f"[+] Obfuscating Layer {layer_num}/{total_layers}")
    mapping = generate_mapping(charset, char_per_byte)
    encoded = [mapping[b] for b in code_bytes]
    noisy_encoded, noise_pos = insert_noise(encoded, charset, noise_ratio, char_per_byte)
    enc_mapping = encrypt_mapping(mapping, key)

    payload = {
        "mapping": enc_mapping,
        "encoded": noisy_encoded,
        "noise_positions": noise_pos,
        "layer": layer_num,
        "total_layers": total_layers
    }

    comp = zlib.compress(json.dumps(payload).encode())
    b64 = base64.b64encode(comp).decode()

    runner = f"""
import zlib, base64, json

def xor_bytes(d, k): return bytes([b ^ k[i % len(k)] for i, b in enumerate(d)])
def decrypt_mapping(enc, k): return json.loads(xor_bytes(base64.b64decode(enc), k).decode())
def decode(b64_payload, k):
 compressed = base64.b64decode(b64_payload)
 payload = json.loads(zlib.decompress(compressed).decode())
 mapping = decrypt_mapping(payload['mapping'], k)
 inv = {{v: int(k) for k, v in mapping.items()}}
 filtered = [e for i, e in enumerate(payload['encoded']) if i not in set(payload['noise_positions'])]
 return bytes([inv[e] for e in filtered]), payload['layer'], payload['total_layers']

data = \"{b64}\"
key = {key}
decoded, layer, total = decode(data, key)
exec(decoded, globals()) if layer == total else exec(decoded)
"""
    return runner.encode()

def recursive_obfuscate(code_bytes, charset, layers, noise_ratio, char_per_byte):
    key = [random.randint(1, 255) for _ in range(16)]
    for i in range(layers, 0, -1):
        code_bytes = build_layer(code_bytes, charset, key, i, layers, noise_ratio, char_per_byte)
    return code_bytes

def main():
    print("=== HYPERMAX Obfuscator ===")
    output_name = input("Output filename (.py): ").strip()
    if not output_name.endswith(".py"):
        output_name += ".py"

    target_path = input("Path to Python script to obfuscate: ").strip()
    if not os.path.isfile(target_path):
        print("[x] File not found.")
        return
    if os.path.abspath(output_name) == os.path.abspath(target_path):
        print("[x] Output file cannot overwrite source.")
        return

    with open(target_path, "rb") as f:
        code = f.read()

    charset = generate_charset()
    print("[*] Obfuscating with 25 layers, 10x noise, 1000-char/byte...")
    start = time.time()
    result = recursive_obfuscate(code, charset, layers=25, noise_ratio=10, char_per_byte=1000)
    elapsed = time.time() - start

    with open(output_name, "wb") as f:
        f.write(result)

    print(f"[✓] Obfuscated file saved to: {output_name}")
    print(f"[i] Completed in {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
