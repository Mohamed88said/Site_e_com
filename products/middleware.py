class ProductHistoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/products/') and request.resolver_match and request.resolver_match.url_name == 'detail':
            pk = request.resolver_match.kwargs.get('pk')
            if pk:
                history = request.session.get('history', [])
                if pk in history:
                    history.remove(pk)
                history.insert(0, pk)
                request.session['history'] = history[:5]
        return response