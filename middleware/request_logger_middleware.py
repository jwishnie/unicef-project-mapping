from django.template import Template, Context

class RequestLogMiddleware:
    def process_response ( self, request, response ): 
        if request.method == 'POST':
            print request.POST
        return response
