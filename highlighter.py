import sublime


class CodeHighlighter(object):

    def __init__(self):
        self.region_key = 'sublimesbt_error_reporting'
        self.error_scope = 'source.scala'
        self.status_key = 'SBT'

    def highlight(self, view, lines, replace=False):
        regions = self._regions(view, replace)
        regions.extend([view.line(view.text_point(l - 1, 0)) for l in lines])
        view.add_regions(self.region_key, regions, self.error_scope, sublime.DRAW_OUTLINED)

    def _regions(self, view, replace):
        if replace:
            return []
        else:
            return view.get_regions(self.region_key)

    def clear(self, view):
        view.erase_regions(self.region_key)

    def set_status_message(self, view, message):
        if message:
            view.set_status(self.status_key, message)
        else:
            view.erase_status(self.status_key)
