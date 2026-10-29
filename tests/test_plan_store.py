"""Temporary-fixture acceptance for summary coverage and recoverable cleanup."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'plan_store.py'
spec = importlib.util.spec_from_file_location('plan_store', SCRIPT)
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'handoffs'
        self.root.mkdir()
        self.original = self.plan('done/plan.md')
        self.summary('done', 'Delivered bounded reading. Historical checks passed; Windows not tested.')

    def plan(self, path, status='completed', body='Implementation evidence: commit abc123.\n'):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        data = f'# A task\n\n- Task status: {status}.\n\n{body}'.encode()
        p.write_bytes(data)
        return data

    def summary(self, entry, body, append=False):
        block = f'\n<!-- plan-handoff:entry:{entry} -->\n## {entry}\n\n{body}\n<!-- /plan-handoff:entry:{entry} -->\n'
        p = self.root / 'summary.md'
        p.write_text((p.read_text() if append else '<!-- plan-handoff:summary:v1 -->\n# Results\n') + block)

    def covered(self):
        store.cover(self.root, 'done/plan.md', 'done', ['commit abc123'])

    def test_no_summary_and_unmanaged_summary_are_refused(self):
        (self.root / 'summary.md').unlink()
        with self.assertRaises(store.StoreError):
            store.preview(self.root)
        (self.root / 'summary.md').write_text('# My unrelated document\n')
        with self.assertRaises(store.StoreError):
            self.covered()
        self.assertEqual((self.root / 'done/plan.md').read_bytes(), self.original)

    def test_cover_requires_real_unique_nonempty_entry(self):
        for text in ['<!-- plan-handoff:summary:v1 -->\n',
                     '<!-- plan-handoff:summary:v1 -->\n<!-- plan-handoff:entry:done -->\n## done\n<!-- /plan-handoff:entry:done -->\n']:
            (self.root / 'summary.md').write_text(text)
            with self.assertRaises(store.StoreError):
                self.covered()

    def test_dry_run_does_not_write_or_remove(self):
        self.covered()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = store.archive(self.root, ['done/plan.md'])
        self.assertEqual(report['eligible'], ['done/plan.md'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_archive_and_restore_exact_bytes_keep_evidence(self):
        self.covered()
        (self.root / 'done/evidence.log').write_bytes(b'keep me')
        report = store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertEqual(report['removed'], ['done/plan.md'])
        self.assertFalse((self.root / 'done/plan.md').exists())
        self.assertEqual((self.root / 'done/evidence.log').read_bytes(), b'keep me')
        destination = Path(self.temp.name) / 'restored'
        store.restore(self.root, report['archive'], destination)
        self.assertEqual((destination / 'done/plan.md').read_bytes(), self.original)
        self.assertIn(report['archive'], (self.root / 'index.md').read_text())
        self.assertNotIn('](done/plan.md)', (self.root / 'summary.md').read_text())
        self.assertEqual(store.preview(self.root)['eligible'], [])
        self.assertEqual(store.scan(self.root), [])

    def test_source_and_summary_changes_invalidate_coverage(self):
        self.covered()
        (self.root / 'done/plan.md').write_bytes(self.original + b'New unresolved detail.\n')
        self.assertEqual(store.preview(self.root)['eligible'], [])
        (self.root / 'done/plan.md').write_bytes(self.original)
        (self.root / 'summary.md').write_text((self.root / 'summary.md').read_text() + '\nChanged overview.\n')
        self.assertEqual(store.preview(self.root)['eligible'], [])
        store.refresh(self.root)
        self.assertEqual(store.preview(self.root)['eligible'], ['done/plan.md'])

    def test_changed_entry_cannot_be_blessed_by_refresh(self):
        self.covered()
        self.summary('done', 'A different claim.')
        with self.assertRaises(store.StoreError):
            store.refresh(self.root)

    def test_active_unknown_and_pending_plans_are_never_covered(self):
        for status in ['in progress', 'blocked', 'awaiting planning', 'implementation complete / acceptance pending', 'awaiting review', 'unclear']:
            self.plan('done/plan.md', status)
            with self.subTest(status=status), self.assertRaises(store.StoreError):
                self.covered()

    def test_examples_and_historical_sections_are_not_task_metadata(self):
        examples = [
            '```markdown\n- Task status: completed\n```\n',
            '~~~~markdown\n- Task status: completed\n~~~\n~~~~\n',
            '<!--\n- Task status: completed\n-->\n',
            '    - Task status: completed\n',
            '> - Task status: completed\n',
            '## Historical example\n- Task status: completed\n',
        ]
        for example in examples:
            with self.subTest(example=example):
                (self.root / 'done/plan.md').write_text('# Active task\n\n' + example)
                with self.assertRaises(store.StoreError):
                    self.covered()
                self.assertTrue((self.root / 'done/plan.md').exists())

    def test_real_status_is_not_overridden_by_example_status(self):
        for status in ['completed', 'in progress']:
            with self.subTest(status=status):
                self.plan('done/plan.md', status,
                          '<!-- - Task status: cancelled -->\n'
                          '```markdown\n- Task status: completed\n```\n'
                          '## Prior state\n- Task status: superseded\n')
                if status == 'completed':
                    self.covered()
                    self.assertEqual(store.preview(self.root)['eligible'], ['done/plan.md'])
                else:
                    with self.assertRaises(store.StoreError):
                        self.covered()

    def test_completed_plan_reopened_after_cover_is_retained(self):
        self.covered()
        self.plan('done/plan.md', 'in progress')
        self.assertEqual(store.preview(self.root)['eligible'], [])

    def test_path_escape_and_symlink_are_refused(self):
        for p in ['../outside.md', '/tmp/outside.md', 'archive/plan.md', 'C:/outside.md', 'summary.md']:
            with self.subTest(path=p), self.assertRaises(store.StoreError):
                store.cover(self.root, p, 'done')
        link = self.root / 'link'
        try:
            link.symlink_to(self.root / 'done', target_is_directory=True)
        except OSError:
            self.skipTest('Symlinks unavailable in this fixture environment')
        with self.assertRaises(store.StoreError):
            store.cover(self.root, 'link/plan.md', 'done')
        self.assertFalse(any(r['path'].startswith('link/') for r in store.scan(self.root)))

    def test_live_references_keep_source(self):
        self.covered()
        self.plan('active/plan.md', 'in progress', 'Still depends on [old](../done/plan.md).\n')
        report = store.preview(self.root)
        self.assertEqual(report['eligible'], [])
        self.assertIn('referenced', report['retained']['done/plan.md'])

    def test_external_declared_reference_root_is_checked(self):
        self.covered()
        outside = Path(self.temp.name) / 'notes'
        outside.mkdir()
        (outside / 'readme.md').write_text('[Context](../handoffs/done/plan.md)\n')
        report = store.preview(self.root, reference_roots=[outside])
        self.assertEqual(report['eligible'], [])

    def test_unmanaged_index_is_not_overwritten(self):
        self.covered()
        (self.root / 'index.md').write_text('# User-owned index\n')
        with self.assertRaises(store.StoreError):
            store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertTrue((self.root / 'done/plan.md').exists())
        self.assertEqual((self.root / 'index.md').read_text(), '# User-owned index\n')

    def test_incremental_summary_preserves_archived_entries(self):
        self.covered()
        first = store.archive(self.root, ['done/plan.md'], apply=True)
        self.plan('second/plan.md')
        self.summary('second', 'Added background waiting; local behavior checked.', append=True)
        store.cover(self.root, 'second/plan.md', 'second')
        manifest = json.loads((self.root / 'summary.manifest.json').read_text())
        self.assertEqual(manifest['entries']['done/plan.md']['archive'], first['archive'])
        self.assertIn('done', (self.root / 'summary.md').read_text())
        second = store.archive(self.root, ['second/plan.md'], apply=True)
        self.assertNotEqual(first['archive'], second['archive'])
        self.assertEqual(len(list((self.root / 'archive').glob('*.zip'))), 2)

    def test_lost_old_summary_entry_is_refused(self):
        self.covered()
        store.archive(self.root, ['done/plan.md'], apply=True)
        self.plan('second/plan.md')
        self.summary('second', 'New feature only, old result accidentally lost.')
        with self.assertRaises(store.StoreError):
            store.cover(self.root, 'second/plan.md', 'second')

    def test_zip_verification_failure_never_removes_source(self):
        self.covered()
        with patch.object(store, '_verify_archive', side_effect=store.StoreError('Corrupt ZIP')):
            with self.assertRaises(store.StoreError):
                store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertEqual((self.root / 'done/plan.md').read_bytes(), self.original)

    def test_source_changed_after_backup_is_not_removed(self):
        self.covered()
        real = store._remove_source
        def change_first(root, path, expected):
            (root / path).write_bytes(self.original + b'concurrent edit\n')
            return real(root, path, expected)
        with patch.object(store, '_remove_source', side_effect=change_first):
            report = store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertEqual(report['removed'], [])
        self.assertIn('done/plan.md', report['retained'])
        self.assertTrue(report['archive'])
        self.assertIn(b'concurrent edit', (self.root / 'done/plan.md').read_bytes())
        self.assertIn('](done/plan.md)', (self.root / 'index.md').read_text())

    def test_same_batch_references_survive_removal_failure_in_both_orders(self):
        self.plan('a/plan.md', body='Required evidence: [B](../b/plan.md).\n')
        self.plan('b/plan.md')
        self.summary('a', 'Delivered A with evidence in B.', append=True)
        self.summary('b', 'Delivered B; local evidence retained.', append=True)
        store.cover(self.root, 'a/plan.md', 'a')
        store.cover(self.root, 'b/plan.md', 'b')
        for plans in [['a/plan.md', 'b/plan.md'], ['b/plan.md', 'a/plan.md']]:
            with self.subTest(order=plans):
                # Each order runs in its own collection so no earlier archive
                # or interruption metadata affects eligibility.
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory) / 'handoffs'
                    shutil.copytree(self.root, root)
                    original_remove = store._remove_source

                    def fail_a(collection, name, expected):
                        if name == 'a/plan.md':
                            raise PermissionError('fixture: A cannot be removed')
                        return original_remove(collection, name, expected)

                    with patch.object(store, '_remove_source', side_effect=fail_a):
                        report = store.archive(root, plans, apply=True)
                    self.assertTrue((root / 'a/plan.md').exists())
                    self.assertTrue((root / 'b/plan.md').exists())
                    self.assertEqual(report['removed'], [])
                    self.assertIn('b/plan.md', report['retained'])
                    self.assertIn('](a/plan.md)', (root / 'index.md').read_text())
                    self.assertIn('](b/plan.md)', (root / 'index.md').read_text())

    def test_mutual_batch_dependencies_are_conservatively_retained(self):
        self.plan('a/plan.md', body='[B](../b/plan.md)\n')
        self.plan('b/plan.md', body='[A](../a/plan.md)\n')
        for entry in ['a', 'b']:
            self.summary(entry, 'Historical result and limits for ' + entry, append=True)
            store.cover(self.root, entry + '/plan.md', entry)
        report = store.archive(self.root, ['a/plan.md', 'b/plan.md'], apply=True)
        self.assertEqual(report['removed'], [])
        self.assertIsNone(report['archive'])
        self.assertTrue((self.root / 'a/plan.md').exists())
        self.assertTrue((self.root / 'b/plan.md').exists())

    def test_retained_legacy_source_stays_in_navigation(self):
        self.plan('legacy.md')
        self.summary('legacy', 'Historical legacy result and evidence.', append=True)
        store.cover(self.root, 'legacy.md', 'legacy')
        with patch.object(store, '_remove_source', side_effect=PermissionError('fixture: retained legacy')):
            report = store.archive(self.root, ['legacy.md'], apply=True)
        self.assertEqual(report['removed'], [])
        self.assertTrue((self.root / 'legacy.md').exists())
        self.assertIn('](legacy.md)', (self.root / 'index.md').read_text())

    def test_navigation_write_failure_reports_actual_removals_and_backup(self):
        self.covered()
        original_write = store._write

        def fail_index(path, data):
            if path.name == 'index.md':
                raise OSError('fixture: navigation write failed')
            return original_write(path, data)

        with patch.object(store, '_write', side_effect=fail_index):
            with self.assertRaisesRegex(store.StoreError, 'removed.*done/plan.md.*verified archive: archive/'):
                store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertFalse((self.root / 'done/plan.md').exists())
        name = next((self.root / 'archive').glob('*.zip')).relative_to(self.root).as_posix()
        destination = Path(self.temp.name) / 'recovered-after-index-error'
        store.restore(self.root, name, destination)
        self.assertEqual((destination / 'done/plan.md').read_bytes(), self.original)

    def test_lf_and_crlf_markers_support_cover_archive_and_byte_exact_restore(self):
        for newline in ['\n', '\r\n']:
            with self.subTest(newline=repr(newline)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / 'handoffs'
                root.mkdir()
                source = ('# Task\n- Task status: completed\n\nEvidence.\n').replace('\n', newline).encode()
                (root / 'plan.md').write_bytes(source)
                summary = (store.SUMMARY_MARKER + '\n<!-- plan-handoff:entry:done -->\n'
                           '## Delivered\nLocal evidence; Windows not tested.\n'
                           '<!-- /plan-handoff:entry:done -->\n').replace('\n', newline).encode()
                (root / 'summary.md').write_bytes(summary)
                (root / 'index.md').write_bytes((store.INDEX_MARKER + '\n[Task](plan.md)\n').replace('\n', newline).encode())
                store.cover(root, 'plan.md', 'done')
                self.assertEqual(store.preview(root)['eligible'], ['plan.md'])
                report = store.archive(root, ['plan.md'], apply=True)
                self.assertEqual(report['removed'], ['plan.md'])
                self.assertNotIn('](plan.md)', (root / 'index.md').read_text())
                destination = Path(directory) / 'restored'
                store.restore(root, report['archive'], destination)
                self.assertEqual((destination / 'plan.md').read_bytes(), source)
                self.assertEqual((root / 'summary.md').read_bytes(), summary)

    def test_write_failure_preserves_sources(self):
        self.covered()
        with patch.object(store.zipfile, 'ZipFile', side_effect=OSError('disk full')):
            with self.assertRaises((OSError, store.StoreError)):
                store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertEqual((self.root / 'done/plan.md').read_bytes(), self.original)

    def test_restore_does_not_overwrite_existing_destination(self):
        self.covered()
        report = store.archive(self.root, ['done/plan.md'], apply=True)
        destination = Path(self.temp.name) / 'existing'
        destination.mkdir()
        with self.assertRaises(store.StoreError):
            store.restore(self.root, report['archive'], destination)

    def test_summary_source_links_are_redirected_before_removal(self):
        self.summary('done', 'Delivered reader; [original](done/plan.md#validation) records historical evidence.')
        self.covered()
        report = store.archive(self.root, ['done/plan.md'], apply=True)
        text = (self.root / 'summary.md').read_text()
        self.assertIn(f']({report["archive"]})', text)
        self.assertNotIn('](done/plan.md', text)
        manifest = json.loads((self.root / 'summary.manifest.json').read_text())
        self.assertEqual(manifest['summary_sha256'], hashlib.sha256((self.root / 'summary.md').read_bytes()).hexdigest())


    def test_unsupported_summary_link_is_retained_instead_of_broken(self):
        self.summary('done', 'Delivered reader. See [source][old].\n\n[old]: done/plan.md')
        self.covered()
        report = store.preview(self.root)
        self.assertEqual(report['eligible'], [])
        self.assertTrue((self.root / 'done/plan.md').exists())

    def test_archived_result_cannot_be_dropped_or_rewritten_on_new_cover(self):
        self.covered()
        store.archive(self.root, ['done/plan.md'], apply=True)
        p = self.root / 'summary.md'
        p.write_text(p.read_text().replace('Delivered bounded reading.', 'Entirely different result.'))
        self.plan('second/plan.md')
        self.summary('second', 'Another delivered feature.', append=True)
        with self.assertRaises(store.StoreError):
            store.cover(self.root, 'second/plan.md', 'second')

    def test_clean_does_not_certify_another_stale_result_block(self):
        self.covered()
        self.plan('second/plan.md')
        self.summary('second', 'Original second result.', append=True)
        store.cover(self.root, 'second/plan.md', 'second')
        p = self.root / 'summary.md'
        p.write_text(p.read_text().replace('Delivered bounded reading.', 'Changed first result.'))
        # Certifying the second block must not certify the changed first one.
        store.cover(self.root, 'second/plan.md', 'second')
        store.archive(self.root, ['second/plan.md'], apply=True)
        report = store.preview(self.root)
        self.assertEqual(report['eligible'], [])
        self.assertIn('done/plan.md', report['retained'])


    def test_metadata_failure_reports_backup_and_preserves_original(self):
        self.covered()
        with patch.object(store, '_json_write', side_effect=OSError('metadata disk full')):
            with self.assertRaisesRegex(store.StoreError, 'verified archive: archive/'):
                store.archive(self.root, ['done/plan.md'], apply=True)
        self.assertEqual((self.root / 'done/plan.md').read_bytes(), self.original)
        archives = list((self.root / 'archive').glob('*.zip'))
        self.assertEqual(len(archives), 1)
        store.restore(self.root, archives[0].relative_to(self.root).as_posix(), Path(self.temp.name) / 'recover')
        self.assertEqual((Path(self.temp.name) / 'recover/done/plan.md').read_bytes(), self.original)

    def test_restore_rejects_escape_member_before_writing_destination(self):
        archive_dir = self.root / 'archive'
        archive_dir.mkdir()
        data = b'outside data'
        with zipfile.ZipFile(archive_dir / 'invalid.zip', 'w') as z:
            z.writestr('../outside.md', data)
            z.writestr(store.ZIP_MANIFEST, json.dumps({'schema': store.ARCHIVE_SCHEMA,
                'files': {'../outside.md': {'source_sha256': hashlib.sha256(data).hexdigest()}}}))
        dest = Path(self.temp.name) / 'restored'
        with self.assertRaises(store.StoreError):
            store.restore(self.root, 'archive/invalid.zip', dest)
        self.assertFalse(dest.exists())
        self.assertFalse((Path(self.temp.name) / 'outside.md').exists())

    def test_cli_roundtrip_and_readonly_default(self):
        def cli(command, *args):
            process = subprocess.run([sys.executable, str(SCRIPT), command, '--root', str(self.root), *args],
                                     text=True, capture_output=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            return json.loads(process.stdout)
        cli('cover', '--plan', 'done/plan.md', '--entry', 'done')
        report = cli('archive', '--plan', 'done/plan.md')
        self.assertEqual(report['eligible'], ['done/plan.md'])
        self.assertTrue((self.root / 'done/plan.md').exists())
        report = cli('archive', '--plan', 'done/plan.md', '--apply')
        dest = Path(self.temp.name) / 'cli-recovered'
        cli('restore', '--archive', report['archive'], '--destination', str(dest))
        self.assertEqual((dest / 'done/plan.md').read_bytes(), self.original)

    def test_cli_missing_summary_exits_nonzero_with_actionable_json(self):
        process = subprocess.run([sys.executable, str(SCRIPT), 'preview', '--root', str(self.root)],
                                 text=True, capture_output=True)
        self.assertEqual(process.returncode, 1)
        self.assertIn('error', json.loads(process.stdout))
        self.assertTrue((self.root / 'done/plan.md').exists())


    def test_unicode_sources_and_all_closed_statuses_restore_exactly(self):
        for i, status in enumerate(['completed', 'cancelled', 'superseded']):
            name = f'旧任务-{i}/plan.md'
            entry = f'closed-{i}'
            data = self.plan(name, status, '中文证据与限制：仅本地验证。\n')
            self.summary(entry, f'Status {status}; retain its actual outcome and limits.', append=True)
            store.cover(self.root, name, entry)
            report = store.archive(self.root, [name], apply=True)
            dest = Path(self.temp.name) / f'恢复-{i}'
            store.restore(self.root, report['archive'], dest)
            self.assertEqual((dest / name).read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
