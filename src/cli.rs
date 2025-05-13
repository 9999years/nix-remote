use camino::Utf8PathBuf;
use clap::Parser;

/// A `git-worktree(1)` manager.
#[derive(Debug, Clone, Parser)]
#[command(version, author, about)]
#[command(max_term_width = 100)]
pub struct Cli {
    /// Log filter directives, of the form `target[span{field=value}]=level`, where all components
    /// except the level are optional.
    ///
    /// Try `debug` or `trace`.
    #[arg(long, default_value = "info", env = "NIX_REMOTE_LOG", global = true)]
    pub log: String,

    /// Path to the `builders.toml` configuration file.
    ///
    /// Default: `~/.config/nix/builders.toml`.
    #[arg(long)]
    pub config: Option<Utf8PathBuf>,

    /// Generate the default configuration file.
    ///
    /// If the path is not given, the default configuration path will be used
    /// (`~/.config/nix/builders.toml`).
    ///
    /// If the path is `-`, the configuration file will be written to stdout.
    #[arg(long)]
    pub generate_config: Option<Option<Utf8PathBuf>>,

    /// Generate shell completions.
    #[arg(long)]
    pub generate_completions: Option<clap_complete::shells::Shell>,

    /// Generate man pages to the given directory.
    #[cfg(feature = "clap_mangen")]
    #[arg(long)]
    pub generate_manpages: Option<camino::Utf8PathBuf>,
}
