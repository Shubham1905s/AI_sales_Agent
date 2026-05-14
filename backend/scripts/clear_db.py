import asyncio

from app.core.json_store import DEFAULT_STORE, write_store


async def clear_store():
    await write_store(DEFAULT_STORE.copy())
    print("JSON data store cleared")


if __name__ == "__main__":
    asyncio.run(clear_store())
