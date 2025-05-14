use base64::prelude::Engine;
use base64::prelude::BASE64_STANDARD;
use camino::Utf8PathBuf;
use miette::Context;
use miette::IntoDiagnostic;
use serde::Deserialize;
use uname::uname;

#[derive(Debug, Default, Deserialize, PartialEq)]
#[serde(default, deny_unknown_fields)]
pub struct Builder {
    host: String,
    systems: Vec<String>,
    private_key: Option<Utf8PathBuf>,
    max_builds: Option<usize>,
    speed_factor: Option<f32>,
    features: Vec<String>,
    mandatory_features: Vec<String>,
    public_key: Option<String>,
}

impl Builder {
    pub fn darwin_builder() -> miette::Result<Self> {
        let system = format!("{}-linux", darwin_builder_arch()?);

        let max_builds = std::thread::available_parallelism()
            .into_diagnostic()
            .wrap_err("Failed to get parallelism estimate")?;

        Ok(Self {
            host: "ssh-ng://builder@linux-builder".into(),
            systems: vec![system],
            private_key: Some(Utf8PathBuf::from("/etc/nix/builder_ed25519")),
            max_builds: Some(max_builds.into()),
            speed_factor: None,
            features: vec![
                "benchmark".into(),
                "big-parallel".into(),
            ],
            mandatory_features: Vec::new(),
            public_key: Some("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJBWcxb/Blaqt1auOtE+F8QUWrUotiC5qBJ+UuEWdVCb root@nixos\n".into()),
        })
    }

    pub fn as_nix_config(&self) -> String {
        let mut ret = self.host.clone();

        ret.push(' ');
        if self.systems.is_empty() {
            ret.push('-');
        } else {
            ret.push_str(&self.systems.join(","));
        }

        ret.push(' ');
        match &self.private_key {
            Some(private_key) => ret.push_str(private_key.as_str()),
            None => {
                ret.push('-');
            }
        }

        ret.push(' ');
        match self.max_builds {
            Some(max_builds) => ret.push_str(&max_builds.to_string()),
            None => ret.push('-'),
        }

        ret.push(' ');
        match self.speed_factor {
            Some(speed_factor) => ret.push_str(&speed_factor.to_string()),
            None => ret.push('-'),
        }

        ret.push(' ');
        if self.features.is_empty() {
            ret.push('-');
        } else {
            ret.push_str(&self.features.join(","));
        }

        ret.push(' ');
        if self.mandatory_features.is_empty() {
            ret.push('-');
        } else {
            ret.push_str(&self.mandatory_features.join(","));
        }

        ret.push(' ');
        match &self.public_key {
            Some(public_key) => ret.push_str(&BASE64_STANDARD.encode(public_key)),
            None => ret.push('-'),
        }

        ret
    }
}

fn darwin_builder_arch() -> miette::Result<String> {
    let uname = uname()
        .into_diagnostic()
        .wrap_err("Failed to get `uname`")?;
    match uname.machine.as_str() {
        "arm64" => Ok("aarch64".into()),
        "x86_64" => Ok(uname.machine),
        _ => {
            tracing::debug!(uname_machine = %uname.machine, "Unknown `uname -m`");
            Ok(uname.machine)
        }
    }
}
