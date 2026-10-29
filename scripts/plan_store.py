#!/usr/bin/env python3
"""Local summary coverage and recoverable plan archiving (Python 3.9+, stdlib).

The agent supplies semantic summaries and requests user authorization. This helper
checks bytes, paths and explicit closed statuses; it cannot judge summary quality
or detect other conversations. Run in a coordinated workspace, not against
hostile concurrent filesystem writers. No model, network or Git operations.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

SUMMARY_MARKER = '<!-- plan-handoff:summary:v1 -->'
INDEX_MARKER = '<!-- plan-handoff:index:v1 -->'
SCHEMA = 'plan-handoff/summary-v1'
ARCHIVE_SCHEMA = 'plan-handoff/archive-v1'
CLOSED = {'completed', 'cancelled', 'superseded'}
MANIFEST = 'summary.manifest.json'
ZIP_MANIFEST = '_plan-handoff-archive.json'


class StoreError(Exception):
    """An input or safety precondition was not met; sources must be retained."""


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _root(path):
    p = Path(path).absolute()
    if p.is_symlink() or not p.is_dir():
        raise StoreError('The plan root must be an existing non-symlink directory')
    return p.resolve()


def _path(root, relative):
    name = str(relative)
    parts = PurePosixPath(name).parts
    if not parts or name.startswith('/') or '\\' in name or ':' in name or any(p in {'.', '..'} for p in name.split('/')):
        raise StoreError('Use a normalized relative path within the plan root')
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise StoreError('Symlink paths are not supported: ' + name)
    return p


def _source(root, name):
    p = _path(root, name)
    if PurePosixPath(name).parts[0] == 'archive' or name in {'summary.md', 'index.md'} or p.suffix != '.md':
        raise StoreError('Not a plan source: ' + name)
    if not p.is_file():
        raise StoreError('Plan source does not exist: ' + name)
    return p


def _read(path):
    if path.is_symlink() or not path.is_file():
        raise StoreError('Expected a regular non-symlink file: ' + str(path))
    return path.read_bytes()


def _text(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as error:
        raise StoreError('Managed documents must use UTF-8') from error


def _status(data):
    # Metadata is an unindented bullet in the document's opening section.
    # Examples, comments and later historical sections never grant eligibility.
    text = re.sub(r'<!--.*?(?:-->|\Z)', '', _text(data), flags=re.S)
    lines, fence = [], None
    for line in text.splitlines():
        if fence:
            if re.fullmatch(r' {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}[ \t]*', line):
                fence = None
            continue
        opening = re.match(r' {0,3}(`{3,}|~{3,})', line)
        if opening:
            fence = (opening[1][0], len(opening[1]))
            continue
        if re.match(r' {0,3}#{2,6}(?:[ \t]+|$)', line):
            break
        lines.append(line)
    matches = re.findall(r'^-[ \t]+(?:Task status|任务状态)[ \t]*[:：][ \t]*(.*?)[ \t]*$',
                         '\n'.join(lines), re.M | re.I)
    if len(matches) != 1:
        return 'unknown'
    value = matches[0].strip().rstrip('.。').lower()
    return {'已完成': 'completed', '已取消': 'cancelled', '已替代': 'superseded'}.get(value, value)


def _title(data):
    match = re.search(r'^#\s+(.+)$', _text(data), re.M)
    return match[1].strip() if match else 'Untitled plan'


def _markdown_files(root, archive_root=None):
    for folder, dirs, files in os.walk(root, followlinks=False):
        base = Path(folder)
        dirs[:] = [d for d in dirs if not (base / d).is_symlink()
                   and d not in {'.git', '.venv', 'node_modules'}
                   and (archive_root is None or base / d != archive_root)]
        for name in files:
            p = base / name
            if p.suffix == '.md' and not p.is_symlink():
                yield p


def scan(root):
    root = _root(root)
    return [{'path': p.relative_to(root).as_posix(), 'status': _status(_read(p)), 'title': _title(_read(p))}
            for p in sorted(_markdown_files(root, root / 'archive')) if p.name == 'plan.md']


def _summary(root):
    data = _read(_path(root, 'summary.md'))
    if not _has_marker(data, SUMMARY_MARKER):
        raise StoreError('No managed summary; ask whether to run plan-summary first')
    return data


def _has_marker(data, marker):
    # Recognize logical first lines without normalizing the hashed source bytes.
    return _text(data).splitlines()[:1] == [marker]


def _block(summary, task_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', task_id):
        raise StoreError('Entry IDs must be ASCII letters, digits, underscores or hyphens')
    start = '<!-- plan-handoff:entry:' + task_id + ' -->'
    end = '<!-- /plan-handoff:entry:' + task_id + ' -->'
    text = _text(summary)
    if text.count(start) != 1 or text.count(end) != 1:
        raise StoreError('Summary entry missing or duplicated: ' + task_id)
    left, right = text.index(start) + len(start), text.index(end)
    body = text[left:right]
    without_headings = re.sub(r'^\s*#+[^\n]*$', '', body, flags=re.M)
    substantive = re.sub(r'<!--.*?-->|\s+', '', without_headings, flags=re.S)
    if right < left or not substantive:
        raise StoreError('Summary entry has no substantive body: ' + task_id)
    return body.encode('utf-8')


def _load(root, required=True):
    p = _path(root, MANIFEST)
    if not p.exists():
        if required:
            raise StoreError('No coverage manifest; ask whether to run plan-summary first')
        return {'schema': SCHEMA, 'summary_sha256': None, 'entries': {}}
    try:
        data = json.loads(_read(p))
    except (ValueError, UnicodeDecodeError) as error:
        raise StoreError('Invalid summary manifest') from error
    if not isinstance(data, dict) or data.get('schema') != SCHEMA or not isinstance(data.get('entries'), dict):
        raise StoreError('Unrecognized manifest; do not overwrite it')
    for name, entry in data['entries'].items():
        _path(root, name)
        if not isinstance(entry, dict) or not isinstance(entry.get('task_id'), str):
            raise StoreError('Malformed source entry')
    return data


def _write(path, data):
    if path.is_symlink():
        raise StoreError('Cannot replace a symlink')
    fd, temp = tempfile.mkstemp(prefix='.plan-handoff-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _json_write(path, value):
    _write(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


@contextmanager
def _lock(root):
    p = _path(root, '.plan-handoff.lock')
    try:
        p.mkdir()
    except FileExistsError as error:
        raise StoreError('Another writer or interrupted operation holds .plan-handoff.lock; inspect before retrying') from error
    try:
        yield
    finally:
        p.rmdir()


def cover(root, plan, task_id, evidence=None):
    root = _root(root)
    with _lock(root):
        source = _read(_source(root, plan))
        status = _status(source)
        if status not in CLOSED:
            raise StoreError('Only completed, cancelled or superseded plans can be covered')
        summary = _summary(root)
        body = _block(summary, task_id)
        manifest = _load(root, required=False)
        for name, entry in manifest['entries'].items():
            previous_body = _block(summary, entry['task_id'])
            if entry.get('archive') and _hash(previous_body) != entry.get('entry_sha256'):
                raise StoreError('Archived result changed; preserve it and append an explicit correction')
            if name != plan and entry['task_id'] == task_id:
                raise StoreError('A summary entry belongs to another plan')
        old = manifest['entries'].get(plan)
        if old and old.get('archive'):
            raise StoreError('An archived source cannot be overwritten by a new live plan')
        manifest['entries'][plan] = {'task_id': task_id, 'status': status, 'source_sha256': _hash(source),
                                     'entry_sha256': _hash(body), 'evidence': list(evidence or [])}
        manifest['summary_sha256'] = _hash(summary)
        _json_write(_path(root, MANIFEST), manifest)
        return manifest


def refresh(root):
    """Accept overview-only edits; changed result blocks require targeted coverage."""
    root = _root(root)
    with _lock(root):
        summary, manifest = _summary(root), _load(root)
        for entry in manifest['entries'].values():
            if _hash(_block(summary, entry['task_id'])) != entry.get('entry_sha256'):
                raise StoreError('A result entry changed; refresh cannot certify new claims')
        manifest['summary_sha256'] = _hash(summary)
        _json_write(_path(root, MANIFEST), manifest)
        return manifest


def _text_links_to(text, parent, target):
    targets = re.findall(r'\]\(<?([^\s)>]+)>?(?:\s+["\'].*?["\'])?\)', text)
    # Also inspect reference-style definitions; unknown formats need agent review.
    targets += re.findall(r'^\s*\[[^\]]+\]:\s*<?([^\s>]+)', text, re.M)
    for link in targets:
        parsed = urlsplit(link)
        if not parsed.scheme and parsed.path and (parent / unquote(parsed.path)).resolve() == target:
            return True
    return False


def _links_to(document, target):
    return _text_links_to(_text(_read(document)), document.parent, target)


def preview(root, plans=None, reference_roots=None):
    root = _root(root)
    summary, manifest = _summary(root), _load(root)
    requested = list(dict.fromkeys(plans if plans is not None else
                                  list(manifest['entries']) + [r['path'] for r in scan(root)]))
    eligible, retained = [], {}
    for name in requested:
        _path(root, name)
        entry = manifest['entries'].get(name)
        if entry and entry.get('archive') and not (root / name).exists():
            continue
        try:
            source = _read(_source(root, name))
            if _status(source) not in CLOSED:
                raise StoreError('active, pending, or unknown status')
            if not entry:
                raise StoreError('not covered by summary')
            if entry.get('archive'):
                raise StoreError('already archived; original retained after interruption; inspect before retrying')
            if _hash(summary) != manifest.get('summary_sha256'):
                raise StoreError('summary changed; ask to refresh or summarize first')
            if _hash(source) != entry.get('source_sha256') or _status(source) != entry.get('status'):
                raise StoreError('source changed after summary')
            if _hash(_block(summary, entry['task_id'])) != entry.get('entry_sha256'):
                raise StoreError('summary entry changed')
            rewritten = _redirect_summary(summary, root, [name], 'archive/preview.zip')
            if _text_links_to(_text(rewritten), root, root / name):
                raise StoreError('summary reference cannot be safely redirected; retain source')
            eligible.append(name)
        except StoreError as error:
            retained[name] = str(error)
    docs = set(_markdown_files(root, root / 'archive'))
    for ref_root in reference_roots or []:
        ref = _root(ref_root)
        docs.update(_markdown_files(ref, root / 'archive'))
    # Even a selected source may remain after a removal failure. Preserve its
    # referenced targets rather than assuming the entire batch will disappear.
    blocked = {}
    for name in eligible:
        for doc in sorted(docs):
            if doc == root / name or doc == root / 'summary.md':
                continue
            if doc == root / 'index.md' and _has_marker(_read(doc), INDEX_MARKER):
                continue
            if _links_to(doc, root / name):
                blocked[name] = 'referenced by existing document: ' + str(doc)
                break
    eligible = [n for n in eligible if n not in blocked]
    retained.update(blocked)
    return {'eligible': eligible, 'retained': retained,
            'reference_scope': [str(root)] + [str(Path(p).resolve()) for p in reference_roots or []]}


def _verify_archive(path, expected=None):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise StoreError('Archive CRC failure')
        metadata = json.loads(z.read(ZIP_MANIFEST))
        if metadata.get('schema') != ARCHIVE_SCHEMA or not isinstance(metadata.get('files'), dict):
            raise StoreError('Unknown archive format')
        if set(z.namelist()) != set(metadata['files']) | {ZIP_MANIFEST} or len(z.namelist()) != len(set(z.namelist())):
            raise StoreError('Unexpected or duplicate archive members')
        if expected is not None and metadata['files'] != expected:
            raise StoreError('Archive manifest differs from selected sources')
        for name, entry in metadata['files'].items():
            if _hash(z.read(name)) != entry['source_sha256']:
                raise StoreError('Archive content hash mismatch')
        return metadata


def _remove_source(root, name, expected):
    p = _source(root, name)
    if _hash(_read(p)) != expected:
        raise StoreError('Source changed after backup; retained')
    p.unlink()
    parent = p.parent
    while parent != root:
        try:
            parent.rmdir()  # Never recursively remove files, evidence or directories.
        except OSError:
            break
        parent = parent.parent


def _redirect_summary(summary, root, names, archive_name):
    text = _text(summary)
    for name in names:
        # Only unambiguous inline links are rewritten. The agent reviews other formats.
        pattern = r'\]\(<?' + re.escape(name) + r'(?:#[^\s)>]*)?>?\)'
        text = re.sub(pattern, '](' + archive_name + ') (member: `' + name + '`)', text)
    return text.encode()


def _index(root, manifest):
    lines = [INDEX_MARKER, '# Plan index', '', '[Results overview](summary.md)', '', '## Current plans', '']
    current = {row['path']: row for row in scan(root)}
    # Explicitly covered legacy filenames need navigation too; scan deliberately
    # discovers only plan.md rather than guessing which other notes are tasks.
    for name in manifest['entries']:
        if name not in current and _path(root, name).exists():
            data = _read(_source(root, name))
            current[name] = {'path': name, 'title': _title(data), 'status': _status(data)}
    for name in sorted(current):
        row = current[name]
        # A verified backup does not imply successful removal. Existing sources
        # stay visible, including changed/reopened plans retained after backup.
        lines.append('- [' + row['title'].replace('[', '').replace(']', '') + '](' + row['path'] + ') — ' + row['status'])
    lines += ['', '## Archived plans', '']
    for name, entry in manifest['entries'].items():
        if entry.get('archive'):
            lines.append('- [' + entry['task_id'] + '](' + entry['archive'] + ') — member: `' + name + '`')
    return ('\n'.join(lines) + '\n').encode()


def archive(root, plans, apply=False, reference_roots=None):
    root = _root(root)
    if not plans:
        raise StoreError('Select explicit plan paths before archiving')
    if not apply:
        return preview(root, plans, reference_roots)
    with _lock(root):
        report = preview(root, plans, reference_roots)
        if not report['eligible']:
            return {**report, 'archive': None, 'removed': []}
        index = _path(root, 'index.md')
        if index.exists() and not _has_marker(_read(index), INDEX_MARKER):
            raise StoreError('User-owned index must be reviewed, not overwritten')
        summary, manifest = _summary(root), _load(root)
        sources = {n: _read(_source(root, n)) for n in report['eligible']}
        for name, data in sources.items():
            if _hash(data) != manifest['entries'][name]['source_sha256']:
                raise StoreError('Source changed while preparing archive')
        archive_dir = _path(root, 'archive')
        archive_dir.mkdir(exist_ok=True)
        day = datetime.now().strftime('%Y-%m-%d')
        sequence = 1
        while (archive_dir / f'{day}-{sequence:03}.zip').exists():
            sequence += 1
        final = archive_dir / f'{day}-{sequence:03}.zip'
        archive_name = final.relative_to(root).as_posix()
        selected = {name: manifest['entries'][name].copy() for name in sources}
        fd, temp_name = tempfile.mkstemp(prefix='.plan-handoff-', suffix='.zip', dir=archive_dir)
        os.close(fd)
        temp = Path(temp_name)
        try:
            with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for name, data in sources.items():
                    z.writestr(name, data)
                z.writestr(ZIP_MANIFEST, json.dumps({'schema': ARCHIVE_SCHEMA, 'files': selected}))
            _verify_archive(temp, selected)
            # Exclusive creation protects an existing archive even if an outside writer races.
            try:
                with final.open('xb') as stream, temp.open('rb') as source:
                    shutil.copyfileobj(source, stream)
                    stream.flush()
                    os.fsync(stream.fileno())
            except FileExistsError:
                raise  # Never remove another writer's archive.
            except Exception:
                final.unlink(missing_ok=True)
                raise
            _verify_archive(final, selected)
        finally:
            temp.unlink(missing_ok=True)
        if _summary(root) != summary or _load(root) != manifest:
            raise StoreError('Summary or manifest changed during backup; originals retained; verified archive: ' + archive_name)
        updated = _redirect_summary(summary, root, sources, archive_name)
        for name in sources:
            manifest['entries'][name]['archive'] = archive_name
            manifest['entries'][name]['member'] = name
        for entry in manifest['entries'].values():
            # Redirecting links may change a covered block; never certify an
            # unrelated stale block merely because another source was archived.
            if _hash(_block(summary, entry['task_id'])) == entry.get('entry_sha256'):
                entry['entry_sha256'] = _hash(_block(updated, entry['task_id']))
        manifest['summary_sha256'] = _hash(updated)
        # Publish recovery pointers before any removal. Interruptions retain originals or a verified backup.
        try:
            _write(_path(root, 'summary.md'), updated)
            _json_write(_path(root, MANIFEST), manifest)
        except (OSError, StoreError) as error:
            raise StoreError('Metadata update failed; originals retained; verified archive: '
                             + archive_name + '; ' + str(error)) from error
        removed = []
        for name in sources:
            try:
                _remove_source(root, name, selected[name]['source_sha256'])
                removed.append(name)
            except (OSError, StoreError) as error:
                report['retained'][name] = str(error)
        try:
            _write(index, _index(root, manifest))
        except (OSError, StoreError) as error:
            raise StoreError('Navigation update failed after removal; removed: '
                             + json.dumps(removed) + '; retained: ' + json.dumps(report['retained'])
                             + '; verified archive: ' + archive_name + '; ' + str(error)) from error
        return {**report, 'archive': archive_name, 'removed': removed}


def restore(root, archive_name, destination):
    root = _root(root)
    path = _path(root, archive_name)
    if PurePosixPath(archive_name).parts[0] != 'archive':
        raise StoreError('Restore only a managed archive under archive/')
    metadata = _verify_archive(path)
    dest = Path(destination).absolute()
    if dest.exists() or dest.is_symlink():
        raise StoreError('Restore destination must be a new directory')
    # Validate every member before creating the destination; never call extractall.
    for name in metadata['files']:
        _path(dest, name)
        if PurePosixPath(name).parts[0] == 'archive' or PurePosixPath(name).suffix != '.md':
            raise StoreError('Unexpected source member')
    for ancestor in dest.parents:
        if ancestor.is_symlink():
            raise StoreError('Restore destination cannot traverse symlinks')
    dest.mkdir(parents=True)
    with zipfile.ZipFile(path) as z:
        for name in metadata['files']:
            p = _path(dest, name)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as stream:
                stream.write(z.read(name))
    return {'destination': str(dest), 'restored': list(metadata['files'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['scan', 'cover', 'refresh', 'preview', 'archive', 'restore'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--plan', action='append', default=[])
    parser.add_argument('--entry')
    parser.add_argument('--evidence', action='append', default=[])
    parser.add_argument('--references-root', type=Path, action='append', default=[])
    parser.add_argument('--apply', action='store_true', help='Archive only after user-authorized preview; default is read-only')
    parser.add_argument('--archive')
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'scan':
            result = scan(args.root)
        elif args.command == 'cover':
            if len(args.plan) != 1 or not args.entry:
                raise StoreError('cover requires exactly one --plan and one --entry')
            result = cover(args.root, args.plan[0], args.entry, args.evidence)
        elif args.command == 'refresh':
            result = refresh(args.root)
        elif args.command == 'preview':
            result = preview(args.root, args.plan or None, args.references_root)
        elif args.command == 'archive':
            result = archive(args.root, args.plan, args.apply, args.references_root)
        else:
            if not args.archive or not args.destination:
                raise StoreError('restore requires --archive and --destination')
            result = restore(args.root, args.archive, args.destination)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (StoreError, OSError, ValueError, zipfile.BadZipFile) as error:
        print(json.dumps({'error': str(error), 'action': 'Retain originals; inspect inputs before retrying'}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
