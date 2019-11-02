class ViewNameMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        request.view_name = ".".join((view_func.__module__, view_func.__name__))
