# Git Authorship Conversion

## Summary

All commits in this repository have been rewritten to have Brandon (brandon@ankhstudio.com) as both the author and committer.

**Total commits converted:** 31

## Changes Made

### Original Commit History

Before the conversion, the repository contained commits from multiple authors:
- **copilot-swe-agent[bot]** (198982749+Copilot@users.noreply.github.com)
- **Brandon** (brandon@ankhstudio.com) - as author
- **Brandon Coburn** (brandon@bazingastudios.com) - different email
- **GitHub** (noreply@github.com) - as committer

### After Conversion

All commits now have:
- **Author**: Brandon <brandon@ankhstudio.com>
- **Committer**: Brandon <brandon@ankhstudio.com>

## Technical Details

The conversion was performed using `git filter-branch` with the following environment filter:

```bash
git filter-branch --env-filter '
CORRECT_NAME="Brandon"
CORRECT_EMAIL="brandon@ankhstudio.com"

export GIT_AUTHOR_NAME="$CORRECT_NAME"
export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
export GIT_COMMITTER_NAME="$CORRECT_NAME"
export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
' -- --all
```

## Important Notes

- **No code changes**: Only commit metadata (author and committer information) was modified
- **File integrity**: All files and their contents remain exactly as they were
- **Commit messages**: All original commit messages were preserved
- **Commit dates**: Original author dates and commit dates were preserved

## Verification

You can verify the authorship conversion by running:

```bash
git log --format="%H %an <%ae> %cn <%ce> %s"
```

All commits should show Brandon as both author and committer.
