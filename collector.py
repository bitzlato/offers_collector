from offers_collector.collector import Collector
from offers_collector import create_app


app = create_app(init_appbuilder=False)


if __name__ == '__main__':
    Collector().start()
