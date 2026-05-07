import threading
import os
from time import sleep
from flask import Flask, render_template, request
import amqpstorm
from amqpstorm import Message

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDAMQP ---
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL', 'amqps://qyrkkzaa:UEt7Rh0kvsoHt-BOJzGGLcq02XDNxv0x@duck.lmq.cloudamqp.com/qyrkkzaa')

class RpcClient(object):
    def __init__(self, amqp_url, rpc_queue):
        self.queue = {}
        self.url = amqp_url
        self.channel = None
        self.connection = None
        self.callback_queue = None
        self.rpc_queue = rpc_queue
        self.open()

    def open(self):
        self.connection = amqpstorm.UriConnection(self.url)
        self.channel = self.connection.channel()
        self.channel.queue.declare(queue=self.rpc_queue, durable=True)
        result = self.channel.queue.declare(exclusive=True)
        self.callback_queue = result['queue']
        self.channel.basic.consume(self._on_response, no_ack=True, queue=self.callback_queue)
        self._create_process_thread()

    def _create_process_thread(self):
        thread = threading.Thread(target=self._process_data_events)
        thread.daemon = True
        thread.start()

    def _process_data_events(self):
        try:
            self.channel.start_consuming(to_tuple=False)
        except Exception:
            pass

    def _on_response(self, message):
        self.queue[message.correlation_id] = message.body

    def send_request(self, payload):
        message = Message.create(self.channel, payload)
        message.reply_to = self.callback_queue
        self.queue[message.correlation_id] = None
        message.publish(routing_key=self.rpc_queue)
        return message.correlation_id

    def has_response(self, correlation_id):
        return self.queue.get(correlation_id) is not None

    def get_response(self, correlation_id):
        response = self.queue.get(correlation_id)
        if correlation_id in self.queue:
            del self.queue[correlation_id]
        return response

# Inicialización segura del cliente
RPC_CLIENT = None

def get_rpc_client():
    global RPC_CLIENT
    if RPC_CLIENT is None:
        RPC_CLIENT = RpcClient(CLOUDAMQP_URL, 'rpc_queue')
    return RPC_CLIENT

@app.route('/', methods=['GET', 'POST'])
def index():
    respuesta = None
    if request.method == 'POST':
        try:
            client = get_rpc_client()
            mensaje = request.form['mensaje']
            corr_id = client.send_request(mensaje)

            timeout = 60
            elapsed = 0
            while not client.has_response(corr_id):
                sleep(0.1)
                elapsed += 0.1
                if elapsed >= timeout:
                    respuesta = "Timeout: el servidor RPC no respondió."
                    break
            else:
                respuesta = client.get_response(corr_id)
        except Exception as e:
            respuesta = f"Error: {str(e)}"
    return render_template('index.html', respuesta=respuesta)

# --- CONFIGURACIÓN FINAL PARA RAILWAY ---
if __name__ == '__main__':
    # Usamos puerto 8080 por defecto para Railway
    port = int(os.environ.get("PORT", 8080))
    # Importante: host 0.0.0.0 y debug False para evitar el error de respuesta
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)