import amqpstorm
from amqpstorm import Message


def on_request(message):
    """Procesar solicitudes RPC."""

    try:
        print(f"[Servidor RPC] Recibido: {message.body}")

        # Simulación de procesamiento
        response = f"Hola, recibí tu mensaje: {message.body}"

        # Crear respuesta
        response_message = Message.create(
            message.channel,
            response
        )

        # Mantener relación request-response
        response_message.correlation_id = message.correlation_id

        # Cola callback del cliente
        response_message.reply_to = message.reply_to

        # Enviar respuesta
        response_message.publish(
            routing_key=message.reply_to
        )

        print(f"[Servidor RPC] Respuesta enviada.")

        # Confirmar mensaje procesado
        message.ack()

    except Exception as e:
        print(f"[Servidor RPC] Error procesando solicitud: {e}")


def main():

    try:
        connection = amqpstorm.Connection(
            'localhost',
            'guest',
            'guest'
        )

        channel = connection.channel()

        # Cola RPC principal
        channel.queue.declare(
            queue='rpc_queue',
            durable=True
        )

        print("[Servidor RPC] Esperando solicitudes...")

        channel.basic.consume(
            on_request,
            queue='rpc_queue'
        )

        channel.start_consuming()

    except Exception as e:
        print(f"[Servidor RPC] Error de conexión: {e}")


if __name__ == "__main__":
    main()