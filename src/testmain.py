from cfg.application import Application

if __name__ == '__main__':
    app = Application()
    app.init('../config/mietar-exp.yml')
    app.run()
