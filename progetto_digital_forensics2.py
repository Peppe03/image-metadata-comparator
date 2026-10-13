import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QFrame, QSplitter, QTextEdit, QPushButton, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QFileDialog, QMessageBox

try:
    from exiftool import ExifToolHelper
except ImportError:
    print("La libreria PyExifTool non è installata. Esegui: pip install PyExifTool")
    sys.exit(1)
except FileNotFoundError:
    print("Errore: ExifTool non trovato.")
    print("Assicurati che ExifTool sia installato e accessibile nel PATH del tuo sistema.")
    print("Puoi scaricarlo da: https://exiftool.org/")
    sys.exit(1)


# sezione logica

class EstrattoreMetadati(QObject):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, percorso_file):
        super().__init__()
        self.percorso_file = percorso_file

    def run(self):
        try:
            with ExifToolHelper() as et:
                metadati = et.get_metadata(self.percorso_file)
                if metadati:
                    metadati_puliti = {}
                    dizionario_sorgente = metadati[0]
                    for k, v in dizionario_sorgente.items():
                        if k != 'SourceFile':
                            metadati_puliti[k] = v
                    self.finished.emit(metadati_puliti)
                else:
                    self.error.emit(f"Nessun metadato trovato per {os.path.basename(self.percorso_file)}.")
        except Exception as e:
            self.error.emit(f"Errore durante l'estrazione: {str(e)}")


def confronta_metadati(metadati1, metadati2):

    if not metadati1 or not metadati2:
        return {}, {}, {}, {}

    chiavi1 = set(metadati1.keys())
    chiavi2 = set(metadati2.keys())

    chiavi_comuni = chiavi1 & chiavi2
    chiavi_uniche1 = chiavi1 - chiavi2
    chiavi_uniche2 = chiavi2 - chiavi1

    chiavi_comuni_con_valori_diversi = {}
    for chiave in chiavi_comuni:
        if metadati1[chiave] != metadati2[chiave]:
            chiavi_comuni_con_valori_diversi[chiave] = (metadati1[chiave], metadati2[chiave])

    metadati_unici1 = {}
    for chiave in chiavi_uniche1:
        metadati_unici1[chiave] = metadati1[chiave]
    
    metadati_unici2 = {}
    for chiave in chiavi_uniche2:
        metadati_unici2[chiave] = metadati2[chiave]

    return chiavi_comuni, chiavi_comuni_con_valori_diversi, metadati_unici1, metadati_unici2


# sezione interfaccia grafica

