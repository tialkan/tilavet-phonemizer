# Validation Model Initialization Summary

Total ayahs: 35

## Status Distribution

- candidate_v1: 35

## Review Status

- Reviewers who have voted: 0 (seed state)
- Agreement consensus: 0 / 35 ayahs
- Ready for LLM hafiz review: ✓

## Fields Added

Each ayah now has:

- `status`: Current validation state (candidate_v1)
- `reviews`: Dict for LLM hafiz verdicts {reviewer_name: {verdict, date, notes}}
- `agreement`: Metrics {total_reviewers, consensus, percent}

