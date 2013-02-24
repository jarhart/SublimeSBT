import sublime

try:
    from .util import group_by, maybe
except(ValueError):
    from util import group_by, maybe


class CodeHighlighter(object):

    error_types = ['error', 'failure', 'warning']

    def __init__(self, settings, current_error_in_view):
        self.settings = settings
        self._current_error_in_view = current_error_in_view
        self.bookmark_key = 'sublimesbt_bookmark'
        self.status_key = 'SBT'
        self._update_highlight_args()
        settings.add_on_change(self._update_highlight_args)

    def set_status_message(self, view, message):
        if message:
            view.set_status(self.status_key, message)
        else:
            view.erase_status(self.status_key)

    def clear(self, view):
        view.erase_regions(self.bookmark_key)
        for error_type in type(self).error_types:
            view.erase_regions(self.region_key(error_type))

    def highlight(self, view, errors, replace=False):
        bookmarked_line = self._bookmark_error(view)
        grouped = group_by(errors, lambda e: e.error_type)
        for error_type in type(self).error_types:
            lines = [e.line for e in grouped.get(error_type, list())]
            lines = [l for l in lines if l != bookmarked_line]
            self._highlight_lines(view, lines, error_type, replace)

    def region_key(self, error_type):
        return 'sublimesbt_%s_marking' % error_type

    def region_scope(self, error_type):
        return self._mark_settings(error_type)['scope']

    def _bookmark_error(self, view):
        for error in maybe(self._current_error_in_view(view)):
            region = self._create_region(view, error.line)
            self._clear_highlight(view, region)
            view.add_regions(self.bookmark_key,
                             [region],
                             self.region_scope(error.error_type),
                             *self._bookmark_args(error.error_type))
            return error.line

    def _highlight_lines(self, view, lines, error_type, replace):
        regions = self._all_regions(view, self._create_regions(view, lines), error_type, replace)
        self._highlight_regions(view, regions, error_type)

    def _highlight_regions(self, view, regions, error_type):
        view.add_regions(self.region_key(error_type),
                         regions,
                         self.region_scope(error_type),
                         *self._highlight_args[error_type])

    def _clear_highlight(self, view, region):
        for error_type in type(self).error_types:
            regions = view.get_regions(self.region_key(error_type))
            if region in regions:
                regions = [r for r in regions if r != region]
                self._highlight_regions(view, regions, error_type)

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
        if r is not None and line.contains(r):
            return sublime.Region(r.begin(), line.end())
        else:
            return line

    def _bookmark_args(self, error_type):
        return ['bookmark', self._highlight_args[error_type][-1]]

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
