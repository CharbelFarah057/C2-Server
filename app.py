from C2Server import create_app
from C2Server.threaded_server import init_server
import threading

app = create_app()

if __name__ == '__main__':
    server_thread = threading.Thread(target=init_server)
    server_thread.start()
    app.run(debug=False)
