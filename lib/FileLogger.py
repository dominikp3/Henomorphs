from datetime import datetime
import os


class FileLogger:
    def __new__(self, dir=None, enabled=None):
        if not hasattr(self, "instance"):
            self.instance = super(FileLogger, self).__new__(self)
            self.enabled = False
        if dir is not None and enabled is not None:
            self.path = f"{dir}{datetime.now().strftime("%d_%m_%Y")}.log"
            self.enabled = enabled
            if enabled and not os.path.exists(dir):
                os.makedirs(dir)
        return self.instance

    def log(self, str):
        if self.enabled:
            with open(self.path, "a", encoding="utf8") as file:
                file.write(f"{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}  {str}\n")
