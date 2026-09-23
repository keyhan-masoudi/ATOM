"""Catch missing moves, incorrect import capitalization, and broken resource paths."""
import ast
import importlib.util
from pathlib import Path
import unittest

from config import Config
from utils.paths import PROJECT_ROOT, CACHE_ROOT


PACKAGES = ('controllers', 'models', 'utils', 'environment', 'preprocessing', 'analysis', 'prediction')


class StructureTests(unittest.TestCase):
    def test_sources_compile_and_local_imports_resolve_with_exact_case(self):
        sources = [PROJECT_ROOT / 'main.py', PROJECT_ROOT / 'config.py']
        for package in PACKAGES:
            sources.extend((PROJECT_ROOT / package).rglob('*.py'))
        for path in sources:
            with self.subTest(file=path.relative_to(PROJECT_ROOT)):
                self.assertRegex(path.stem, r'^[a-z][a-z0-9_]*$|^__init__$')
                source = path.read_text()
                compile(source, str(path), 'exec')
                for node in ast.walk(ast.parse(source)):
                    modules = []
                    if isinstance(node, ast.Import):
                        modules = [item.name for item in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        if node.level:
                            package = '.'.join(path.relative_to(PROJECT_ROOT).parts[:-1])
                            module = importlib.util.resolve_name('.' * node.level + module, package)
                        modules = [module]
                    for module in modules:
                        if module.split('.')[0] not in (*PACKAGES, 'main', 'config'):
                            continue
                        parent = PROJECT_ROOT
                        parts = module.split('.')
                        for index, part in enumerate(parts):
                            candidates = {p.name for p in parent.iterdir()}
                            if index == len(parts) - 1 and part + '.py' in candidates:
                                break
                            self.assertIn(part, candidates, f'{path}: {module}')
                            parent = parent / part
                            self.assertTrue((parent / '__init__.py').is_file(), module)

    def test_runtime_cache_paths_exist(self):
        self.assertEqual(Path(Config.VehiclesTraffic.PROJECT_ROOT), PROJECT_ROOT)
        self.assertEqual(Path(Config.VehiclesTraffic.CACHE_ROOT), CACHE_ROOT)
        self.assertEqual(Path(Config.Paths.pklPath), CACHE_ROOT)
        self.assertTrue(Path(Config.VehiclesTraffic.PKL_PATH).is_file())
        for filename in ('precalculated_weather.pkl', 'precalculated_vehicle_traffic.pkl',
                         'precalculated_spatial_grid.pkl', 'precalculated_vehicle_predictions.pkl',
                         'hex_traffic_predictions.pkl', 'traffic_processed_data.pkl'):
            self.assertTrue((CACHE_ROOT / filename).is_file(), filename)

    def test_dynamic_partition_import(self):
        from environment.geometry import UtilsFunc
        partitions = UtilsFunc.load_partitions('environment.partitions')
        self.assertEqual(len(partitions), 56)
        self.assertEqual(len({p.__class__.__name__ for p in partitions}), 56)
        self.assertTrue(all(p.radius == 200 for p in partitions))

    def test_no_overwritten_methods(self):
        for path in (PROJECT_ROOT / 'controllers').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ClassDef):
                    names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    self.assertEqual(len(names), len(set(names)), f'{path}: {node.name}')
