import os
import platform
import subprocess
import shutil

def build_executable():
    print("🚀 ចាប់ផ្តើម Build Python Engine ជា Executable Binary...")

    # ១. ស្វែងរកប្រព័ន្ធប្រតិបត្តិការ (Windows ឬ macOS)
    system_os = platform.system().lower()
    arch = platform.machine().lower()

    # កំណត់ឈ្មោះ Output Executable តាមស្តង់ដារ Tauri Sidecar Naming Convention
    if system_os == "windows":
        target_name = f"python-engine-x86_64-pc-windows-msvc.exe"
    elif system_os == "darwin":
        target_name = f"python-engine-aarch64-apple-darwin" if "arm" in arch or "aarch64" in arch else "python-engine-x86_64-apple-darwin"
    else:
        target_name = f"python-engine-x86_64-unknown-linux-gnu"

    # ២. កំណត់ Asset Paths (ONNX Models & Presets)
    models_dir = os.path.abspath("models")
    presets_dir = os.path.abspath("presets")

    # Separator សម្រាប់ PyInstaller: Windows ប្រើ ';' , Mac/Linux ប្រើ ':'
    sep = ";" if system_os == "windows" else ":"

    # ៣. រៀបចំ PyInstaller Command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",  # ឬប្រើ --onefile
        "--clean",
        "--name", target_name,
        "--add-data", f"{models_dir}{sep}models",
        "--add-data", f"{presets_dir}{sep}presets",
        "main.py"
    ]

    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # ៤. ចម្លង Output Binary ទៅកាន់ `src-tauri/bin/` ដោយស្វ័យប្រវត្តិ
    output_dist = os.path.join("dist", target_name)
    tauri_bin_dir = os.path.abspath("../src-tauri/bin")

    if not os.path.exists(tauri_bin_dir):
        os.makedirs(tauri_bin_dir)

    print(f"📦 ឆ្ពោះទៅកាន់: {tauri_bin_dir}")
    if os.path.isdir(output_dist):
        shutil.copytree(output_dist, os.path.join(tauri_bin_dir, target_name), dirs_exist_ok=True)
    else:
        shutil.copy2(output_dist, tauri_bin_dir)

    print("✅ Build Python Engine និងចម្លងទៅ Tauri Bin រួចរាល់ដោយជោគជ័យ!")

if __name__ == "__main__":
    build_executable()