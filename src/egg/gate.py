"""Experimental evidence-driven decision rule; not a correctness oracle."""

REQUIRED = ('tests_available', 'tests_passed', 'contracts_checked',
            'contract_conflicts', 'neighbor_regressions', 'unresolved_critical_risks',
            'high_impact_change')


def decide(evidence):
    missing = [key for key in REQUIRED if key not in evidence]
    if missing:
        raise ValueError(f'Missing evidence field(s): {missing}')
    for key in ('tests_available', 'tests_passed', 'contracts_checked', 'high_impact_change'):
        if type(evidence[key]) is not bool:
            raise ValueError(f'{key} must be a boolean')
    for key in ('contract_conflicts', 'neighbor_regressions', 'unresolved_critical_risks'):
        if not isinstance(evidence[key], list):
            raise ValueError(f'{key} must be a list')

    reasons = []
    if evidence['contract_conflicts']:
        reasons.append('Observed contract mismatch')
    if evidence['neighbor_regressions']:
        reasons.append('Potential neighboring behavior regression')
    if evidence['unresolved_critical_risks']:
        reasons.append('Unresolved critical risk')
    if evidence['tests_available'] and not evidence['tests_passed']:
        reasons.append('Observed test failure')
    if evidence['high_impact_change']:
        reasons.append('High-impact change requires independent risk assessment')
    if reasons:
        return {"action": "escalate", "reasons": reasons,
                "instructions": "Request targeted independent review and concrete reproduction; recheck after repair."}
    if not evidence['tests_available'] or not evidence['contracts_checked']:
        return {"action": "verify", "reasons": ["Required verification evidence is missing"],
                "instructions": "Obtain test and contract evidence before making completion claims."}
    return {"action": "stop_extra_review", "reasons": ["Visible checks passed and no additional trigger was recorded"],
            "instructions": "Report exact checks performed and remaining unverified risks; hidden evaluation is separate."}
