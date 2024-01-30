import pytest

from noter_gpt.storage import Storage


def pytest_addoption(parser):
    parser.addoption(
        "--runapi",
        action="store_true",
        default=False,
        help="run tests that hit APIs",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runapi"):
        # --runapi given in cli: do not skip API tests
        return
    skip_api = pytest.mark.skip(reason="need --runapi option to run")
    for item in items:
        if "api" in item.keywords:
            item.add_marker(skip_api)


@pytest.fixture
def storage(shared_datadir):
    return Storage(
        root_path=(shared_datadir / "notes"),
        cache_path=(shared_datadir / "notes" / ".noter"),
    )
