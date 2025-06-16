"""Speechmatics Batch Transcription GUI
======================================
• Drag‑and‑drop up to 10 audio/video files.
• Checkbox for **MP3** (default) or WAV extraction (16 kHz mono).
• Sends parallel Batch‑V2 jobs (fa) to Speechmatics.

Build to single EXE:
    pyinstaller -y pyi-speechmatics.spec
"""
from __future__ import annotations
import os, sys, json, mimetypes, subprocess, shutil, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import Qt, QRunnable, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QLabel, QHBoxLayout,
    QCheckBox, QMessageBox
)

# ────────── helpers ──────────
FFMPEG = shutil.which("ffmpeg") or os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "ffmpeg.exe")
CFG = {"api_token": os.getenv("SPEECHMATICS_API_TOKEN", ""), "language": "fa"}
if Path("config.json").exists(): CFG.update(json.loads(Path("config.json").read_text()))
if not CFG["api_token"]: raise RuntimeError("Speechmatics API token not found (env var or config.json)")

def is_av(p: Path) -> bool:
    mt, _ = mimetypes.guess_type(p)
    return mt and (mt.startswith("audio/") or mt.startswith("video/"))

def convert(src: Path, mp3: bool) -> Path:
    dst = src.with_suffix(".mp3" if mp3 else ".wav")
    cmd = [FFMPEG, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000"]
    cmd += ["-b:a", "128k", str(dst)] if mp3 else [str(dst)]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst

class Sig(QObject): progress=pyqtSignal(int); status=pyqtSignal(str); done=pyqtSignal(str,str); error=pyqtSignal(str)
class Task(QRunnable):
    def __init__(self, src: Path, mp3: bool): super().__init__(); self.src=src; self.mp3=mp3; self.sig=Sig(); self.setAutoDelete(True)
    @pyqtSlot()
    def run(self):
        try:
            from speechmatics.batch_client import BatchClient
            self.sig.status.emit("Preparing…"); audio=convert(self.src,self.mp3)
            with BatchClient(CFG["api_token"]) as c:
                job=c.submit_job(audio=str(audio), transcription_config={"language":CFG["language"],"operating_point":"enhanced"})
                while True:
                    jd=c.get_job_details(job); ph=jd["job"]["job_status"]["current_phase"]; pc=int(jd["job"]["job_status"].get("progress",0)*100)
                    self.sig.status.emit(ph.capitalize()); self.sig.progress.emit(pc)
                    if ph in ("done","failed"): break; time.sleep(5)
                if ph=="failed": raise RuntimeError("Server error")
                txt=c.get_transcript(job,"txt"); srt=c.get_transcript(job,"srt")
                Path(audio.with_suffix(".txt")).write_text(txt,encoding="utf8")
                Path(audio.with_suffix(".srt")).write_text(srt,encoding="utf8")
                self.sig.done.emit(str(audio.with_suffix('.txt')),str(audio.with_suffix('.srt')))
        except Exception as e: self.sig.error.emit(str(e))

class GUI(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Speechmatics Batch"); self.resize(600,400)
        c=QWidget(); self.setCentralWidget(c); v=QVBoxLayout(c)
        v.addWidget(QLabel("<b>Drag ≤10 files → choose format → Transcribe</b>"))
        self.list=QListWidget(); v.addWidget(self.list)
        self.cb=QCheckBox("Export MP3 (otherwise WAV)"); self.cb.setChecked(True); v.addWidget(self.cb)
        h=QHBoxLayout(); add=QPushButton("Add Files…"); add.clicked.connect(self.add_dialog); h.addWidget(add)
        self.go=QPushButton("Transcribe (0)"); self.go.clicked.connect(self.start); h.addWidget(self.go); v.addLayout(h)
        self.pool=ThreadPoolExecutor(max_workers=10); self.list.dragEnterEvent=self.dragEnter; self.list.dropEvent=self.drop
    def dragEnter(self,e): e.acceptProposedAction() if e.mimeData().hasUrls() else e.ignore()
    def drop(self,e): [self.add(Path(u.toLocalFile())) for u in e.mimeData().urls()]; self.refresh()
    def add_dialog(self):
        files,_=QFileDialog.getOpenFileNames(self,"Select files"); [self.add(Path(f)) for f in files]; self.refresh()
    def add(self,p):
        if self.list.count()<10 and p.exists() and is_av(p):
            it=QListWidgetItem(str(p)); it.setData(Qt.ItemDataRole.UserRole,p); self.list.addItem(it)
    def refresh(self): self.go.setText(f"Transcribe ({self.list.count()})"); self.go.setEnabled(self.list.count()>0)
    def start(self):
        self.go.setEnabled(False)
        for i in range(self.list.count()):
            it=self.list.item(i); src=it.data(Qt.ItemDataRole.UserRole); t=Task(src,self.cb.isChecked())
            t.sig.status.connect(lambda s, item=it: item.setToolTip(s))
            t.sig.error.connect(lambda e, item=it: item.setToolTip(f"Error: {e}"))
            t.sig.done.connect(lambda *_: None); self.pool.submit(t.run)

def main():
    app=QApplication(sys.argv); GUI().show(); sys.exit(app.exec())
if __name__=="__main__": main()