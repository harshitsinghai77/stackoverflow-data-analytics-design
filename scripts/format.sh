# Sort imports one per line, so autoflake can remove unused imports
isort app
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
black .
isort .
isort --check-only app
flake8
black app --check