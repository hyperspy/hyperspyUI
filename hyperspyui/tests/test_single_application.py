import os
import sys
from subprocess import Popen, PIPE, run, TimeoutExpired

import pytest


here = os.path.abspath(__file__)
app_module = os.path.join(os.path.dirname(here), 'single_app.py')


def wait(proc, timeout):
    try:
        proc.wait(timeout)
    except TimeoutExpired:
        return True
    return False


@pytest.mark.timeout(10)
def test_single_application(request):
    cmd = [sys.executable, '-u', app_module, 'my_flag']
    # Start primary instance
    primary = Popen(cmd, stdout=PIPE, stderr=PIPE,
                    universal_newlines=True)

    def _term():
        try:
            primary.kill()
        except OSError:
            # unknown
            pass
    request.addfinalizer(_term)

    # Wait for completed start-up:
    primary_output = ''
    i = 0
    while wait(primary, 1):
        i += 1
        primary_output += primary.stdout.readline()
        if primary_output:
            break
        elif i >= 5:
            raise TimeoutError(
                'Timed out waiting for primary start.'
                '\n\tstdout: %s\n\tstderr: %s' % (
                    primary_output, primary.stderr.read())
                )
    if primary.poll() is not None:
        raise ValueError(
            'Primary instance exited prematurely!'
            '\n\tstdout: %s\n\tstderr: %s' % (
                primary_output, primary.stderr.read()))

    # Start secondary instance
    secondary = run(cmd, timeout=5)

    # Check that secondary instance exited as expected
    assert secondary.returncode == 1

    # Check that primary instance exited as expected
    out, err = primary.communicate(timeout=5)
    primary_output += out
    assert primary.returncode == 0
    assert 'my_flag' in primary_output
