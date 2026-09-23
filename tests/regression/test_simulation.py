"""Compare each algorithm with the pre-refactor develop fixture."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


class SimulationRegressionTests(unittest.TestCase):
    def test_all_algorithm_snapshots(self):
        directory = Path(__file__).resolve().parent
        result = subprocess.run(
            [sys.executable, str(directory / 'simulation_probe.py')],
            cwd=directory.parents[1], check=True, capture_output=True, text=True,
            timeout=120, env={**os.environ, 'MPLBACKEND': 'Agg'},
        )
        actual = json.loads(result.stdout)
        expected = json.loads((directory / 'fixtures/simulation_baseline.json').read_text())
        self.assertEqual(set(actual), set(expected))
        for algorithm in expected:
            with self.subTest(algorithm=algorithm):
                self.assertNotIn('error', actual[algorithm])
                self.assert_snapshot(actual[algorithm], expected[algorithm])

    def assert_snapshot(self, actual, expected):
        if isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected))
            for key in expected:
                self.assert_snapshot(actual[key], expected[key])
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected))
            for left, right in zip(actual, expected):
                self.assert_snapshot(left, right)
        elif isinstance(expected, float):
            self.assertAlmostEqual(actual, expected, places=5)
        else:
            self.assertEqual(actual, expected)
