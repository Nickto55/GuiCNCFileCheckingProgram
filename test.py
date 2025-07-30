import asyncio
import tkinter as tk
from tk_async_execute import *

async def my_async_task(label):
    for i in range(10):
        await asyncio.sleep(1)
        label.config(text=f"Асинхронная задача: {i+1}/10")

async def main():
    root = tk.Tk()
    root.title("AsyncIO with Tkinter")

    label = tk.Label(root, text="Загрузка...")
    label.pack()

    async_execute = TkAsyncExecute(root)

    task = async_execute.run_coroutine(my_async_task(label))

    root.mainloop()
    await task

if __name__ == "__main__":
    asyncio.run(main())