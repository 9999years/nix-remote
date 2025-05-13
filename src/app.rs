use calm_io::stdout;
use camino::Utf8PathBuf;
use clap::CommandFactory;
use fs_err as fs;
use miette::miette;
use miette::IntoDiagnostic;
use tracing::instrument;

use crate::cli;
use crate::config::Config;

pub struct App {
    config: Config,
}

impl App {
    pub fn new(config: Config) -> Self {
        Self { config }
    }

    #[instrument(level = "trace", skip(self))]
    pub fn run(self) -> miette::Result<()> {
        if let Some(shell) = &self.config.cli.generate_completions {
            let mut clap_command = cli::Cli::command();
            clap_complete::generate(
                *shell,
                &mut clap_command,
                "nix-remote",
                &mut std::io::stdout(),
            );
            return Ok(());
        }

        #[cfg(feature = "clap_mangen")]
        if let Some(directory) = &self.config.cli.generate_manpages {
            use miette::Context;
            let clap_command = cli::Cli::command();
            clap_mangen::generate_to(clap_command, directory)
                .into_diagnostic()
                .wrap_err("Failed to generate man pages")?;
            return Ok(());
        }

        if let Some(maybe_config_path) = &self.config.cli.generate_config {
            self.config_init(maybe_config_path)?;
            return Ok(());
        }

        Ok(())
    }

    #[instrument(level = "trace", skip(self))]
    fn config_init(&self, maybe_config_path: &Option<Utf8PathBuf>) -> miette::Result<()> {
        let path = match &maybe_config_path {
            Some(path) => {
                if path == "-" {
                    stdout!("{}", Config::DEFAULT).into_diagnostic()?;
                    return Ok(());
                } else {
                    path
                }
            }
            None => &self.config.path,
        };

        if path.exists() {
            return Err(miette!("Default configuration file already exists: {path}"));
        }

        tracing::info!(
            %path,
            "Writing default configuration file"
        );

        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).into_diagnostic()?;
        }

        fs::write(path, Config::DEFAULT).into_diagnostic()?;

        Ok(())
    }
}
