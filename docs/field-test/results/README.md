# Field test results

One run of a step from [`../steps.json`](../steps.json) is two files written by `scripts/field_test.py record`:
`<date>-<step id>.json` (the record, `velisa/field-test-result@1`) and `<date>-<step id>.md` (the same for people).
They hold measurements, versions, the machine, and the sha256 of each medium; never the media, names or credentials.
`python3 scripts/field_test.py check` validates every record here; the scripts tests run it in CI.

No result has been recorded yet.
