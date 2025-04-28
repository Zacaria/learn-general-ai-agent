add DEPENDENCIES:
  uv add {{DEPENDENCIES}}
  uv pip compile pyproject.toml -o requirements.txt

dev:
  uv run pymon app.py

start:
  uv run app.py
