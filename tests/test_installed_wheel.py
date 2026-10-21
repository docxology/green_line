import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_clean_installed_wheel_has_no_siblings(tmp_path):
    def run(argv):
        result = subprocess.run(argv, cwd=tmp_path, env=os.environ.copy(), capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    run(["uv", "build", "--wheel", "--out-dir", str(tmp_path / "dist"), str(ROOT)])
    wheels = list((tmp_path / "dist").glob("*.whl"))
    assert len(wheels) == 1
    environment = tmp_path / "isolated"
    run(["uv", "venv", "--python", sys.executable, str(environment)])
    python = environment / "bin" / "python"
    run(["uv", "pip", "install", "--python", str(python), "--no-deps", str(wheels[0])])
    output = run([str(python), "-I", "-c", (
        "import os, sys, importlib.util; from pathlib import Path; import green_line as g; "
        "assert all(Path(p).resolve().is_relative_to(Path(os.environ['TMPDIR']).parents[1]) for p in (sys.prefix, sys.base_prefix)); "
        "assert all(importlib.util.find_spec(n) is None for n in "
        "('black_line','golden_line','red_line','white_line','silver_line','violet_line','blue_line','line_set','witness_register')); "
        "r=g.read_cultivation(g.CultivationAttempt('p',frozenset({'research'})),as_of='2026-08-29'); "
        "assert r.status is g.GrowthStatus.NEEDS_MARKER; "
        "assert g.canonical_reading(g.replay_reading(g.canonical_reading(r)))==g.canonical_reading(r); "
        "print('installed wheel: siblings NOT_INSTALLED; read and replay PASS')"
    )])
    assert "NOT_INSTALLED" in output
