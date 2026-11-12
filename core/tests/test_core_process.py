"""The core run as the desktop shell runs it: as a process of its own."""

import http.client
import json
import os
import socket
import subprocess
import sys
import threading
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from conftest import SECRET


@dataclass
class RunningCore:
    process: subprocess.Popen
    port: int

    def get(self, path: str, secret: str | None = SECRET) -> tuple[int, object]:
        """Ask the API over a real connection to the loopback interface."""
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Authorization": f"Bearer {secret}"} if secret else {}
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        body = json.loads(response.read())
        connection.close()
        return response.status, body


def start_core(data_dir, secret: str | None = SECRET) -> subprocess.Popen:
    environment = {key: value for key, value in os.environ.items() if key != "TRACE_API_SECRET"}
    if secret is not None:
        environment["TRACE_API_SECRET"] = secret
    return subprocess.Popen(
        [sys.executable, "-m", "trace_telemetry", "--data-dir", str(data_dir)],
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


@pytest.fixture
def core(data_dir) -> Iterator[RunningCore]:
    process = start_core(data_dir)
    # A core that never says where it listens is stopped, so the test fails
    # instead of waiting for ever.
    watchdog = threading.Timer(15, process.kill)
    watchdog.start()
    try:
        announcement = process.stdout.readline()
        assert announcement, f"the core stopped without announcing: {process.stderr.read()}"
        yield RunningCore(process, port=json.loads(announcement)["port"])
    finally:
        watchdog.cancel()
        process.kill()
        process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()


def test_the_core_serves_the_api_on_the_port_it_announces(core):
    assert core.get("/logs") == (200, [])


def test_the_running_core_rejects_a_request_without_the_secret(core):
    status, _ = core.get("/logs", secret=None)

    assert status == 401


def test_the_core_listens_on_the_loopback_interface_only(core):
    address = address_on_the_network()
    if address is None:
        pytest.skip("this machine has no network interface besides loopback")

    with pytest.raises(OSError):
        socket.create_connection((address, core.port), timeout=2).close()


def test_the_core_stops_when_the_shell_closes_its_input(core):
    # The shell holds the core's standard input open for as long as it runs,
    # so the core also stops if the shell dies without saying goodbye.
    core.process.stdin.close()

    assert core.process.wait(timeout=10) == 0


def test_the_core_does_not_start_without_a_secret(data_dir):
    process = start_core(data_dir, secret=None)

    _, errors = process.communicate(timeout=15)

    assert process.returncode != 0
    assert "TRACE_API_SECRET" in errors


def address_on_the_network() -> str | None:
    """This machine's address on its network, or None if it has only loopback.

    Connecting a UDP socket sends nothing; it only makes the system choose the
    interface it would use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("192.0.2.1", 9))  # TEST-NET-1: never a real host
        except OSError:
            return None
        address = probe.getsockname()[0]
    return None if address.startswith("127.") else address
