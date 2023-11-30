import wx
import sqlite3


def connect_db():
    conn = sqlite3.connect('imc.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculos (
            nome TEXT,
            endereco TEXT,
            peso REAL,
            altura REAL,
            imc REAL,
            classificacao TEXT
        )
    ''')
    return conn


def calcular_imc(peso, altura):
    imc = peso / ((altura / 100) ** 2)
    if imc < 18.5:
        return imc, "Abaixo do peso", wx.BLACK
    elif imc < 24.9:
        return imc, "Peso normal", wx.BLACK
    elif imc < 29.9:
        return imc, "Sobrepeso", wx.BLACK
    elif imc < 34.9:
        return imc, "Obesidade grau 1", wx.RED
    elif imc < 39.9:
        return imc, "Obesidade grau 2", wx.RED
    else:
        return imc, "Obesidade grau 3", wx.RED


class IMCCalculator(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Calculadora de IMC", style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.SetSize((400, 300))
        self.Centre()

        self.conn = connect_db()

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.WHITE)

        self.labels = ["Nome:", "Endereço:", "Peso (kg):", "Altura (cm): (ex: 175)"]
        self.texts = [wx.TextCtrl(self.panel) for _ in self.labels]
        self.buttons = [wx.Button(self.panel, label=label) for label in ["Calcular", "Reiniciar"]]
        self.resultado_label = wx.StaticText(self.panel, label="Seu IMC é:")

        self.buttons[0].Bind(wx.EVT_BUTTON, self.on_calcular)
        self.buttons[1].Bind(wx.EVT_BUTTON, self.on_reiniciar)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for label, text in zip(self.labels, self.texts):
            self.sizer.Add(wx.StaticText(self.panel, label=label), 0, wx.ALIGN_CENTER)
            self.sizer.Add(text, 0, wx.EXPAND)
        self.sizer.Add(self.buttons[0], 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.buttons[1], 0, wx.ALIGN_CENTER)
        self.sizer.Add(self.resultado_label, 0, wx.ALIGN_CENTER)

        self.panel.SetSizer(self.sizer)

    def on_calcular(self, event):
        peso = float(self.texts[2].GetValue().replace(',', '.'))
        altura = float(self.texts[3].GetValue().replace(',', '.'))
        imc, classificacao, cor = calcular_imc(peso, altura)
        self.resultado_label.SetLabel("Seu IMC é: {:.2f} ({})".format(imc, classificacao))
        self.resultado_label.SetForegroundColour(cor)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO calculos (nome, endereco, peso, altura, imc, classificacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.texts[0].GetValue(), self.texts[1].GetValue(), peso, altura, imc, classificacao))
        self.conn.commit()

    def on_reiniciar(self, event):
        for text in self.texts:
            text.SetValue("")
        self.resultado_label.SetLabel("Seu IMC é:")
        self.resultado_label.SetForegroundColour(wx.BLACK)


if __name__ == "__main__":
    app = wx.App()
    frame = IMCCalculator(None)
    frame.Show()
    app.MainLoop()
