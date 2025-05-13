use nix_remote::App;
use nix_remote::Config;

fn main() -> miette::Result<()> {
    let config = Config::new()?;
    App::new(config).run()
}
