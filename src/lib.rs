//! `nix-remote` is a Nix remote-builder wrapper.
//!
//! The `nix-remote` Rust library is a convenience and shouldn't be depended on. I do not
//! consider this to be a public/stable API and will make breaking changes here in minor version
//! bumps. If you'd like a stable `nix-remote` Rust API for some reason, let me know and we can maybe
//! work something out.

mod app;
mod builder;
mod cli;
mod config;
mod install_tracing;

pub use app::App;
pub use config::Config;
