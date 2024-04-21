import asyncio

from textual_ui import run_ui


async def main():
    await run_ui()


if __name__ == '__main__':
    asyncio.run(main())