# Using the GitHub repository

Repository: https://github.com/Kimeiga/evidence-gated-goldfish

Clone and run the deterministic checks:

```bash
git clone https://github.com/Kimeiga/evidence-gated-goldfish.git
cd evidence-gated-goldfish
python -m pip install -e .
python -m unittest discover -s tests -v
python benchmarks/architecture-review/prepare.py egm
```

The repository is currently public. Its benchmark fixtures are sanitized. Keep the hidden defect key, credentials, agent transcripts, raw local tasks, and proprietary code outside the public Git history. The checked-in CI workflow does not call paid inference APIs.

The `$30` budget ledger tracks intended reservations locally; it cannot guarantee provider billing limits. Configure billing caps at the provider before enabling any paid runs.
