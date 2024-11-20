import os
import requests
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Variables de configuración: credenciales y detalles del servidor SMTP
client_id = os.getenv("AZURE_CLIENT_ID")
tenant_id = os.getenv("AZURE_TENANT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
subscription_id = os.getenv("SUBSCRIPTION_ID")
sender_email = os.getenv("SENDER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")

# URL para obtener el token de acceso de Azure
url_token = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

# Datos necesarios para obtener el token de acceso de Azure
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://management.azure.com/.default',
    'grant_type': 'client_credentials'
}

# Obtener el token de acceso de Azure
response = requests.post(url_token, data=payload)
token = response.json().get('access_token')

# Verificar si se obtuvo el token correctamente
if token:
    print("Token obtenido con éxito")
else:
    print("Error al obtener el token:", response.json())

# Cabecera de la solicitud para las APIs de Azure
headers = {
    'Authorization': f"Bearer {token}",
    'Content-Type': 'application/json',
}

# Configurar la solicitud para obtener los costos del mes
url_costs = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2024-08-01"

# Cuerpo de la consulta para obtener los costos mensuales y diarios
body_costs = {
    "type": "ActualCost",
    "timeframe": "MonthToDate",
    "dataset": {
        "granularity": "Daily",
        "aggregation": {
            "totalCost": {
                "name": "PreTaxCost",
                "function": "Sum"
            }
        }
    }
}

# Realizar la solicitud para obtener los costos
response_costs = requests.post(url=url_costs, headers=headers, json=body_costs)
rows = response_costs.json().get('properties', {}).get('rows', [])

# Calcular el costo total del mes
total_cost = sum(row[0] for row in rows)
print(f"Costo total acumulado en el mes: {total_cost} EUR")

# Obtener el costo diario (último registro)
last_record = rows[-1]
cost_today = last_record[0]
date_today = datetime.strptime(str(last_record[1]), "%Y%m%d").strftime("%d-%m-%Y")

print(f"Coste de hoy ({date_today}): {cost_today} EUR")

# Calcular el saldo restante de créditos
initial_credit = 145  # Créditos iniciales
remaining_credit = initial_credit - total_cost
print(f"Créditos restantes: {remaining_credit} EUR")

# Configurar la solicitud para el pronóstico de costos
url_forecast = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/forecast?api-version=2024-08-01"

# Definir el rango de fechas para el pronóstico (primer y último día del mes)
current_date = datetime.now()
first_day_of_month = current_date.replace(day=1)
first_day_of_next_month = (first_day_of_month + timedelta(days=32)).replace(day=1)
last_day_of_month = first_day_of_next_month - timedelta(days=1)

# Convertir las fechas a formato adecuado para la API
first_day_str = first_day_of_month.strftime("%Y-%m-%dT00:00:00+00:00")
last_day_str = last_day_of_month.strftime("%Y-%m-%dT23:59:59+00:00")

# Cuerpo de la consulta para el pronóstico
body_forecast = {
    "type": "ActualCost",
    "timeframe": "Custom",
    "timePeriod": {
        "from": first_day_str,
        "to": last_day_str
    },
    "dataset": {
        "granularity": "Daily",
        "aggregation": {
            "totalCost": {
                "name": "PreTaxCost",
                "function": "Sum"
            }
        }
    }
}

# Realizar la solicitud para obtener el pronóstico de costos
response_forecast = requests.post(url=url_forecast, headers=headers, json=body_forecast)
rows_forecast = response_forecast.json().get('properties', {}).get('rows', [])

# Calcular el pronóstico total de costos
forecast_cost = sum(row[0] for row in rows_forecast)
total_forecast = total_cost + forecast_cost
print(f"Pronóstico total para el mes: {total_forecast} EUR")

# Obtener los 5 principales grupos de recursos por costo
body_rg = {
    "type": "ActualCost",
    "timeframe": "MonthToDate",
    "dataset": {
        "granularity": "None",
        "aggregation": {
            "totalCost": {
                "name": "PreTaxCost",
                "function": "Sum"
            }
        },
        "grouping": [
            {
                "type": "Dimension",
                "name": "ResourceGroup"
            }
        ]
    }
}

response_rg = requests.post(url=url_costs, headers=headers, json=body_rg)
rows_rg = response_rg.json().get('properties', {}).get('rows', [])

# Ordenar y mostrar los 5 principales grupos de recursos por costo
top_rg = sorted(rows_rg, key=lambda x: x[0], reverse=True)[:5]
print("\nTop 5 Grupos de Recursos por Costo:")

counter  = 0
for group in top_rg:
    cost, group_name = group[:2]
    counter += 1
    print(f"{counter}. {group_name} -> {cost}")

# Obtener los 5 principales servicios por costo
body_sv = {
    "type": "ActualCost",
    "timeframe": "MonthToDate",
    "dataset": {
        "granularity": "None",
        "aggregation": {
            "totalCost": {
                "name": "PreTaxCost",
                "function": "Sum"
            }
        },
        "grouping": [
            {
                "type": "Dimension", 
                "name": "ServiceName"
            }
        ]
    }
}

response_sv = requests.post(url=url_costs, headers=headers, json=body_sv)
rows_sv = response_sv.json().get('properties', {}).get('rows', [])

# Ordenar y mostrar los 5 principales servicios por costo
top_sv = sorted(rows_sv, key=lambda x: x[0], reverse=True)[:5]
print("\nTop 5 Servicios por Costo:")

counter = 0
for service in top_sv:
    cost, service_name = service[:2]
    counter += 1
    print(f"{counter}. {service_name} --> {cost} EUR")

# Crear el mensaje HTML para el correo
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = "Reporte de Costos de Azure"

email_body = f"""\
<html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                color: #0078D7;
                font-size: 24px;
            }}
            h2 {{
                color: #333;
                font-size: 20px;
                margin-top: 20px;
            }}
            p, ol {{
                font-size: 14px;
                margin-bottom: 10px;
            }}
            ol {{ 
                padding-left: 20px;
            }}
            b {{
                font-weight: bold;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .highlight {{
                font-size: 16px;
                color: #E74C3C;
            }}
        </style>
    </head>
    <body>
        <h1>Reporte de Costos de Azure</h1>

        <div class="section">
            <h2>Resumen General</h2>
            <p><b>Coste total acumulado en el mes:</b> {total_cost} EUR</p>
            <p><b>Coste diario ({date_today}):</b> {cost_today} EUR </p>
            <p><b>Créditos restantes:</b> <span class="highlight">{remaining_credit} EUR</span></p>
            <p><b>Previsión total para el mes:</b> {total_forecast} EUR</p>
        </div>

        <div class="section">
            <h2>Top 5 Grupos de Recursos</h2>
            <ol>
                {"".join(f"<li><b>{group[1]}</b>: {group[0]:.2f} EUR</li>" for group in top_rg)}            </ol>
        </div>

        <div class="section">
            <h2>Top 5 Servicios</h2>
            <ol>
                {"".join(f"<li><b>{service[1]}</b>: {service[0]:.2f} EUR</li>" for service in top_sv)}            </ol>
        </div>
    </body>
</html>
"""

# Adjuntar el cuerpo HTML al mensaje
part = MIMEText(email_body, "html")
message.attach(part)

# Enviar el correo electrónico
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Conexión segura
        server.login(sender_email, email_password)  # Iniciar sesión en el servidor SMTP
        server.sendmail(sender_email, receiver_email, message.as_string())  # Enviar el correo
    print("Correo enviado correctamente.")
except Exception as e:
    print(f"Error al enviar el correo: {e}")