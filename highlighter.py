import sublime


class CodeHighlighter(object):

    def __init__(self, settings):
        self.settings = settings
        self.region_key = 'sublimesbt_error_reporting'
        self.status_key = 'SBT'
        self._update_highlight_args()
        settings.add_on_change(self._update_highlight_args)

    def set_status_message(self, view, message):
        if message:
            view.set_status(self.status_key, message)
        else:
            view.erase_status(self.status_key)

    def clear(self, view):
        view.erase_regions(self.region_key)

    def highlight(self, view, lines, replace=False):
        regions = self._all_regions(view, self._create_regions(view, lines), replace)
        view.add_regions(self.region_key, regions, self.region_scope, *self._highlight_args)

    def _all_regions(self, view, new_regions, replace):
        if replace:
            return new_regions
        else:
            return view.get_regions(self.region_key) + new_regions

    def _create_regions(self, view, lines):
        return [self._create_region(view, l) for l in lines]

    def _create_region(self, view, lineno):
        line = view.line(view.text_point(lineno - 1, 0))
        r = view.find(r'\S', line.begin())
        if line.contains(r):
            return sublime.Region(r.begin(), line.end())
        else:
            return line

    def _update_highlight_args(self):
        self.region_scope = self.settings.get('error_scope')
        style = self.settings.get('mark_style')
        self._highlight_args = self._create_highlight_args(style)

    def _create_highlight_args(self, style):
        if style == 'dot':
            return ['dot', sublime.HIDDEN]
        elif style == 'outline':
            return [sublime.DRAW_OUTLINED]
        else:
            return ['dot', sublime.DRAW_OUTLINED]
