from datetime import datetime
import os


class FileLogger:
    def __init__(self, dir, enabled):
        self.path = f"{dir}{datetime.now().strftime("%d_%m_%Y")}.log"
        self.enabled = enabled
        if enabled and not os.path.exists(dir):
            os.mkdir(dir)

    def log(self, str):
        if self.enabled:
            with open(self.path, "a", encoding="utf8") as file:
                file.write(f"{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}  {str}\n")
