"""Eight-step deterministic integration fixture, executed in a subprocess."""
import contextlib
import io
import json
from pathlib import Path
import random
import sys
import traceback
from types import MethodType
from unittest.mock import patch

import numpy as np
import torch

# This test is launched by filename from a clean Python subprocess.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main
from config import Config
from controllers.loader import Loader
from models.node.cloud import CloudNode
from models.node.fog import FixedFogNode, MobileFogNode
from models.node.user import UserNode
from models.task import Task
from models.zone import Zone
from utils.clock import Clock


def new_task(tick, hard=False):
    task = Task(
        id=f'V_{"H" if hard else "S"}_{tick}', release_time=float(tick),
        deadline=float(tick + 3), exec_time=0.5, power=1.0, creator_id='V',
        dataSize=0.25, cycles_per_bit=1.0, remaining_time=-1.0,
    )
    if hard:
        task.is_hard = True
        task.core = 0
        task.type_index = 0
    return task


class FixtureLoader:
    def load_zones(self):
        manager = Loader.ALGORITHM_MAP[Config.ZoneManagerConfig.DEFAULT_ALGORITHM]
        return {'Z': manager(Zone(id='Z', x=346.4, y=300.0, radius=1000.0))}

    def load_fixed_zones(self):
        return {'F': FixedFogNode(id='F', x=360.0, y=300.0, radius=1000.0,
                                 power=500.0, remaining_power=500.0)}

    def load_user_nodes(self, time):
        return {'V': UserNode(id='V', x=346.4, y=300.0, radius=150.0,
                              speed=3.0, angle=0.0)}

    def load_mobile_fog_nodes(self, time):
        return {'M': MobileFogNode(id='M', x=380.0, y=300.0, radius=150.0,
                                   speed=3.0, angle=0.0)}

    def load_nodes_tasks(self, time):
        return {'V': [new_task(int(time))]} if time < 6 else {}

    def load_nodes_hard_tasks(self, time):
        return {'V': [new_task(int(time), True)]} if time % 3 == 0 else {}


def load_traffic(simulator):
    simulator.traffic_cache = {
        tick: {p.__class__.__name__: 'NoiseConfig.GreenTraffic()'
               for p in simulator.partitions}
        for tick in range(10)
    }


def load_weather(simulator):
    simulator.precalculated_weather = {
        tick: {p.__class__.__name__: 'Rain0' for p in simulator.partitions}
        for tick in range(10)
    }


def load_grid(simulator):
    simulator.spatial_grid_cache = {
        (69, 60): 'Partition10', (72, 60): 'Partition10', (76, 60): 'Partition10',
    }
    simulator._partition_name_map = {
        p.__class__.__name__: p for p in simulator.partitions
    }


def capture_simulations():
    Config.SimulatorConfig.SIMULATION_START_TIME = 0
    Config.SimulatorConfig.SIMULATION_DURATION = 8
    Config.SimulatorConfig.ENABLE_HARD_TASKS = True
    Config.UserNodeConfig.NUM_CORE = 2
    classes = {
        'MADDPG': main.SimulatorMADDPG, 'MAPPO': main.SimulatorMAPPO,
        'DDPG': main.SimulatorDDPG, 'DDPGNew': main.SimulatorDDPGnew,
        'PPO': main.SimulatorPPO, 'SAC': main.SimulatorSAC,
        'Greedy': main.SimulatorGreedy,
    }
    results = {}
    for algorithm in Loader.ALGORITHM_MAP:
        Config.ZoneManagerConfig.DEFAULT_ALGORITHM = algorithm
        random.seed(37)
        np.random.seed(37)
        torch.manual_seed(37)
        with contextlib.redirect_stdout(io.StringIO()), \
             patch('os.path.isfile', return_value=False), \
             patch('torch.cuda.is_available', return_value=False):
            try:
                simulator = classes.get(algorithm, main.Simulator)(
                    FixtureLoader(), Clock(),
                    CloudNode(id='C', x=6000.0, y=1500.0, radius=10000.0),
                )
                simulator.load_cached_traffic = MethodType(load_traffic, simulator)
                simulator.load_cached_weather = MethodType(load_weather, simulator)
                simulator.load_cached_spatial_grid = MethodType(load_grid, simulator)
                simulator.load_cached_vehicle_traffic = lambda: None
                simulator.load_cached_future_predictions = lambda: None
                simulator.save_missed_deadlines_to_excel = lambda *args: None
                simulator.save_success_deadlines_to_excel = lambda *args: None
                simulator.metrics.save_to_excel = lambda *args: None
                simulator.metrics.save_convergence_to_csv = lambda *args: None
                simulator.start_simulation()
                results[algorithm] = {
                    'metrics': simulator.metrics.dataPerStep,
                    'success': simulator.success_deadline_data,
                    'missed': simulator.missed_deadline_data,
                    'convergence': simulator.metrics.convergence_data,
                }
            except Exception as error:
                results[algorithm] = {
                    'error': type(error).__name__, 'message': str(error),
                }
                print(traceback.format_exc(), file=sys.stderr)
    return results


if __name__ == '__main__':
    print(json.dumps(capture_simulations(), sort_keys=True,
                     default=lambda value: value.item() if hasattr(value, 'item') else str(value)))
