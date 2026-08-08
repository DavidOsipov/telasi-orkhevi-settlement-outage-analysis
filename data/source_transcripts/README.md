# Source transcripts

These files contain redacted text transcripts of SMS messages supplied by residents.

They are **not forensic raw SMS exports** and do not preserve original receipt timestamps or device metadata.

- `site_a_sms_redacted.txt` — longer neighbor-supplied series.
- `site_b_sms_redacted.txt` — primary overlapping series used for the Orkhevi analysis.

Run:

```bash
python scripts/build_notifications.py
```

to regenerate `../derived/notifications.csv`.

Subscriber numbers are replaced with stable pseudonyms before publication.
