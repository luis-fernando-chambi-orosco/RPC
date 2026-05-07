import amqpstorm
from amqpstorm import Message

# --- CONFIGURACIÓN DE CLOUDAMQP ---
# USA LA MISMA URL QUE PUSISTE EN APP.PY
CLOUDAMQP_URL = 'amqps://qyrkkzaa:UEt7Rh0kvsoHt-BOJzGGLcq02XDNxv0x@duck.lmq.cloudamqp.com/qyrkkzaa'
def on_request(message):
    """Procesar solicitudes RPC."""
    try:
        # Decodificar el cuerpo si viene como bytes
        body = message.body
        print(f"[Servidor RPC] Recibido: {body}")

        # Simulación de procesamiento
        response = f"Hola, recibí tu mensaje: {body}"

        # Crear respuesta
        response_message = Message.create(
            message.channel,
            response
        )

        # Mantener relación request-response (IMPORTANTE)
        response_message.correlation_id = message.correlation_id

        # Enviar respuesta a la cola que nos indicó el cliente
        response_message.publish(
            routing_key=message.reply_to
        )

        print(f"[Servidor RPC] Respuesta enviada.")

        # Confirmar mensaje procesado (Ack)
        message.ack()

    except Exception as e:
        print(f"[Servidor RPC] Error procesando solicitud: {e}")

def main():
    try:
        # CAMBIO CLAVE: Usamos la URL de la nube y UriConnection
        connection = amqpstorm.UriConnection(CLOUDAMQP_URL)
        channel = connection.channel()

        # Cola RPC principal (debe coincidir con la del cliente)
        channel.queue.declare(
            queue='rpc_queue',
            durable=True
        )

        # Prefetch 1: No envíes más de un mensaje a la vez a este worker
        channel.basic.qos(1)

        print("[Servidor RPC] Esperando solicitudes en la nube...")

        channel.basic.consume(
            on_request,
            queue='rpc_queue'
        )

        channel.start_consuming()

    except Exception as e:
        print(f"[Servidor RPC] Error de conexión: {e}")
    except KeyboardInterrupt:
        print("[Servidor RPC] Detenido por el usuario.")

if __name__ == "__main__":
    main()