import json
import os

import boto3

JUEGOS = ("doom", "pacman")

sqs = boto3.client("sqs")
COLA_URL = os.environ["COLA_PUNTAJES_URL"]


def respuesta(codigo, cuerpo):
    return {
        "statusCode": codigo,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(cuerpo),
    }


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except ValueError:
        return respuesta(400, {"error": "El cuerpo no es un JSON válido"})

    if not isinstance(body, dict):
        return respuesta(400, {"error": "El cuerpo debe ser un objeto JSON"})

    jugador = body.get("jugador")
    juego = body.get("juego")
    puntaje = body.get("puntaje")

    if not isinstance(jugador, str) or not jugador.strip():
        return respuesta(400, {"error": "jugador es obligatorio"})
    if juego not in JUEGOS:
        return respuesta(400, {"error": "juego debe ser doom o pacman"})
    if isinstance(puntaje, bool) or not isinstance(puntaje, int) or puntaje < 0:
        return respuesta(400, {"error": "puntaje debe ser un entero mayor o igual a 0"})

    sqs.send_message(
        QueueUrl=COLA_URL,
        MessageBody=json.dumps({"jugador": jugador.strip(), "juego": juego, "puntaje": puntaje}),
    )
    return respuesta(202, {"estado": "encolado"})
