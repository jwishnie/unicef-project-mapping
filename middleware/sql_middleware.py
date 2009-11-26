from django.db import connection
from django.template import Template, Context

class SQLLogMiddleware:

    def process_response ( self, request, response ): 
        time = 0.0
        for q in connection.queries:
		time += float(q['time'])
		
		    
        
        t = Template('''
            <p><em>Total query count:</em> {{ count }}<br/>
            <em>Total execution time:</em> {{ time }}</p>
            <ul class="sqllog">
                {% for sql in sqllog %}
                    <li>{{ sql.time }}: {{ sql.sql }}</li>
                {% endfor %}
            </ul>
        ''')

        response.content = "%s%s" % ( response.content, t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time})))
        return response
