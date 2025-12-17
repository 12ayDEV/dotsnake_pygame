import asyncio
import dotsnake

# Entry point for Pygbag/WASM
async def main():
    await dotsnake.main()

if __name__ == "__main__":
    asyncio.run(main())
