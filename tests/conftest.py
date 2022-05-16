"""pytest conftest."""
import pytest
from sphinx import __display_version__


@pytest.hookimpl(trylast=True)
def pytest_report_header(*_):
    """Include library versions in output before tests start."""
    return f"libraries: Sphinx-{__display_version__}"
