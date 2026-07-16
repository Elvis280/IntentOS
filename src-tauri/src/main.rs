#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::Manager;

#[tauri::command]
fn set_click_through(window: tauri::Window, ignore: bool) {
    if let Err(e) = window.set_ignore_cursor_events(ignore) {
        eprintln!("Failed to set_ignore_cursor_events: {}", e);
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![set_click_through])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
