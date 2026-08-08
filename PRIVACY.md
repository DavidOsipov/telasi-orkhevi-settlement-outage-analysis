# Privacy notes

The public repository removes Telasi subscriber/account numbers, apartment numbers and the exact residential building address.

`SITE_A` and `SITE_B` are stable pseudonymous **resident-source IDs for the same Orkhevi building**, not public location identifiers.

Do not commit:

- mappings between `SITE_A` / `SITE_B` and real subscriber numbers or apartment numbers;
- the exact residential address unless necessary, consented to and intentionally disclosed;
- screenshots containing unrelated personal information;
- phone exports containing unrelated SMS traffic;
- browser HAR/netlog/network traces unless specifically reviewed and redacted for cookies, tokens, unrelated request metadata and personal identifiers.

The primary complaint to Telasi can identify the complainant's own subscriber number privately while citing the public repository for reproducible analysis.

The neighbor may receive Telasi messages for other properties generally. This is still privacy-relevant context, but the pseudonymized SITE_A transcript used in the repository is treated methodologically as the same Orkhevi building as SITE_B; do not publish the private subscriber-to-property mapping.

Live API/runtime output belongs under ignored `artifacts/`, including Telasi API responses and refreshed WBES benchmark captures. Only deliberately reviewed source/benchmark material with documented provenance should be promoted under `data/`.

The current WBES benchmark contains public aggregate/subgroup statistics rather than respondent-level microdata. Do not add respondent-level Enterprise Survey records to this repository unless source terms, necessity and disclosure risk have been separately reviewed.