class AreaRilascioImmagine(QLabel):

    immagine_rilasciata = pyqtSignal(str)

    def __init__(self, titolo, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(300, 200)
        self.titolo = titolo
        self.setAcceptDrops(True)
        self.reset_stile()
        self.setText(f"{self.titolo}\n\nTrascina un'immagine qui\no clicca per selezionarla")

    def reset_stile(self):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #4C566A;
                border-radius: 10px;
                background-color: #3B4252;
                color: #D8DEE9;
                font-size: 14px;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            percorso_file = event.mimeData().urls()[0].toLocalFile()
            if percorso_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                event.acceptProposedAction()
                self.setStyleSheet("border: 2px solid #88C0D0; background-color: #434C5E;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.reset_stile()

    def dropEvent(self, event: QDropEvent):
        percorso_file = event.mimeData().urls()[0].toLocalFile()
        self.carica_immagine(percorso_file)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            percorso_file, _ = QFileDialog.getOpenFileName(
                self, f"Seleziona {self.titolo}", "",
                "File Immagine (*.png *.jpg *.jpeg *.tiff *.bmp)"
            )
            if percorso_file:
                self.carica_immagine(percorso_file)

    def carica_immagine(self, percorso_file):
        mappa_pixel = QPixmap(percorso_file)
        if not mappa_pixel.isNull():
            mappa_pixel_scalata = mappa_pixel.scaled(self.size() - QSize(20, 20),
                                                  Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(mappa_pixel_scalata)
            self.immagine_rilasciata.emit(percorso_file)
        else:
            QMessageBox.warning(self, "Errore", "Impossibile caricare il file immagine.")
        self.reset_stile()

    def reset(self):
        self.clear()
        self.setText(f"{self.titolo}\n\nTrascina un'immagine qui\no clicca per selezionarla")


class FinestraPrincipale(QMainWindow):
    
    COLORE_IDENTICO = "#4A6B54"
    COLORE_DIVERSO = "#B8860B"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparatore di Metadati di Immagini")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E3440;
                color: #D8DEE9;
            }
            QFrame {
                border: none;
            }
            QTextEdit {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 5px;
                color: #ECEFF4;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
            }
            QScrollArea {
                border: none;
            }
            QLabel#resultLabel {
                font-size: 16px;
                font-weight: bold;
                color: #88C0D0;
                padding: 10px;
                background-color: #3B4252;
                border-radius: 5px;
            }
            QSplitter::handle {
                background-color: #4C566A;
            }
            QSplitter::handle:hover {
                background-color: #5E81AC;
            }
            QScrollBar:vertical {
                border: none;
                background: #2E3440;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5E81AC;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #88C0D0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QPushButton {
                background-color: #4C566A;
                color: #E5E9F0;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #434C5E;
            }
            QStatusBar {
                background-color: #3B4252;
                color: #D8DEE9;
            }
        """)

        self.percorso_immagine1 = None
        self.percorso_immagine2 = None
        self.metadati1 = None
        self.metadati2 = None

        widget_principale = QWidget()
        self.setCentralWidget(widget_principale)
        layout_principale = QVBoxLayout(widget_principale)

        divisore = QSplitter(Qt.Orientation.Horizontal)

        cornice1 = QFrame()
        layout1 = QVBoxLayout(cornice1)
        self.zona_rilascio1 = AreaRilascioImmagine("Immagine 1")
        self.visualizzatore_metadati1 = QTextEdit()
        self.visualizzatore_metadati1.setReadOnly(True)
        layout1.addWidget(self.zona_rilascio1, 2)
        layout1.addWidget(QLabel("Metadati Immagine 1:"))
        layout1.addWidget(self.visualizzatore_metadati1, 3)

        cornice2 = QFrame()
        layout2 = QVBoxLayout(cornice2)
        self.zona_rilascio2 = AreaRilascioImmagine("Immagine 2")
        self.visualizzatore_metadati2 = QTextEdit()
        self.visualizzatore_metadati2.setReadOnly(True)
        layout2.addWidget(self.zona_rilascio2, 2)
        layout2.addWidget(QLabel("Metadati Immagine 2:"))
        layout2.addWidget(self.visualizzatore_metadati2, 3)

        divisore.addWidget(cornice1)
        divisore.addWidget(cornice2)
        divisore.setSizes([600, 600])
        

        layout_principale.addWidget(divisore, 1)


        self.etichetta_risultato = QLabel("Carica due immagini per iniziare il confronto.")
        self.etichetta_risultato.setObjectName("resultLabel")
        self.etichetta_risultato.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etichetta_risultato.setWordWrap(True)
        layout_principale.addWidget(self.etichetta_risultato)


        self.pulsante_reset = QPushButton("Reset")
        layout_principale.addWidget(self.pulsante_reset)


        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        legenda_html = f"""
            <span style='color: {self.COLORE_IDENTICO}; font-size: 16px; vertical-align: middle;'>●</span> Valore Identico
              
            <span style='color: {self.COLORE_DIVERSO}; font-size: 16px; vertical-align: middle;'>●</span> Valore Diverso
        """
        self.legenda_statusbar = QLabel(legenda_html)
        self.statusBar.addPermanentWidget(self.legenda_statusbar)


        self.zona_rilascio1.immagine_rilasciata.connect(self.on_rilascio_immagine1)
        self.zona_rilascio2.immagine_rilasciata.connect(self.on_rilascio_immagine2)
        self.pulsante_reset.clicked.connect(self.reimposta_interfaccia)

    def on_rilascio_immagine1(self, percorso):
        self.percorso_immagine1 = percorso
        self.metadati1 = None
        self.visualizzatore_metadati1.setText(f"Estrazione metadati da:\n{os.path.basename(percorso)}...")
        self.avvia_estrazione_metadati(1, percorso)
        self.controlla_e_confronta()

    def on_rilascio_immagine2(self, percorso):
        self.percorso_immagine2 = percorso
        self.metadati2 = None
        self.visualizzatore_metadati2.setText(f"Estrazione metadati da:\n{os.path.basename(percorso)}...")
        self.avvia_estrazione_metadati(2, percorso)
        self.controlla_e_confronta()

    def avvia_estrazione_metadati(self, numero_immagine, percorso):
        self.thread = QThread()
        self.worker = EstrattoreMetadati(percorso)
        self.worker.moveToThread(self.thread)

        if numero_immagine == 1:
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_metadati1_estratti)
        else:
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_metadati2_estratti)

        self.worker.error.connect(self.on_errore_estrazione)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_metadati1_estratti(self, metadati):
        self.metadati1 = metadati
        self.controlla_e_confronta()

    def on_metadati2_estratti(self, metadati):
        self.metadati2 = metadati
        self.controlla_e_confronta()

    def on_errore_estrazione(self, messaggio_errore):
        QMessageBox.warning(self, "Errore Estrazione", messaggio_errore)
        if self.metadati1 is None and self.percorso_immagine1:
            self.visualizzatore_metadati1.clear()
        if self.metadati2 is None and self.percorso_immagine2:
            self.visualizzatore_metadati2.clear()

    def controlla_e_confronta(self):
        if self.metadati1 and self.visualizzatore_metadati1.toPlainText().startswith("Estrazione"):
            self.mostra_metadati(self.visualizzatore_metadati1, self.metadati1)
        if self.metadati2 and self.visualizzatore_metadati2.toPlainText().startswith("Estrazione"):
            self.mostra_metadati(self.visualizzatore_metadati2, self.metadati2)

        if self.metadati1 is not None and self.metadati2 is not None:
            chiavi_comuni, chiavi_comuni_con_valori_diversi, metadati_unici1, metadati_unici2 = confronta_metadati(self.metadati1, self.metadati2)
            comuni_identici = set(chiavi_comuni) - set(chiavi_comuni_con_valori_diversi.keys())
            comuni_diversi = set(chiavi_comuni_con_valori_diversi.keys())

            self.mostra_metadati(self.visualizzatore_metadati1, self.metadati1, comuni_identici, comuni_diversi)
            self.mostra_metadati(self.visualizzatore_metadati2, self.metadati2, comuni_identici, comuni_diversi)

            num_comuni_valore_identico = len(comuni_identici)
            testo_risultato = (f"Esito Finale:\nTrovati {len(chiavi_comuni)} metadati in comune "
                           f"({num_comuni_valore_identico} con valore identico, {len(comuni_diversi)} con valore diverso).\n"
                           f"Immagine 1 ha {len(metadati_unici1)} metadati unici. "
                           f"Immagine 2 ha {len(metadati_unici2)} metadati unici.")
            self.etichetta_risultato.setText(testo_risultato)
        elif self.percorso_immagine1 and self.percorso_immagine2:
            self.etichetta_risultato.setText("In attesa del completamento dell'estrazione dei metadati...")
        elif self.percorso_immagine1 or self.percorso_immagine2:
            self.etichetta_risultato.setText("Carica la seconda immagine per avviare il confronto.")
        else:
            self.etichetta_risultato.setText("Carica due immagini per iniziare il confronto.")

    def mostra_metadati(self, widget_testo, metadati, comuni_identici=None, comuni_diversi=None):
        if comuni_identici is None:
            comuni_identici = set()
        if comuni_diversi is None:
            comuni_diversi = set()

        html = ""
        chiavi_ordinate = sorted(metadati.keys())

        for chiave in chiavi_ordinate:
            valore = metadati[chiave]
            try:
                valore_stringa = str(valore)
            except:
                valore_stringa = repr(valore)

            if chiave in comuni_identici:
                html += f'<div style="background-color:{self.COLORE_IDENTICO};"><b>{chiave}:</b> {valore_stringa}</div>'
            elif chiave in comuni_diversi:
                html += f'<div style="background-color:{self.COLORE_DIVERSO};"><b>{chiave}:</b> {valore_stringa}</div>'
            else:
                html += f'<div><b>{chiave}:</b> {valore_stringa}</div>'

        widget_testo.setHtml(html)

    def reimposta_interfaccia(self):
        self.percorso_immagine1 = None
        self.percorso_immagine2 = None
        self.metadati1 = None
        self.metadati2 = None

        self.visualizzatore_metadati1.clear()
        self.visualizzatore_metadati2.clear()

        self.zona_rilascio1.reset()
        self.zona_rilascio2.reset()

        self.etichetta_risultato.setText("Carica due immagini per iniziare il confronto.")


def main():
    app = QApplication(sys.argv)
    finestra = FinestraPrincipale()
    finestra.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()