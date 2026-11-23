"""Build the commit for the public repository (branch "public") from the files of the working tree.

Usage: python tools/veroeffentlichen.py "Commit message"
The private branch keeps the full history and the internal notes. The public branch gets one commit per call with a
selection of the tracked files: everything except INTERN, and docs/adressindex.md in a version that does not cite the
internal notes. The working tree and the normal index are not touched (a temporary index is used). Nothing is
uploaded: push the branch yourself, for example  git push <remote> public:main
The first call creates the branch without a parent (no history of the private branch); later calls add a commit.
Author and committer are taken from the git configuration of this repository (user.name, user.email).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = 'public'
# Tracked paths that stay private: internal working notes, notes on other projects of the forum, the statistics page
# (not part of the patch) and the installers of earlier versions (the current one replaces them, its change log lists them all).
INTERN = ('docs/HANDOFF.md', 'docs/forum-anstoss-juenger.md', 'ansicht/', 'patch-1.41/', 'patch-1.42/', 'patch-1.43/',
          'patch-1.44/', 'patch-1.45/', 'patch-1.46/', 'patch-1.47/', 'tools/patch141_bauen.py',
          'tools/patch141_test.ps1')


def git(*args, env=None, data=None):
    r = subprocess.run(['git', '-C', ROOT, *args], input=data, capture_output=True, env=env)
    if r.returncode:
        sys.exit(f'git {" ".join(args)}: {r.stderr.decode("utf-8", "replace")}')
    return r.stdout.decode('utf-8').strip()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if git('status', '--porcelain', '--untracked-files=no'):
        sys.exit('Es gibt nicht committete Änderungen; erst im privaten Zweig committen.')
    files = [f for f in git('ls-files').splitlines() if not f.startswith(INTERN)]
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp, 'index'))
        git('read-tree', '--empty', env=env)
        git('update-index', '--add', '--', *files, env=env)
        index = os.path.join(tmp, 'adressindex.md')
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'fundstellen_index.py'), '--oeffentlich', index],
                       check=True, capture_output=True)
        blob = git('hash-object', '-w', index)
        git('update-index', '--add', '--cacheinfo', f'100644,{blob},docs/adressindex.md', env=env)
        tree = git('write-tree', env=env)
    parent = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--verify', '--quiet', f'refs/heads/{BRANCH}'],
                            capture_output=True).stdout.decode().strip()
    if parent and git('rev-parse', f'{parent}^{{tree}}') == tree:
        sys.exit('Keine Änderung gegenüber dem letzten öffentlichen Stand.')
    commit = git('commit-tree', tree, *(['-p', parent] if parent else []), '-m', sys.argv[1])
    git('update-ref', f'refs/heads/{BRANCH}', commit)
    print(f'Zweig {BRANCH}: {commit[:8]} mit {len(files)} Dateien' + ('' if parent else ' (erster Commit, ohne Vorgänger)'))


if __name__ == '__main__':
    main()
