# Privacy notes

The public repository removes Telasi subscriber/account numbers and exact residential addresses.

Do not commit:

- private mappings between `SITE_A` / `SITE_B` and real subscriber numbers;
- exact residential addresses unless necessary, consented to, and intentionally disclosed;
- screenshots containing unrelated personal information;
- phone exports containing unrelated SMS traffic;
- browser HAR/netlog/network traces unless they have been specifically reviewed and redacted for cookies, tokens, unrelated request metadata and personal identifiers.

The primary complaint to Telasi can identify the complainant's own subscriber number privately while citing the public repository for reproducible analysis.

The neighbor's multiple-property warning is a methodological/privacy constraint: do not publicly assert SITE_A's exact location unless the subscriber-to-property mapping has been privately confirmed.

Live API/runtime output belongs under ignored `artifacts/`, including Telasi API responses and refreshed WBES benchmark captures. Only deliberately reviewed source/benchmark snapshots with documented provenance should be promoted under `data/`.

The current WBES benchmark contains public aggregate/subgroup statistics rather than respondent-level microdata. Do not add respondent-level Enterprise Survey records to this repository unless their terms and disclosure risk have been separately reviewed.
