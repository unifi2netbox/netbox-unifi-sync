import contextvars
from concurrent.futures import ThreadPoolExecutor

from netbox_unifi_sync.services import sync_engine

_marker = contextvars.ContextVar("marker", default=None)


def _read_marker():
    return _marker.get()


def test_plain_submit_loses_context():
    # Documents why the helper exists: worker threads start with an empty context.
    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            assert executor.submit(_read_marker).result() is None
    finally:
        _marker.reset(token)


def test_submit_with_context_keeps_context():
    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [sync_engine._submit_with_context(executor, _read_marker) for _ in range(8)]
            assert [f.result() for f in futures] == ["request"] * 8
    finally:
        _marker.reset(token)


def test_submit_with_context_survives_nested_pools():
    # Controllers -> sites -> devices are three nested pools in the sync engine.
    def outer():
        with ThreadPoolExecutor(max_workers=2) as inner:
            return sync_engine._submit_with_context(inner, _read_marker).result()

    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            assert sync_engine._submit_with_context(executor, outer).result() == "request"
    finally:
        _marker.reset(token)


def test_submit_with_context_passes_args_and_kwargs():
    def add(a, b=0):
        return a + b

    with ThreadPoolExecutor(max_workers=1) as executor:
        assert sync_engine._submit_with_context(executor, add, 2, b=3).result() == 5


def test_submit_with_context_releases_db_connections_in_worker(monkeypatch):
    # Worker threads must hand their Django connections back when a task ends,
    # or a connection pool runs dry (issue #35).
    import threading

    closed_in = []
    monkeypatch.setattr(
        sync_engine, "_close_thread_db_connections", lambda: closed_in.append(threading.get_ident())
    )

    def work():
        return threading.get_ident()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [sync_engine._submit_with_context(executor, work) for _ in range(6)]
        worker_ids = [f.result() for f in futures]

    assert sorted(closed_in) == sorted(worker_ids)
    assert threading.get_ident() not in closed_in


def test_submit_with_context_releases_db_connections_when_task_fails(monkeypatch):
    closed = []
    monkeypatch.setattr(sync_engine, "_close_thread_db_connections", lambda: closed.append(True))

    def boom():
        raise ValueError("task failed")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = sync_engine._submit_with_context(executor, boom)
        try:
            future.result()
        except ValueError:
            pass
        else:
            raise AssertionError("expected the task's exception")

    assert closed == [True]


def test_close_thread_db_connections_tolerates_unconfigured_django():
    # Unit tests import the engine without Django settings.
    sync_engine._close_thread_db_connections()
