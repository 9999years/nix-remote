use camino::Utf8PathBuf;
use clap::Parser;
use fs_err as fs;
use miette::Context;
use miette::IntoDiagnostic;
use serde::Deserialize;
use tracing::instrument;
use xdg::BaseDirectories;

use crate::builder::Builder;
use crate::cli::Cli;
use crate::install_tracing::install_tracing;

/// Configuration, both from the command-line and a user configuration file.
#[derive(Debug)]
pub struct Config {
    /// User directories.
    #[expect(dead_code)]
    pub(crate) dirs: BaseDirectories,
    /// User configuration file.
    pub file: ConfigFile,
    /// User configuration file path.
    pub path: Utf8PathBuf,
    /// Command-line options.
    pub cli: Cli,
}

impl Config {
    /// The contents of the default configuration file.
    pub const DEFAULT: &str = include_str!("../builders.toml");

    #[instrument(level = "trace")]
    pub fn new() -> miette::Result<Self> {
        let cli = Cli::parse();

        install_tracing(&cli.log)?;

        let dirs = BaseDirectories::with_prefix("nix-remote").into_diagnostic()?;

        let path = cli
            .config
            .as_ref()
            .map(|path| Ok(path.to_owned()))
            .unwrap_or_else(|| config_file_path(&dirs))?;

        let file = {
            if !path.exists() {
                ConfigFile::default()
            } else {
                toml::from_str(
                    &fs::read_to_string(&path)
                        .into_diagnostic()
                        .wrap_err("Failed to read configuration file")?,
                )
                .into_diagnostic()
                .wrap_err("Failed to deserialize configuration file")?
            }
        };

        Ok(Self {
            dirs,
            path,
            file,
            cli,
        })
    }
}

fn config_file_path(dirs: &BaseDirectories) -> miette::Result<Utf8PathBuf> {
    let mut config_home: Utf8PathBuf = dirs.get_config_home().try_into().into_diagnostic()?;

    config_home.push("nix");
    config_home.push(ConfigFile::FILE_NAME);

    Ok(config_home)
}

/// Configuration file format.
///
/// For documentation, see the default configuration file (`../builders.toml`).
///
/// The default configuration file is accessible as [`Config::DEFAULT`].
#[derive(Debug, Default, Deserialize, PartialEq, Eq)]
#[serde(default, deny_unknown_fields)]
pub struct ConfigFile {
    builders: Vec<Builder>,
}

impl ConfigFile {
    pub const FILE_NAME: &str = "builders.toml";
}
