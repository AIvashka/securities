import json

class populate():
    def __init__(self, width, height, symbol, interval, timezone, theme, style, locale, toolbar_bg, enable_publishing, allow_symbol_change, container_id):
        self.width = width
        self.height = height
        self.symbol = symbol
        self.interval = interval
        self.timezone = timezone
        self.theme = theme
        self.style = style
        self.locale = locale
        self.toolbar_bg = toolbar_bg
        self.enable_publishing = enable_publishing
        self.allow_symbol_change = allow_symbol_change
        self.container_id = container_id


    def populate_json(self):
        return json.dumps(self.__dict__)

    def get_chart(self):
        return str(self.get_header()) + str(self.populate_json()) + self.get_close()

    def get_header(self):
        header = '"<div class="tradingview-widget-container"><div id="' + self.container_id + '"></div><script type="text/javascript">new TradingView.widget('
        return header

    def get_close(self):
        return ');</script>'