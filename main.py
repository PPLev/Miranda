import asyncio

import packages
from core import Core


async def main():
    core = Core()
    await core.init_plugins()

    await core.start_loop()


if __name__ == '__main__':
    asyncio.run(main())
