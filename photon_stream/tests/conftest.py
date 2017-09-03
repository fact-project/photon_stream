import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--out_dir", 
        action="store", 
        default=None,
        help=("Writes the photon-stream obs production output into a permament "
              "directory. This contains the fake fact/raw file tree. "
              "Default is temporary directory."
        )
    )

@pytest.fixture
def out_dir(request):
    return request.config.getoption("--out_dir")