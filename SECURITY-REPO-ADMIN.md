# Repo Administration (Public Sanitized)

## Default branch rename

```bash
git branch -m main public-sanitized
git push origin public-sanitized
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/public-sanitized
```

Keep a private branch with real artifacts in a separate private repo or branch.

## GitHub topic tags

Add repository topics:
- security-education
- red-team
- ethical-hacking
- defensive-research

## Evidence policy

- Only commit sanitized artifacts under `security-analysis-project/evidence/sanitized/`.
- Raw evidence, cracked secrets, and large logs are excluded via `.gitignore`.
