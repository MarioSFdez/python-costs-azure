# Automatización de Costos en Azure con Python

Herramienta que automatiza el monitoreo y pronóstico de costos en Azure, utilizando sus APIs para obtener datos sobre gastos diarios y mensuales. Genera reportes detallados y envía actualizaciones por correo electrónico en formato HTML, facilitando el control de costos en tiempo real.

## Introducción
**Cost Management** en Azure es un conjunto de herramientas diseñadas para ayudar a las organizaciones a **monitorear, analizar y optimizar** los **gastos** de sus **recursos** en la nube.

Esta aplicación aprovecha las APIs de Cost Management para automatizar la generación de informes y el envío por correo electrónico, ofreciendo una visión clara sobre los siguientes puntos:
* **Costos mensuales acumulados.**
* **Costos diarios.**
* **Top 5 servicios con mayor gasto.**
* **Top 5 grupos de recursos con mayor gasto.**
* **Saldo restante de créditos**

## Requisitos
**1.** Suscripción de Azure

**2.** Una aplicación registrada en Azure Active Directory con permisos de lectura sobre los costos de suscripción.

**3.** Doble factor de la cuenta de correo utilizada

**4.** Crear una contraseña de aplicaciones en Gmail

## Permisos en Azure
Necesitaremos registrar una aplicación en Azure a través de Microsoft Entra ID. Copiaremos el id de la aplicación ```<client_id>```, el id de directorio ```<tenant_id>``` para poder autenticarse en Azure a traves del modelo OAuth 2.0.

Debemos de crear un secreto ```<client_secret>``` o certificado para poder autenticarnos a traves de Certificados y Secretos

![image](https://github.com/user-attachments/assets/c85eb725-f8ac-472a-9b4d-e1b2adaf604b)

Además, debemos de asignarle el rol de Reader + Cost Management para permitir elacceso a los costos de la suscripción

![image](https://github.com/user-attachments/assets/4b4f3102-841f-496d-acc1-4b7f33204219)
![image](https://github.com/user-attachments/assets/bb225941-6466-4e90-ae61-a6b882c28dbd)

## Contraseñas de aplicación
Para enviar correos electrónicos desde la aplicación, es crucial proteger la cuenta de correo utilizada. Será necesario tener el 2FA activado.
Muchos proveedores de correo, como Gmail, no permiten que aplicaciones externas accedan directamente a tu cuenta principal por razones de seguridad. En su lugar, será necesario generar una contraseña de aplicaciones que actúa como una clave única para acceder desde el script

![image](https://github.com/user-attachments/assets/b3b3e8d3-6ccd-49fc-82f4-b6341c3cd372)

## Ejecución del script

Una vez creado la contraseña de aplicación, nos iremos a la aplicación desarrollada con Python y agregaremos los anteriores valores en el fichero [.env](./.env)

![image](https://github.com/user-attachments/assets/2019e3cd-d80e-4680-bdb3-d4c9a5729a54)

A continuación, crearemos un entorno virtual de Python

```
python3 -m venv env
source env/bin/activate
```

Dentro del entorno virtual instalaremos la lista de paquetes y librerias que seránnecesarias para que funcione la aplicación

```
pip install -r requirements.txt
```

Posteriormente, ejecutaremos el programa, el cual, nos proporcionará información sobre los costes de la suscripción

```
python3 app.py
```

![image](https://github.com/user-attachments/assets/a34c1f73-f8af-431b-b786-9442e9e5879b)

Por último, nos iremos al correo del destinatario y comprobaremos que se habrá generado un informe que incluye costos mensuales, costos diarios, y un desglose de los recursos más costosos, junto con la proyección del mes.

![image](https://github.com/user-attachments/assets/4ccb799a-c051-47aa-ba9b-04fddde30335)

## Autor
| [<img src="https://avatars.githubusercontent.com/u/140948023?s=400&u=f1aaaefb0cd2fe5f6be92fba05411a79d3a92878&v=4" width=115><br><sub>Mario Sierra Fernández</sub>](https://github.com/MarioSFdez) |
| :---: | 
