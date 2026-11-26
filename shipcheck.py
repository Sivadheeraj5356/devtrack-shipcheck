"""ShipCheck: a tiny offline release-readiness gate for founder-led projects.

Company-specific demonstration for DevTrackAcademy's Founder Office & Technology
Intern role. Synthetic examples only, no connection to their internal systems.
Run: python shipcheck.py --test
Or:  python shipcheck.py release.json
Input: {"tasks": [{"id":"T1", "owner":"dev", "state":"done",
                 "evidence":"tests pass", "depends_on":[]}]}
A release passes only when each task is done, owned, evidenced, references known
completed dependencies and its dependency graph is acyclic. Standard library only.
Not a security audit, proof of deployment or replacement for human review.
"""
import argparse
import json
import sys
import unittest


def check(plan):
    errors = []
    if not isinstance(plan, dict) or not isinstance(plan.get('tasks'), list) or not plan['tasks']:
        return ['tasks must be a non-empty list']
    tasks = plan['tasks']
    ids = {}
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f'task {i}: expected object')
            continue
        key = task.get('id')
        if not isinstance(key, str) or not key.strip():
            errors.append(f'task {i}: missing id')
            continue
        if key in ids:
            errors.append(f'duplicate id: {key}')
        ids[key] = task
        for field in ('owner', 'evidence'):
            if not isinstance(task.get(field), str) or not task[field].strip():
                errors.append(f'{key}: missing {field}')
        if task.get('state') != 'done':
            errors.append(f'{key}: not done')
        deps = task.get('depends_on', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            errors.append(f'{key}: depends_on must be a list of strings')
    graph = {}
    for key, task in ids.items():
        deps = task.get('depends_on', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
            deps = []
        graph[key] = deps
        for dep in deps:
            if dep not in ids:
                errors.append(f'{key}: unknown dependency {dep}')
            elif ids[dep].get('state') != 'done':
                errors.append(f'{key}: incomplete dependency {dep}')
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            errors.append(f'cycle at {key}')
            return
        if key in visited or key not in graph:
            return
        visiting.add(key)
        for dep in graph[key]:
            visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in graph:
        visit(key)
    return errors


def task(key='T1', **changes):
    value = dict(id=key, owner='builder', state='done', evidence='unit tests', depends_on=[])
    value.update(changes)
    return value


class Tests(unittest.TestCase):
    def test_pass(self): self.assertEqual(check({'tasks':[task(), task('T2',depends_on=['T1'])]}), [])
    def test_empty(self): self.assertTrue(check({'tasks':[]}))
    def test_wrong_shape(self): self.assertTrue(check([]))
    def test_bad_task(self): self.assertTrue(check({'tasks':[None]}))
    def test_id(self): self.assertTrue(check({'tasks':[task(id='')]}))
    def test_duplicate(self): self.assertTrue(check({'tasks':[task(), task()]}))
    def test_owner(self): self.assertTrue(check({'tasks':[task(owner=' ')]}))
    def test_evidence(self): self.assertTrue(check({'tasks':[task(evidence=None)]}))
    def test_pending(self): self.assertTrue(check({'tasks':[task(state='doing')]}))
    def test_unknown(self): self.assertTrue(check({'tasks':[task(depends_on=['missing'])]}))
    def test_cycle(self): self.assertTrue(check({'tasks':[task(depends_on=['T2']),task('T2',depends_on=['T1'])]}))
    def test_bad_deps(self): self.assertTrue(check({'tasks':[task(depends_on=[{}])]}))
    def test_incomplete_dep(self): self.assertTrue(check({'tasks':[task(state='doing'),task('T2',depends_on=['T1'])]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', nargs='?')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    if args.test:
        unittest.main(argv=[sys.argv[0]])
    elif args.plan:
        try:
            with open(args.plan, encoding='utf-8') as handle:
                problems = check(json.load(handle))
        except (OSError, ValueError) as exc:
            parser.exit(2, f'Cannot read plan: {exc}\n')
        print(json.dumps({'ready':not problems, 'errors':problems}, indent=2))
        sys.exit(bool(problems))
    else:
        parser.error('provide a JSON plan or --test')
