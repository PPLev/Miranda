import asyncio

import packages
from core import Core


async def main():
    core = Core()
    await core.init_plugins()



    await core.start_loop()
    print("sdjflskdjflskdjflskdjflskdjfslkdfjslkdjfs;lkfjs;lkdjas;ldkfj;lsakfjas;lkdfj;lskdjfl;sakdfjsl;akdfj;saldkfjsal;df")




if __name__ == '__main__':
    asyncio.run(main())
