"""Register the adjacent tokenizer under a collision-free Nuke module name."""
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('tokenizerSD2i', Path(__file__).with_name('tokenizer.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.modules['tokenizerSD2i'] = module