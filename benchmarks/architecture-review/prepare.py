#!/usr/bin/env python3
"""Copy public, intentionally flawed fixture to an isolated temp workspace.

The answer key is intentionally NOT copied. Install/init the framework separately
in the resulting directory, and run a clean agent session there.
"""
import argparse
import pathlib
import shutil
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('framework',choices=['egm','bmad','spec-kit','openspec','superpowers'])
    parser.add_argument('--scenario',choices=['flawed','control'],default='flawed')
    args=parser.parse_args()
    folder=pathlib.Path(tempfile.mkdtemp(prefix=f'review-{args.framework}-{args.scenario}-'))
    shutil.copytree(ROOT / ('case' if args.scenario == 'flawed' else 'control'), folder / 'case')
    print(folder)
    print('Read-only benchmark fixture: case/requirements.md, case/design.md, case/tasks.md')
    print('Hidden answer key is outside this workspace. Open a NEW agent session here.')

if __name__=='__main__':
    main()
