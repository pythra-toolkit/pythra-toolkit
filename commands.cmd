# Commands executed during session
git log -n 5 --oneline
git show --stat d62823e4a207192b33ba9b6b9f2b21b4fb98f77b
git log -n 4 --stat
diff -u /home/red-x/Documents/pythra-toolkit/new-app/render/js/pythra_bridge.js /home/red-x/projects/desktop/Note-app/render/js/pythra_bridge.js
git show d62823e4a207192b33ba9b6b9f2b21b4fb98f77b -- src/
git status
git diff new-app/
find /home/red-x/Documents/pythra-toolkit -name "shibokensupport*" 2>/dev/null
git show d62823e4a207192b33ba9b6b9f2b21b4fb98f77b -- new-app/render/js/pythra_bridge.js
git show d62823e4a207192b33ba9b6b9f2b21b4fb98f77b~1:src/pythra/pythra/project_template/render/js/pythra_bridge.js
git log -n 1 b5f21d4ebf541ba294379f97e6ae979584a067b8 --stat
find /home/red-x/Documents/pythra-toolkit -iname "*motion*.js"
git diff
git log -n 10 --oneline
git log -n 5 --oneline src/pythra/pythra/core.py
cp src/pythra/pythra/project_template/render/js/pythra_bridge.js new-app/render/js/pythra_bridge.js && cp src/pythra/pythra/project_template/render/js/pythra_bridge.js /home/red-x/projects/desktop/Note-app/render/js/pythra_bridge.js
git status
git diff
git diff src/pythra/pythra/core.py
git diff src/pythra/pythra/project_template/render/js/pythra_bridge.js
grep -n "// ──" src/pythra/pythra/project_template/render/js/pythra_bridge.js
grep -n "# ──" src/pythra/pythra/core.py src/pythra/pythra/reconciler.py
diff -u src/pythra/pythra/project_template/render/js/pythra_bridge.js /home/red-x/projects/desktop/Note-app/render/js/pythra_bridge.js
diff -u src/pythra/pythra/project_template/render/js/pythra_bridge.js new-app/render/js/pythra_bridge.js
python3 -c "import Cython; print(Cython.__version__)"
python3 setup.py build_ext --help
cp src/pythra/pythra/project_template/render/js/pythra_bridge.js new-app/render/js/pythra_bridge.js && cp src/pythra/pythra/project_template/render/js/pythra_bridge.js /home/red-x/projects/desktop/Note-app/render/js/pythra_bridge.js
python3 setup.py build_ext --inplace
git status
git diff HEAD~3 src/pythra/pythra/reconciler.py
git diff src/pythra/pythra/reconciler.py
git diff
git status (in Note-app)
git diff lib/screens/note_editor_screen.py (in Note-app)
python3 -m py_compile src/pythra/pythra/reconciler.py
git add src/pythra/pythra/reconciler.py src/pythra/pythra/__pycache__/reconciler.cpython-312.pyc commands.cmd
git commit -m "..." (pythra-toolkit)
git add -A (in Note-app)
git commit -m "..." (in Note-app)
git log dd600fd48f9f01ef16722d16dea117101f4134a2..HEAD --oneline
git show --stat dd600fd48f9f01ef16722d16dea117101f4134a2
git log dd600fd48f9f01ef16722d16dea117101f4134a2..HEAD --stat -- src/
git log dd600fd48f9f01ef16722d16dea117101f4134a2..HEAD --oneline -- src/
git diff --stat dd600fd48f9f01ef16722d16dea117101f4134a2..HEAD -- . ':!new-app' ':!plugins'
python3 -m py_compile src/pythra/pythra/__init__.py
git add CHANGELOG.md pyproject.toml src/pythra/pythra/__init__.py src/pythra/pythra/__pycache__/__init__.cpython-312.pyc src/pythra/setup.py commands.cmd
git commit -m "..." (pythra-toolkit bump to 0.2.0)
ls -la /home/red-x/projects/desktop/Note-app/plugins
ls -la /home/red-x/Documents/pythra-toolkit/new-app/plugins
python3 -m py_compile src/pythra/pythra/config.py src/pythra/pythra/package_manager.py src/pythra/pythra/core.py
git status
git diff src/
git add src/pythra/pythra/config.py src/pythra/pythra/package_manager.py src/pythra/pythra/core.py src/pythra/pythra/pythra_cli/config.yaml commands.cmd
git commit -m "feat(plugins): enforce declarative plugin registration via config.yaml..."
git add config.yaml && git commit -m "feat(config): declare enabled plugins in config.yaml..." (in Note-app)

