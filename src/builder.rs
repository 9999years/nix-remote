use serde::Deserialize;

#[derive(Debug, Default, Deserialize, PartialEq, Eq)]
#[serde(default, deny_unknown_fields)]
pub struct Builder {}
