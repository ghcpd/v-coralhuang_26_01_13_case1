import statistics

from fake import UserAgent
from utils import load


def test_dataset_size():
    data = load()
    assert isinstance(data, list)
    assert len(data) >= 9000, f"Expected at least 9000 UAs, got {len(data)}"


def test_repetition_rate():
    ua = UserAgent()
    samples = [ua.random for _ in range(1000)]
    unique = len(set(samples))
    repetition_rate = (1000 - unique) / 1000 * 100
    assert unique >= 950, (
        f"Repetition too high: unique={unique}, repetition_rate={repetition_rate:.2f}%"
    )


def test_browser_methods():
    ua = UserAgent()
    # get* methods return full dict
    chrome = ua.getChrome
    assert isinstance(chrome, dict)
    assert chrome.get("browser") == "chrome"

    firefox = ua.getFirefox
    assert isinstance(firefox, dict)
    assert firefox.get("browser") == "firefox"

    # string getters
    assert isinstance(ua.chrome, str)
    assert isinstance(ua.firefox, str)


def test_device_filtering():
    ua = UserAgent(platforms=["mobile"])
    samples = [ua.getRandom for _ in range(100)]
    types = [s.get("type") for s in samples]
    assert all(t == "mobile" for t in types), f"Not all samples are mobile: {statistics.multimode(types)}"
