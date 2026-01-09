import asyncio
import time
async def say_hello():
    print("Hello...")
    # This task is paused for 1 second, but other tasks can run.
    await asyncio.sleep(1)
    print("...World!")
    
asyncio.run(say_hello())

async def main():
    start_time = time.time()
    # Run two tasks concurrently
    await asyncio.gather(
        say_hello(),
        say_hello()
    )
    end_time = time.time()
    print(f"Finished in {end_time - start_time:.2f} seconds")
    
asyncio.run(main())