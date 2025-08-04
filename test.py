import tkinter


def func():
        label_visible_false.pack()
        button_visible_false.pack()
        label_visible_true.pack_forget()
        button_visible_true.pack_forget()


def visible_true():
        label_visible_false.pack_forget()
        button_visible_false.pack_forget()
        label_visible_true.pack()
        button_visible_true.pack()


root = tkinter.Tk()
root.geometry("400x400")
label_visible_true = tkinter.Label(root, text='Не скрытый текст')
label_visible_true.pack()

button_visible_true = tkinter.Button(root, text='Не скрытая кнопка', command=func)
button_visible_true.pack()

label_visible_false = tkinter.Label(root, text='Скрытый текст')

button_visible_false = tkinter.Button(root, text='Скрытая кнопка', command=visible_true)

root.mainloop()