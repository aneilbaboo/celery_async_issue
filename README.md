This project demonstrates a bug that occurs when a chain is added to a chord.
There are 6 tests:


| Name | Test                         | async   | Result       |
| ------ | ----------------------------- | ------- | ------------ |
|test_chord | group() &#124; s()               | yes     |  pass        |
|test_chord_chain_one_task | group() &#124; s() &#124; s()        | yes     | fail         |
|test_chord_chain_two_tasks | group() &#124; s() &#124; s() &#124; s() | yes     | pass         |
|test_chord_sync | group() &#124; s()               | no      |  pass        |
|test_chord_chain_one_task_sync | group() &#124; s() &#124; s()        | no      | pass         |
|test_chord_chain_two_tasks_sync | group() &#124; s() &#124; s() &#124; s() | no      | pass         |


Strangely, only the asynchronous version of a chord followed by another task
shows a problem; the synchronous version passes.  Adding another task to the 
chain (3rd row) "fixes" the problem.


# Install

```
pip install -r requirements.txt
```

for celery 3.1.13


# Run Tests

```
nosetests
```

The test class spins up redis-server and a celery worker.

This is the test that fails:

```python
def test_chord_chain_one_task(self):
    c = (group([add.si(2, 2), add.si(4, 4)])
         | add_list.s()
         | mul.s(2))
    res = c.apply_async()
    self.assertEqual(res.get(), 24)
```


# Try Celery Master

The current master branch (2fddb876e1b966c3540aadbbc2257dfd493abb85) fails
every async test with:

TypeError: group object got multiple values for keyword argument 'task_id'

To install celery master branch:
```pip install -r requirements_master.txt```

