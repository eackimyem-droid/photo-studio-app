use tauri::{AppHandle, command, Emitter};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandEvent, CommandChild};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::Mutex;
use tauri::State;

// 1. រចនាសម្ព័ន្ធ Payload សម្រាប់ផ្ញើទៅ និងទទួលពី Python Sidecar
#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessRequest {
    pub command: String,
    pub payload: Value,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProcessResponse {
    pub status: String,
    pub data: Option<Value>,
    pub error: Option<String>,
}

// Global State សម្រាប់រក្សាទុក Process Child របស់ Python
pub struct SidecarState(pub Mutex<Option<CommandChild>>);

// 2. Command សម្រាប់ចាប់ផ្តើម (Spawn) Python Sidecar Engine
#[command]
pub async fn init_python_sidecar(
    app: AppHandle,
    state: State<'_, SidecarState>,
) -> Result<String, String> {
    let mut sidecar_lock = state.0.lock().map_err(|e| e.to_string())?;

    // ប្រសិនបើ Sidecar កំពុងដើរស្រាប់ មិនបាច់ Spawn ថ្មីទេ
    if sidecar_lock.is_some() {
        return Ok("Python sidecar is already running.".into());
    }

    // Spawn sidecar ដោយប្រើឈ្មោះដែលបានកំណត់ក្នុង tauri.conf.json ("python-engine")
    let (mut rx, child) = app
        .shell()
        .sidecar("python-engine")
        .map_err(|e| format!("Failed to create sidecar command: {}", e))?
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar process: {}", e))?;

    // រក្សាទុក Child handle
    *sidecar_lock = Some(child);

    // 3. Spawn Background Task សម្រាប់ស្តាប់ Output (stdout/stderr) ពី Python Engine
    let app_clone = app.clone();
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line_bytes) => {
                    if let Ok(line) = String::from_utf8(line_bytes) {
                        // ផ្ញើ Response ទៅកាន់ Frontend React តាមរយៈ Event "python-response"
                        let _ = app_clone.emit("python-response", line.trim());
                    }
                }
                CommandEvent::Stderr(line_bytes) => {
                    if let Ok(line) = String::from_utf8(line_bytes) {
                        eprintln!("[Python Sidecar Error]: {}", line.trim());
                        let _ = app_clone.emit("python-error", line.trim());
                    }
                }
                CommandEvent::Terminated(payload) => {
                    println!("[Python Sidecar Terminated]: Exit code {:?}", payload.code);
                    let _ = app_clone.emit("python-terminated", payload.code);
                    break;
                }
                _ => {}
            }
        }
    });

    Ok("✅ Python sidecar successfully spawned!".into())
}

// 4. Command សម្រាប់ផ្ញើ Command/Data ទៅកាន់ Python Sidecar (stdin)
#[command]
pub async fn send_to_python(
    state: State<'_, SidecarState>,
    command: String,
    payload: Value,
) -> Result<String, String> {
    let mut sidecar_lock = state.0.lock().map_err(|e| e.to_string())?;

    if let Some(child) = sidecar_lock.as_mut() {
        let req = ProcessRequest { command, payload };
        
        // Convert Request ទៅជា JSON String + "\n"
        let mut json_string = serde_json::to_string(&req).map_err(|e| e.to_string())?;
        json_string.push('\n');

        // សរសេរទិន្នន័យចូលទៅកាន់ stdin របស់ Python Process
        child
            .write(json_string.as_bytes())
            .map_err(|e| format!("Failed to write to sidecar stdin: {}", e))?;

        Ok("Request sent to Python successfully.".into())
    } else {
        Err("Python sidecar process is not running.".into())
    }
}

// 5. Command សម្រាប់បិទ Python Sidecar នៅពេលចាកចេញ
#[command]
pub async fn kill_python_sidecar(state: State<'_, SidecarState>) -> Result<String, String> {
    let mut sidecar_lock = state.0.lock().map_err(|e| e.to_string())?;

    if let Some(child) = sidecar_lock.take() {
        child.kill().map_err(|e| format!("Failed to kill sidecar: {}", e))?;
        Ok("Python sidecar process terminated.".into())
    } else {
        Ok("No active Python sidecar process found.".into())
    }
}