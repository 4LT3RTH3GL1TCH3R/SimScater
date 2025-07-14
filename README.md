# 🔐 SimScater – "Code Confusion Engine"

This project contains a Python-based **hyper-obfuscator** designed to transform any `.py` script into a bloated, encrypted, randomized, anti-reverse-engineering nightmare. A 20 KB script will balloon into a **10–20 MB single Python file** that runs the original logic — but hides it under extreme obfuscation layers.

---

## 🚀 What It Does

- ✅ Obfuscates every byte of your original script
- ✅ Encodes each byte into a **random 200–400 character string**
- ✅ Injects **300%+ randomized fake strings** (noise) that mimic the real ones
- ✅ Stores all data as a compressed + base64 payload
- ✅ Embeds that payload in a **self-contained `.py` runner**
- ✅ Uses a custom multi-layer decoder to reverse the chaos at runtime

---

## 🔐 Obfuscation Techniques Used

| Layer                      | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| **Per-byte expansion**     | Each byte → 200–400 char random string                                      |
| **Random mapping**         | Fresh mapping every time, no reused keys                                    |
| **Massive noise injection**| 3× more fake strings than real ones                                         |
| **Base64 + zlib wrapper**  | Compresses large garbage into a single blob                                 |
| **Multi-stage runner**     | base64 → zlib → JSON → decode → execute                                     |
| **Globals-aware exec**     | Executes in real Python global scope                                        |

---

## 📈 Reverse Engineering Difficulty

| Attacker Type          | Knows Format? | Estimated Time   | Realistic Reaction            |
|------------------------|---------------|------------------|-------------------------------|
| 🧑 Beginner             | ❌ No          | ❌ Never          | Rage quits instantly          |
| 🧠 Intermediate         | ❌ No          | 24–72+ hours      | Needs custom tools            |
| 🧠 Expert (cold)        | ❌ No          | 12–36 hours       | Deep manual reverse needed    |
| 🧠 Expert (informed)    | ✅ Yes         | 3–6 hours         | Still annoying and bloated    |
| 🤖 Automation tools     | ❌ No          | ⛔️ Fail entirely   | Can't parse randomized chaos  |

---

## 🧬 Technical Stats (for a 20 KB script)

| Metric                     | Result                            |
|----------------------------|-----------------------------------|
| Output file size           | 10–20 MB                          |
| Avg encoding per byte      | 200–400 chars                     |
| Total encoded strings      | 20,000 real + 60,000 fake         |
| Payload type               | zlib-compressed JSON, base64      |
| Final format               | Single executable `.py` file      |

---

## 💣 Why It's a Nightmare to Reverse

- 🔁 Every obfuscation is unique
- 🔊 No string patterns, no consistent length
- 🎭 Fake strings are indistinguishable from real ones
- 🧩 Encoding format is custom and undocumented
- 🧱 Multi-layer logic can't be flattened easily
- 🧼 No hints in the payload — it's just garbage without context

---

## 🛠️ Usage (Simple)

1. Run the `hyper_obfuscator.py` script.
2. Enter the path to your real `.py` source file.
3. Choose the output filename for the obfuscated runner.
4. Done — it generates a bloated `.py` file that runs the original code but reveals nothing.

---

## ☠️ Disclaimer

This is **not encryption**, and **not meant for malicious use**. It is purely for:
- Reverse engineering prevention
- Code protection
- Anti skidding

Reverse engineers: enjoy the migraine.

---
