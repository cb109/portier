import tkinter


class PortierGui(tkinter.Frame):

    def __init__(self, parent):
        super(PortierGui, self).__init__(parent)
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.hostAddress = tkinter.StringVar()
        self.hostAddress.set("localhost")
        self.portRange = tkinter.StringVar()
        self.portRange.set("20-1000")

        self.frameHost = tkinter.Frame(self)
        self.labelHost = tkinter.Label(self.frameHost, text="Host Adress: ")
        self.entryHost = tkinter.Entry(self.frameHost, textvariable=self.hostAddress)

        self.labelHost.pack(side=tkinter.LEFT)
        self.entryHost.pack(side=tkinter.RIGHT)
        self.frameHost.pack()

        self.framePort = tkinter.Frame(self)
        self.labelPort = tkinter.Label(self.framePort, text="Port Range: ")
        self.entryPort = tkinter.Entry(self.framePort, textvariable=self.portRange)

        self.labelPort.pack(side=tkinter.LEFT)
        self.entryPort.pack(side=tkinter.RIGHT)
        self.framePort.pack()

        self.buttonCheck = tkinter.Button(self, text="Check for open Ports")
        self.buttonCheck.pack(fill=tkinter.BOTH)

        self.listboxResult = tkinter.Listbox(self)
        self.listboxResult.pack(fill=tkinter.BOTH)

        self.parent.title("portier")
        self.pack()


def show():
    app = tkinter.Tk()
    PortierGui(app)
    app.mainloop()


if __name__ == "__main__":
    show()