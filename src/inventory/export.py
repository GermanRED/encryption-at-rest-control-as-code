import json

from .setup import setup


def main() -> int:
    setup()

    from . import assets

    jstr = json.dumps([a.dictfields() for a in assets.load()], indent=2)
    print(jstr)
    return 0


if __name__ == "__main__":
    exit(main())
