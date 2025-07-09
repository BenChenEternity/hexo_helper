from collections import defaultdict


class WidgetManager:
    def __init__(self):
        self.by_id = {}
        self.by_widget = {}
        self.by_tag = defaultdict(list)

    def register(self, widget, widget_id=None, tags=None):
        if widget_id:
            self.by_id[widget_id] = widget
            self.by_widget[widget] = widget_id
        if tags:
            for tag in tags:
                self.by_tag[tag].append(widget)

    def get_by_id(self, widget_id):
        return self.by_id.get(widget_id)

    def get_id_by_widget(self, widget):
        return self.by_widget.get(widget)

    def get_by_tag(self, tag):
        return self.by_tag.get(tag, [])

    def update_all(self, tag, **kwargs):
        for widget in self.get_by_tag(tag):
            widget.config(**kwargs)
