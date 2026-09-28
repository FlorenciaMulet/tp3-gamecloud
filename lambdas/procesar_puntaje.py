import json
import os

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ["TABLA_PUNTAJES"])


def guardar_si_supera(jugador, juego, puntaje):
    """Guarda solo si no hay registro o si el puntaje nuevo es mayor. Devuelve True si guardó."""
    try:
        tabla.put_item(
            Item={"juego": juego, "jugador": jugador, "puntaje": puntaje},
            ConditionExpression="attribute_not_exists(puntaje) OR puntaje < :nuevo",
            ExpressionAttributeValues={":nuevo": puntaje},
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def handler(event, context):
    procesados = 0
    for record in event["Records"]:
        # Si el cuerpo no es JSON o faltan campos, lanza excepción:
        # el mensaje vuelve a la cola y tras 3 intentos va a la DLQ.
        p = json.loads(record["body"])
        jugador = p["jugador"]
        juego = p["juego"]
        puntaje = int(p["puntaje"])

        if guardar_si_supera(jugador, juego, puntaje):
            print(f"Guardado: {jugador} - {juego} - {puntaje}")
        else:
            print(f"Ignorado (no supera el mejor puntaje): {jugador} - {juego} - {puntaje}")
        procesados += 1

    return {"procesados": procesados}
