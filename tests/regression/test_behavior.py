"""Behavior captured before the directory refactor; no external simulation data needed."""
import contextlib
import hashlib
import io
import json
import unittest
from unittest.mock import patch

from config import Config
from controllers.metrics import MetricsController
from models.node.user import UserNode
from models.task import Task
from preprocessing.task_parameters import generate


def task_for(node, identifier, execution, deadline):
    return Task(id=identifier, release_time=0.0, deadline=deadline,
                exec_time=execution, power=0.0, creator_id=node.id,
                dataSize=1.0, cycles_per_bit=1.0, remaining_time=execution,
                creator=node, executor=node)


def schedule_snapshot(parallel):
    # Control the offline task set explicitly, independently of local files.
    with patch.object(Config.SimulatorConfig, 'BASELINE_PARALLEL_FREQUENCY', parallel), \
         patch('os.path.isfile', return_value=False), contextlib.redirect_stdout(io.StringIO()):
        node = UserNode(id='vehicle')
        node.core_Up = [0.5] * node.num_cores
        node.core_Us = [0.5] * node.num_cores
        node.hard_task_specs[0] = [{'type_index': 0, 'period': 3.0, 'wcet': 1.0}]
        tasks = []
        for tick in range(12):
            if tick % 3 == 0:
                hard = task_for(node, f'hard-{tick}', 1.0, tick + 3.0)
                hard.core = 0
                hard.type_index = 0
                hard.is_hard = True
                node.assign_local_hard_task(hard, float(tick))
                tasks.append(hard)
            soft = task_for(node, f'soft-{tick}', 0.75, tick + 2.0)
            node.assign_task(soft, float(tick))
            tasks.append(soft)
            node.execute_tasks(float(tick), {})
        return {'tasks': [[t.id, t.server_deadline, t.finish_time, t.remaining_time,
                           t.is_deadline_missed] for t in tasks],
                'reservations': node.last_tbs_deadline,
                'execution': node.execution_log}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class BehaviorTests(unittest.TestCase):
    def test_unified_edf_itbs_schedule(self):
        self.assertEqual(digest(schedule_snapshot(False)), 'c4d10aecd765fd352466db4a5a263c48a1cb39ad06fb2db46fa944c5de3d04a3')

    def test_parallel_frequency_schedule(self):
        self.assertEqual(digest(schedule_snapshot(True)), '72927209ebbaf0df5b3a1ceb15a4b9db90a60c759f3bdd24128ccf82aea82b4c')

    def test_seeded_hard_task_generation(self):
        specs = generate(12, [3, 4, 5, 6] * 3, 4, 2.0, seed=37)
        self.assertEqual(digest(specs), '3c427692f1105fb3fe710f70440e0b09368b47eac6d9d5fe752f2d75461eefd5')

    def test_metrics_and_output_columns(self):
        metrics = MetricsController()
        for _ in range(4):
            metrics.inc_total_tasks()
        metrics.inc_packet_loss()
        metrics.inc_deadline_miss()
        metrics.inc_hard_deadline_miss()
        metrics.inc_completed_task()
        metrics.add_reward(3.5)
        metrics.add_data(7)
        self.assertEqual(digest(metrics.dataPerStep), '78956b2010b4b43e4cfcfb885ac40a04511bbb8c6eed822d7d4da15983ad3a93')
        self.assertEqual(metrics.convergence_data[0]['CumulativeAvgReward'], 3.5)
        metrics.flush()
        self.assertEqual(metrics.current_step_reward, 0.0)
        self.assertEqual(metrics.total_reward, 3.5)

    def test_application_deadline_stays_separate(self):
        with patch('os.path.isfile', return_value=False), contextlib.redirect_stdout(io.StringIO()):
            node = UserNode(id='vehicle')
        task = task_for(node, 'soft', 1.0, 10.0)
        node.assign_task(task, 0.0)
        self.assertEqual(task.deadline, 10.0)
        self.assertEqual(task.server_deadline, 1.0)


if __name__ == '__main__':
    unittest.main()
