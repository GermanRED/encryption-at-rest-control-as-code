import pytest

from inventory import assets


# we just want the ARN to appear in the parametrized test
def object_id(st: assets.Storage) -> str:
    if hasattr(st, "arn"):
        return st.arn
    return ""


@pytest.mark.parametrize("st", assets.load(), ids=object_id)
def test_storage_encryption(st: assets.Storage) -> None:
    assert st.encrypted, f"{st.name} is not encrypted"
