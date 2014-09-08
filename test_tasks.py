from unittest import TestCase
import subprocess as sp
from time import sleep

from tasks import add, mul, add_list, div
from celery import group, chord


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
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s())
        res = c.apply_async()
        self.assertEqual(res.get(), 12)

    def test_chain_in_group1(self):
        c = (group([add.si(1, 1) | add.s(2), # 1+1 + 2 = 4
                    add.si(3,3) | add.s(4)]) # 3+3 + 4 = 10
             | add_list.s()) # 4 + 10 = 14
        res = c.apply_async()
        self.assertEqual(res.get(), 14)

    def test_group_in_chain_in_group(self):
        c = (add.si(1, 1)  # 2
             | group(add.s(2) | add.s(3),  # [(2)+2 + 3,
                     add.s(4) | add.s(5)))  # (2)+4+5]
        res = c.apply_async()
        self.assertEqual(res.get(), [5, 11])



    def test_chord_chain_one_task(self):
        c = (group([add.si(2, 2), add.si(4, 4)])
             | add_list.s()
             | mul.s(2))
        res = c.apply_async()
        self.assertEqual(res.get(), 24)

    def test_group_in_chain_in_group(self):
        c = (add.si(1, 1)  # 2
             | group(add.s(2) | add.s(3),  # [(2)+2 + 3,
                     add.s(4) | add.s(5)))  # (2)+4+5]
        res = c.apply_async()
        self.assertEqual(res.get(), [5, 11])

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

    def test_chain_in_group2(self):
        c = group(add.s(1, 1), add.s(2, 2) | mul.s(100))
        res = c.apply_async()
        self.assertEqual(res.get(), [2, 400])

    def test_complex_nesting(self):
        """Tests for deep nesting of chords, groups and chains"""
        c = (add.si(1, 1) |  # 2
             group(add.s(2) | add.s(3)  # (2) + 2 + 3 = 7

                   # [(7)+4+5, (7)+6+7] = [ 16, 20 ]
                   | group(add.s(4) | add.s(5), add.s(6) | add.s(7))

                   # (16)+(20) = 36
                   | add_list.s()

                   # (36)+8, (36)+9 = [ 44, 45 ]
                   | group(add.s(8), add.s(9)),

                   add.s(8)))  # (2) + 8 = 10

        res = c.apply_async()
        self.assertEqual(res.get(), [[44, 45], 10])

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