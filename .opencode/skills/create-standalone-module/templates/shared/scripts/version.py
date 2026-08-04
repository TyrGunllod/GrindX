"""
scripts/version.py — Gera a proxima versao semver e o changelog a partir
de conventional commits (git log + tags). Padrao de export.py.

Uso:
    python scripts/version.py [--dry-run] [--no-tag]

Regras de bump:
    BREAKING CHANGE / `<tipo>!: ...`   -> MAJOR
    feat: ...                          -> MINOR
    fix:/refactor:/perf:/docs:/style:/build:/ci:/chore:/test: -> PATCH
    sem tag git -> primeira release: usa module.json.version (agrupa todos os commits)

A versao e gravada em TODAS as abas do frontend: cada frontend/*/shared/version.js
expoe o mesmo global `window.{module_upper}_VERSION`.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

STANDALONE_ROOT = Path(__file__).resolve().parent.parent
MODULE_JSON = STANDALONE_ROOT / "module.json"
VERSION_JS_FILES = sorted((STANDALONE_ROOT / "frontend").glob("*/shared/version.js"))
CHANGELOG = STANDALONE_ROOT / "CHANGELOG.md"

MODULE_VAR = "{module_upper}"

COMMIT_RE = re.compile(
    r'^(?P<type>feat|fix|refactor|perf|docs|style|build|ci|chore|test)'
    r'(?P<scope>\([^)]*\))?(?P<breaking>!)?:'
)
BREAKING_RE = re.compile(r'BREAKING CHANGE', re.IGNORECASE)
RELEASE_COMMIT_RE = re.compile(r'^docs: registrar changelog')

SECTION_LABELS = {
    'feat': 'Adicionado',
    'fix': 'Corrigido',
    'refactor': 'Refatorado',
    'perf': 'Performance',
    'docs': 'Documentacao',
    'style': 'Estilo',
    'build': 'Build',
    'ci': 'CI',
    'chore': 'Chore',
    'test': 'Testes',
}


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git " + " ".join(args) + " falhou: " + r.stderr.strip())
    return r.stdout


def get_last_tag():
    """Retorna a ultima tag vX.Y.Z (sem o 'v') ou None."""
    try:
        out = git("tag", "--list", "v*", "--sort=-v:refname")
    except RuntimeError:
        return None
    for t in out.splitlines():
        t = t.strip()
        if re.fullmatch(r'v\d+\.\d+\.\d+', t):
            return t[1:]
    return None


def get_commits(since_version):
    """Subjects dos commits desde a tag (ou de todos, se since_version for None).

    Exclui os commits de release do proprio script (docs: registrar changelog...),
    que ficam apos a tag e nao devem gerar bump nem entrar no changelog.
    """
    args = ["log", "--pretty=format:%s"]
    if since_version:
        args.insert(1, "v" + since_version + "..")
    commits = [l for l in git(*args).splitlines() if l]
    return [c for c in commits if not RELEASE_COMMIT_RE.match(c)]


def classify(subject):
    m = COMMIT_RE.match(subject)
    if not m:
        return None
    if m.group('breaking') or BREAKING_RE.search(subject):
        return 'major'
    if m.group('type') == 'feat':
        return 'minor'
    return 'patch'


def highest_bump(commits):
    kinds = [classify(c) for c in commits]
    if 'major' in kinds:
        return 'major'
    if 'minor' in kinds:
        return 'minor'
    if 'patch' in kinds:
        return 'patch'
    return None


def bump(version, kind):
    major, minor, patch = (int(x) for x in version.split('.'))
    if kind == 'major':
        return f"{major + 1}.0.0"
    if kind == 'minor':
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def read_manifest():
    return json.loads(MODULE_JSON.read_text(encoding="utf-8"))


def write_manifest(data):
    MODULE_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_section(version, commits):
    lines = [f"## [{version}] - {date.today().isoformat()}", ""]
    groups = {'feat': [], 'fix': [], 'refactor': [], 'perf': [], 'docs': [],
              'style': [], 'build': [], 'ci': [], 'chore': [], 'test': [], 'other': []}
    for c in commits:
        m = COMMIT_RE.match(c)
        groups[m.group('type') if m else 'other'].append(c)
    for key in SECTION_LABELS:
        if groups[key]:
            lines.append(f"### {SECTION_LABELS[key]}")
            lines.extend(f"- {c}" for c in groups[key])
            lines.append("")
    if groups['other']:
        lines.append("### Outros")
        lines.extend(f"- {c}" for c in groups['other'])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_changelog(section, dry_run):
    if CHANGELOG.exists():
        lines = CHANGELOG.read_text(encoding="utf-8").splitlines(keepends=True)
        header = []
        idx = 0
        while idx < len(lines) and not lines[idx].startswith("## "):
            header.append(lines[idx])
            idx += 1
        body = "".join(lines[idx:])
        new_content = "".join(header) + section + "\n" + body
    else:
        header = "# Changelog\n\nTodas as mudancas notaveis deste modulo.\n\n"
        new_content = header + section + "\n"
    if dry_run:
        print("[DRY-RUN] Atualizaria CHANGELOG.md")
    else:
        CHANGELOG.write_text(new_content, encoding="utf-8")
        print("CHANGELOG.md atualizado")


def update_version_js(version, dry_run):
    content = f'window.{MODULE_VAR}_VERSION = "{version}";\n'
    if dry_run:
        for f in VERSION_JS_FILES:
            print("[DRY-RUN] Atualizaria " + str(f))
        return
    if not VERSION_JS_FILES:
        print("Nenhuma aba frontend encontrada; version.js nao atualizado")
        return
    for f in VERSION_JS_FILES:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
        print("version.js atualizado: " + str(f))


def main():
    parser = argparse.ArgumentParser(
        description="Gera a proxima versao e o changelog a partir de conventional commits"
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas exibe o que seria feito")
    parser.add_argument("--no-tag", action="store_true", help="Nao cria a tag git da nova versao")
    args = parser.parse_args()

    try:
        last_version = get_last_tag()
        manifest = read_manifest()
        current = manifest["version"]

        if last_version:
            commits = get_commits(last_version)
            kind = highest_bump(commits)
            if not kind:
                print(f"Nenhum commit relevante desde v{last_version}; versao permanece {current}")
                return
            new_version = bump(last_version, kind)
        else:
            commits = get_commits(None)
            new_version = current

        print(f"Versao atual: v{last_version}" if last_version else f"Versao atual: {current} (sem tag)")
        print(f"Commits considerados: {len(commits)}")
        print(f"Nova versao: {new_version}")

        if args.dry_run:
            print("[DRY-RUN] Atualizaria module.json")
            update_version_js(new_version, dry_run=True)
            print("[DRY-RUN] Atualizaria CHANGELOG.md")
            if not args.no_tag:
                print(f"[DRY-RUN] Criaria a tag v{new_version}")
            return

        manifest["version"] = new_version
        write_manifest(manifest)
        print("module.json atualizado")

        update_version_js(new_version, dry_run=False)
        update_changelog(build_section(new_version, commits), dry_run=False)

        if not args.no_tag:
            git("tag", "v" + new_version)
            print("Tag criada: v" + new_version)
    except RuntimeError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
