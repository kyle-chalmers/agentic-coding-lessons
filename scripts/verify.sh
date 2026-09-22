#!/usr/bin/env bash
# Verification gate for agentic-coding-lessons.
#
# CI mode (default): everything that needs no private input.
# Release mode (--release --denylist-file FILE): adds the literal denylist scan and, when
# --verdicts-dir and --ledger are given, the verdict-hash binding check. Release mode
# refuses to run without a denylist so a release check can never pass by accident.
#
# Usage: scripts/verify.sh [--release --denylist-file F] [--offline] [--verdicts-dir D --ledger L]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RELEASE=0; DENY=""; OFFLINE=0; VERDICTS=""; LEDGER=""; ALLOW_INCONCLUSIVE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --release) RELEASE=1 ;;
    --denylist-file) DENY="$2"; shift ;;
    --offline) OFFLINE=1 ;;
    --verdicts-dir) VERDICTS="$2"; shift ;;
    --ledger) LEDGER="$2"; shift ;;
    --allow-inconclusive) ALLOW_INCONCLUSIVE=1 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done
if [ "$RELEASE" = 1 ] && { [ -z "$DENY" ] || [ -z "$VERDICTS" ] || [ -z "$LEDGER" ]; }; then
  echo "verify.sh: --release requires --denylist-file, --verdicts-dir and --ledger (release mode never skips the verdict-binding check)" >&2; exit 2
fi

fails=0
step() { printf '\n== %s\n' "$1"; }
ok()   { printf 'PASS  %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

step "manifest allowlist"
if [ ! -f MANIFEST ]; then bad "MANIFEST missing"; else
  actual="$(find . -type f -not -path './.git/*' -not -path '*/__pycache__/*' -not -path './.ruff_cache/*' -not -path './.pytest_cache/*' -not -path './.venv/*' | sed 's|^\./||' | LC_ALL=C sort)"
  expected="$(grep -v '^\s*#' MANIFEST | grep -v '^\s*$' | LC_ALL=C sort)"
  if [ "$actual" = "$expected" ]; then ok "tree matches MANIFEST ($(printf '%s\n' "$expected" | wc -l | tr -d ' ') files)"; else
    bad "tree differs from MANIFEST"; diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/      /'; fi
fi

step "no symlinks or submodules"
links="$(find . -type l -not -path './.git/*')"
[ -z "$links" ] && ok "no symlinks" || { bad "symlinks present"; printf '%s\n' "$links"; }
if [ -d .git ]; then
  modes="$(git ls-files --stage | awk '$1=="120000"||$1=="160000"')"
  [ -z "$modes" ] && ok "no symlink/gitlink modes in index" || { bad "symlink/gitlink modes in index"; printf '%s\n' "$modes"; }
fi

step "lessons.json schema + cross-entry rules"
python3 scripts/check_lessons.py && ok "check_lessons" || bad "check_lessons"

step "rendered markdown equals lessons.json"
python3 scripts/render.py --check && ok "render --check" || bad "render --check"

step "no em or en dashes"
if command -v rg >/dev/null; then
  if rg -n --glob '!.git' '[\x{2013}\x{2014}]' . ; then bad "dashes found"; else ok "no U+2013/U+2014"; fi
else
  if python3 - <<'PY'
import os,sys,re
bad=0
for root,dirs,files in os.walk('.'):
    dirs[:]=[d for d in dirs if d!='.git']
    for f in files:
        p=os.path.join(root,f)
        try: t=open(p,encoding='utf-8').read()
        except Exception: continue
        for i,l in enumerate(t.splitlines(),1):
            if re.search('[\\u2013\\u2014]',l): print(f"{p}:{i}"); bad+=1
sys.exit(1 if bad else 0)
PY
  then ok "no U+2013/U+2014"; else bad "dashes found"; fi
fi

step "no home-directory paths"
pat='/Use''rs/|/ho''me/[a-z]|[A-Za-z]:\\\\Use''rs\\\\'
if rg -n --glob '!.git' --glob '!scripts/verify.sh' --glob '!scripts/scrub_check.py' "$pat" . ; then bad "home paths found"; else ok "no home paths"; fi

step "secrets (gitleaks)"
if command -v gitleaks >/dev/null; then
  gl_out="$(mktemp)"; trap 'rm -f "$gl_out"' EXIT
  if gitleaks dir . --redact --no-banner --exit-code 1 >"$gl_out" 2>&1 || gitleaks detect --no-git -s . --redact --no-banner --exit-code 1 >"$gl_out" 2>&1; then ok "gitleaks clean"; else bad "gitleaks findings"; tail -20 "$gl_out"; fi
else
  bad "gitleaks not installed"
fi

step "structural leak scan"
python3 scripts/scrub_check.py . --exclude scripts/scrub_check.py && ok "structural scrub" || bad "structural scrub"

if [ "$RELEASE" = 1 ]; then
  step "literal denylist scan (release)"
  python3 scripts/scrub_check.py . --release --denylist-file "$DENY" --exclude scripts/scrub_check.py && ok "denylist scrub" || bad "denylist scrub"
  step "verdicts bound to bytes (release)"
  tool="${VERIFY_VERDICTS_TOOL:-$(dirname "$VERDICTS")/tools/check_verdicts.py}"
  if [ ! -f "$tool" ]; then bad "verdict checker not found at $tool"; else
    python3 "$tool" --lessons lessons/lessons.json --results "$VERDICTS" --ledger "$LEDGER" && ok "verdict binding" || bad "verdict binding"; fi
fi

step "links"
if [ "$OFFLINE" = 1 ]; then python3 scripts/check_links.py --offline && ok "local links" || bad "local links";
else
  link_out="$(python3 scripts/check_links.py 2>&1)"; link_rc=$?; printf '%s\n' "$link_out"
  if [ "$link_rc" != 0 ]; then bad "confirmed broken links";
  elif [ "$RELEASE" = 1 ] && [ "$ALLOW_INCONCLUSIVE" = 0 ] && printf '%s' "$link_out" | grep -q '^INCONCLUSIVE:'; then bad "inconclusive external links in release mode (resolve them, or pass --allow-inconclusive after checking by hand)";
  else ok "links (no confirmed broken links)"; fi
fi

printf '\n== summary: %s failure(s)\n' "$fails"
[ "$fails" = 0 ]
