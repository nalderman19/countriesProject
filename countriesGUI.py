import tkinter as tk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import countriesClass as cc

HEIGHT = 500
WIDTH = 600


root = tk.Tk()
root.title("Countries")

def getInfo():
	l = tk.Label(frameL, text="You searched for:  " + entry.get(), fg='#434445', bg='#80c1ff')
	l.place(relx=0) 
	search = cc.countrySearch('https://en.wikipedia.org/wiki/List_of_sovereign_states')
	in2 = search.df[search.df['Country'].str.match(entry.get())].reset_index()
	in3 = str(in2.iloc[0][1])
	search.getNameClass(in3)
	search.processResultClass()
	search.saveImageClass()

	imgIn = convert_from_path("images/" + entry.get()+".pdf")
	cropped = imgIn[0].crop((80,70,1175,900))
	cropped = cropped.resize((540,350))
	searchPhoto = ImageTk.PhotoImage(cropped)
	searchLabel = tk.Label(frameL, image=searchPhoto, anchor='n')
	searchLabel.img = searchPhoto
	searchLabel.place(relwidth=0.98, relheight=0.9, relx=0.01, rely=0.05)




# Entry box stuff
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

image = Image.open("images/bg.png")
bgPhoto = ImageTk.PhotoImage(image)
bgLabel = tk.Label(root, image=bgPhoto)
bgLabel.img = bgPhoto
bgLabel.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg='#80c1ff')
frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.1)

button = tk.Button(frame, text='Submit', command=getInfo)
button.place(relx=0.86, rely=0.4, relwidth=0.13)

label = tk.Label(frame, text='Enter Name of Desired Country', fg='#434445', bg='#80c1ff')
label.place(relx=0.01)

entry = tk.Entry(frame)
entry.place(relx=0.01, rely=0.4, relwidth=0.84)

# info box stuff
frameL = tk.Frame(root, bg='#80c1ff')
frameL.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.75)

label2 = tk.Label(frameL, fg='#434445', bg='#80c1ff')
label2.place(relx=0.01)

root.mainloop()