from livereload import Server, shell
from render_website import on_reload


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
