from unittest import TestCase
from tasks import add, mul, add_list, div
import subprocess as sp
from celery import group
from time import sleep


class TestApplyAsync(TestCase):
    @classmethod
    def setUpClass(cls):
        print("setting up worker...")
        cls.worker = sp.Popen(['celery', 'worker', '--app=tasks.app'])
        cls.redis = sp.Popen(['redis-server'])
        sleep(5)

    @classmethod
    def tearDownClass(cls):
        print("killing worker")
        cls.worker.kill()
        cls.redis.kill()

    def test_chord(self):
        print("test_chord")
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s())
        res = c.apply_async()
        self.assertEqual(res.get(), 12)

    def test_chord_chain_one_task(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | mul.s(2))
        res = c.apply_async()
        self.assertEqual(res.get(), 24)

    def test_chord_chain_two_tasks(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | mul.s(2)
             | mul.s(2))
        res = c.apply_async()
        self.assertEqual(res.get(), 48)

    def test_nested_group(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | add.s(0)
             | group([mul.s(2), mul.s(4)])
             | add_list.s())
        res = c.apply_async()
        self.assertEqual(res.get(), 72)

    def test_chord_sync(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s())
        res = c.apply()
        self.assertEqual(res.get(), 12)

    def test_chord_chain_one_task_sync(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | mul.s(2))
        res = c.apply()
        self.assertEqual(res.get(), 24)

    def test_chord_chain_two_tasks_sync(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | mul.s(2)
             | mul.s(2))
        res = c.apply()
        self.assertEqual(res.get(), 48)

    def test_nested_group_sync(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | add.s(0)
             | group([mul.s(2), mul.s(4)])
             | add_list.s())
        res = c.apply()
        self.assertEqual(res.get(), 72)