"""Exercise publication authorization using the workflow's actual shell script."""
import os
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('overrides, returncode, publish', [
    ({}, 0, True),
    ({'RELEASE_OK': 'false'}, 0, False),
    ({'SOURCE_REPOSITORY': 'other/repository'}, 0, False),
    ({'SOURCE_EVENT': 'pull_request'}, 0, False),
    ({'TAG_SHA': 'changed'}, 1, False),
    ({'RELEASE_DRAFT': 'true'}, 1, False),
    ({'INPUT_TAG': 'v0.3.26$(touch unsafe)'}, 1, False),
    ({'SOURCE_RUN_ID': ''}, 0, True),
])
def test_standalone_publication_requires_validated_published_release(tmp_path, overrides, returncode, publish):
    gh = tmp_path / 'gh'
    gh.write_text('''#!/usr/bin/env python3
import os
import sys
args = ' '.join(sys.argv[1:])
if '/jobs?' in args:
    print('123' if os.environ['RELEASE_OK'] == 'true' else '')
elif '/git/ref/tags/' in args:
    print('tag\\ttag-object')
elif '/git/tags/' in args:
    print(os.environ['TAG_SHA'])
elif args.startswith('release view '):
    print(os.environ['RELEASE_DRAFT'])
else:
    raise SystemExit('Unexpected GitHub operation')
''')
    gh.chmod(0o755)
    output = tmp_path / 'output'
    env = {**os.environ,
           'PATH': f'{tmp_path}{os.pathsep}{os.environ["PATH"]}',
           'INPUT_TAG': 'v0.3.26', 'SOURCE_RUN_ID': '123', 'SOURCE_SHA': 'validated',
           'SOURCE_EVENT': 'push', 'SOURCE_REPOSITORY': 'unifi2netbox/netbox-unifi-sync',
           'GITHUB_REPOSITORY': 'unifi2netbox/netbox-unifi-sync', 'GITHUB_OUTPUT': str(output),
           'RELEASE_OK': 'true', 'TAG_SHA': 'validated', 'RELEASE_DRAFT': 'false', **overrides}
    workflow = yaml.safe_load((ROOT / '.github/workflows/publish-python-package.yml').read_text())
    script = workflow['jobs']['resolve']['steps'][0]['run']
    result = subprocess.run(['bash', '-c', script], env=env, cwd=tmp_path,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == returncode, result.stderr
    values = dict(line.split('=', 1) for line in output.read_text().splitlines())
    assert values['publish'] == str(publish).lower()
    if publish:
        assert values['tag'] == 'v0.3.26'
    assert not (tmp_path / 'unsafe').exists()
