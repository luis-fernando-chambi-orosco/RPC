import threading
from time import sleep
from flask import Flask, render_template, request
import amqpstorm
from amqpstorm import Message

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDAMQP ---
# REEMPLAZA ESTA URL con la que copiaste de tu instancia "RPC" en CloudAMQP
CLOUDAMQP_URL = 'amqps://qyrkkzaa:UEt7Rh0kvsoHt-BOJzGGLcq02XDNxv0x@duck.lmq.cloudamqp.com/qyrkkzaa'

class RpcClient(object):
    """Asynchronous RPC Client compatible con la nube."""

    def __init__(self, amqp_url, rpc_queue):
        self.queue = {}
        self.url = amqp_url
        self.channel = None
        self.connection = None
        self.callback_queue = None
        self.rpc_queue = rpc_queue

        try:
            self.open()
            print("[Cliente RPC] Conexión establecida con CloudAMQP correctamente.")
        except Exception as e:
            print(f"[Cliente RPC] Error al conectar: {e}")

    def open(self):
        """Abre la conexión usando la URL (UriConnection)."""
        # CAMBIO CLAVE: Usamos UriConnection para la nube
        self.connection = amqpstorm.UriConnection(self.url)
        self.channel = self.connection.channel()

        # Cola principal RPC
        self.channel.queue.declare(
            queue=self.rpc_queue,
            durable=True
        )

        # Cola exclusiva de callback
        result = self.channel.queue.declare(exclusive=True)
        self.callback_queue = result['queue']

        # Consumidor de respuestas
        self.channel.basic.consume(
            self._on_response,
            no_ack=True,
            queue=self.callback_queue
        )

        self._create_process_thread()

    def _create_process_thread(self):
        thread = threading.Thread(target=self._process_data_events)
        thread.daemon = True
        thread.start()

    def _process_data_events(self):
        try:
            self.channel.start_consuming(to_tuple=False)
        except Exception as e:
            print(f"[Cliente RPC] Error consumiendo mensajes: {e}")

    def _on_response(self, message):
        self.queue[message.correlation_id] = message.body

    def send_request(self, payload):
        try:
            message = Message.create(self.channel, payload)
            message.reply_to = self.callback_queue
            self.queue[message.correlation_id] = None
            message.publish(routing_key=self.rpc_queue)
            return message.correlation_id
        except Exception as e:
            print(f"[Cliente RPC] Error enviando solicitud: {e}")
            return None

    def has_response(self, correlation_id):
        return self.queue.get(correlation_id) is not None

    def get_response(self, correlation_id):
        response = self.queue.get(correlation_id)
        if correlation_id in self.queue:
            del self.queue[correlation_id]
        return response

# Inicializar cliente globalmente para que Flask lo use
# Nota: rpc_queue debe ser el mismo nombre que use el rpc_server.py
RPC_CLIENT = RpcClient(CLOUDAMQP_URL, 'rpc_queue')

@app.route('/', methods=['GET', 'POST'])
def index():
    respuesta = None
    if request.method == 'POST':
        try:
            mensaje = request.form['mensaje']
            corr_id = RPC_CLIENT.send_request(mensaje)

            if corr_id is None:
                respuesta = "No se pudo enviar la solicitud RPC."
            else:
                timeout = 30
                elapsed = 0
                while not RPC_CLIENT.has_response(corr_id):
                    sleep(0.1)
                    elapsed += 0.1
                    if elapsed >= timeout:
                        respuesta = "Timeout: el servidor RPC no respondió."
                        break
                else:
                    respuesta = RPC_CLIENT.get_response(corr_id)
        except Exception as e:
            respuesta = f"Error de conexión RPC: {str(e)}"

    return render_template('index.html', respuesta=respuesta)

if __name__ == '__main__':
    app.run(debug=True)