# ShipCheck

A small offline release-readiness gate built for the DevTrackAcademy Founder’s Office & Technology Intern role.

It turns a synthetic project checklist into a repeatable handoff check. Every task needs an owner, a done state, written evidence and valid completed dependencies. Cycles, duplicate IDs, unknown dependencies and malformed fields fail the gate.

This is an independent demonstration, not a DevTrackAcademy integration. It contains no company data or private work.

## Run

Python 3, standard library only.

```sh
python shipcheck.py --test
python shipcheck.py release.json
```

Example `release.json`:

```json
{"tasks":[{"id":"T1","owner":"builder","state":"done","evidence":"unit tests passed","depends_on":[]}]}
```

A ready plan prints `ready: true` and exits 0. A failed gate prints its errors and exits 1. File or JSON errors exit 2.

## Checks

13 unit tests cover a valid dependent release, missing/empty plans, malformed tasks, missing IDs, duplicate IDs, missing owners, missing evidence, unfinished work, unknown dependencies, cycles, malformed dependency lists and unfinished dependencies.

## Limits

Evidence is supplied text, not independently verified. A pass does not prove deployment, security, code quality or customer readiness. Human review is still needed. This demonstration reads a local file and does not contact services or change a project.
