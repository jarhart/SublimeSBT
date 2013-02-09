import sublime

try:
    from .util import group_by
except(ValueError):
    from util import group_by


class CodeHighlighter(object):

    def __init__(self, settings):
        self.settings = settings
        self.status_key = 'SBT'
        self._update_highlight_args()
        settings.add_on_change(self._update_highlight_args)

    def set_status_message(self, view, message):
        if message:
            view.set_status(self.status_key, message)
        else:
            view.erase_status(self.status_key)

    def clear(self, view):
        for error_type in ['error', 'failure', 'warning']:
            view.erase_regions(self.region_key(error_type))

    def highlight(self, view, errors, replace=False):
        grouped = group_by(errors, lambda e: e.error_type)
        for error_type in ['warning', 'failure', 'error']:
            lines = [e.line for e in grouped.get(error_type, list())]
            self._highlight_lines(view, lines, error_type, replace)

    def region_key(self, error_type):
        return 'sublimesbt_%s_marking' % error_type

    def region_scope(self, error_type):
        return self._mark_settings(error_type)['scope']

    def _highlight_lines(self, view, lines, error_type, replace):
        regions = self._all_regions(view, self._create_regions(view, lines), error_type, replace)
        view.add_regions(self.region_key(error_type),
                         regions,
                         self.region_scope(error_type),
                         *self._highlight_args[error_type])

    def _all_regions(self, view, new_regions, error_type, replace):
        if replace:
            return new_regions
        else:
            return view.get_regions(self.region_key(error_type)) + new_regions

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
        self._highlight_args = {
            'error': self._create_highlight_args('error'),
            'failure': self._create_highlight_args('failure'),
            'warning': self._create_highlight_args('warning')
        }

    def _create_highlight_args(self, error_type):
        style = self._mark_settings(error_type)['style']
        if style == 'dot':
            return ['dot', sublime.HIDDEN]
        elif style == 'outline':
            return [sublime.DRAW_OUTLINED]
        else:
            return ['dot', sublime.DRAW_OUTLINED]

    def _mark_settings(self, error_type):
        return self.settings.get('%s_marking' % error_type)
