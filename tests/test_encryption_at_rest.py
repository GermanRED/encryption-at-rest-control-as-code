import pytest

from inventory import storage


# we just want the ARN to appear in the parametrized test
def object_id(st: storage.Storage) -> str:
    if hasattr(st, "arn"):
        return st.arn
    return ""


@pytest.mark.parametrize("st", storage.load(), ids=object_id)
def test_storage_encryption(st: storage.Storage) -> None:
    assert st.encrypted, f"{st.name} is not encrypted"
