from cfg.application import Application
from cfg.config import get_config_path

if __name__ == '__main__':
    app = Application()
    app.init(get_config_path())
    app.run()
