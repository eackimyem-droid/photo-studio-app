mod commands;

use commands::{init_python_sidecar, send_to_python, kill_python_sidecar, SidecarState};
use std::sync::Mutex;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(SidecarState(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            init_python_sidecar,
            send_to_python,
            kill_python_sidecar
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}