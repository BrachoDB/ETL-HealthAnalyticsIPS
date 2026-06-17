class NoCacheMiddleware:
    """Evita que el navegador almacene en caché las páginas HTML.

    Sin estas cabeceras, tras cerrar sesión el botón "Atrás" puede mostrar
    páginas del dashboard con datos privados servidas desde el caché/bfcache.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.headers.get('Content-Type', '')
        if content_type.startswith('text/html'):
            response.headers['Cache-Control'] = (
                'no-store, no-cache, must-revalidate, max-age=0'
            )
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
