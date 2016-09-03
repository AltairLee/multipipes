import pytest


def double(x):
    return x * 2


def test_task_runs_target_function():
    from multipipes import Task

    task = Task(double)
    assert task(2) == 4


def test_task_runs_target_function_and_count_requests():
    from multipipes import Task

    task = Task(double)
    task(2)
    task(2)
    task(2)

    assert task.requests_count == 3


def test_task_returns_multiple_elements_when_iterator():
    from multipipes import Task

    def unpack(x):
        for i in x:
            yield i

    task = Task(unpack)

    generator = task([1, 2, 3])
    assert next(generator) == 1
    assert next(generator) == 2
    assert next(generator) == 3
    with pytest.raises(StopIteration):
        next(generator)


def test_task_allows_empty_args_only_if_target_has_defaults():
    from multipipes import Task
    from multipipes import exceptions

    def add(x, y):
        return x + y

    task = Task(add)
    assert task(1, 2) == 3

    with pytest.raises(exceptions.TimeoutNotSupportedError):
        task(None)


def test_task_triggers_deadline_when_slow():
    from multipipes import Task
    import time

    def power(x, y):
        time.sleep(1)
        return x ** y

    task = Task(power, max_execution_time=0.1)

    with pytest.raises(TimeoutError):
        task(1, 2)


@pytest.mark.skipif(reason='need refactor')
def test_task_handles_max_request_count(monkeypatch):
    from multipipes import exceptions, Task

    monkeypatch.setattr('multipipes.worker._randomize_max_requests',
                        lambda x: x)

    task = Task(double, max_requests=3)

    assert task(1) == 2
    assert task(2) == 4
    assert task(3) == 6

    with pytest.raises(exceptions.MaxRequestsException):
        task(4)


def test_read_from_indata_read_timeout_lt_polling_timeout():
    from multipipes import Pipe, Task

    indata = Pipe()
    task = Task(double, indata=indata, read_timeout=0.1, polling_timeout=0.5)

    task.exit_signal = True
    assert not task._read_from_indata()

    indata.put(1)
    assert task._read_from_indata() == 1


def test_read_from_indata_read_timeout_gt_polling_timeout():
    from multipipes import Pipe, Task

    indata = Pipe()
    task = Task(double, indata=indata, read_timeout=1, polling_timeout=0.3)

    task.exit_signal = True
    assert not task._read_from_indata()


def test_read_from_indata_read_timeout_is_none():
    from multipipes import Pipe, Task

    indata = Pipe()
    task = Task(double, indata=indata, read_timeout=None, polling_timeout=0.5)

    task.exit_signal = True
    assert not task._read_from_indata()