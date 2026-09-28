import json
import os

import boto3
from boto3.dynamodb.conditions import Key

JUEGOS = ["doom", "pacman"]

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ["TABLA_PUNTAJES"])


def top10(juego):
    resp = tabla.query(KeyConditionExpression=Key("juego").eq(juego))
    items = sorted(resp.get("Items", []), key=lambda i: int(i["puntaje"]), reverse=True)[:10]
    return [{"jugador": i["jugador"], "puntaje": int(i["puntaje"])} for i in items]


def handler(event, context):
    params = event.get("queryStringParameters") or {}
    juego = params.get("juego")
    juegos = [juego] if juego else JUEGOS
    resultado = {j: top10(j) for j in juegos}
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(resultado),
    }
