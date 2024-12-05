<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Pipeline y gestión de solicitudes HTTP en streaming</h3>

  <p align="center">
    Una aplicación para monitorear logs de Nginx
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Tabla de contenido</summary>
  <ol>
    <li>
      <a href="#about-the-project">Acerca de este proyecto</a>
      <ul>
        <li><a href="#built-with">Construido con</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Iniciando</a>
      <ul>
        <li><a href="#prerequisites">Prerequisitos</a></li>
        <li><a href="#installation">Instalación</a></li>
      </ul>
    </li>
    <li><a href="#usage">Uso</a></li>
    <li><a href="#next-steps">Siguientes pasos</a></li>
  </ol>
</details>


<a id="about-the-project"></a>

<!-- ABOUT THE PROJECT -->
## Acerca de este proyecto

![](https://richardhapb.s3.us-east-2.amazonaws.com/resources/2024-12-04-09-28-09.gif)

En cada página web existe una gran cantidad de solicitudes realizadas por software malicioso que intenta obtener información confidencial o acceso a nuestro sistema. Este proyecto busca generar insights relevantes para poder gestionar las ips que se conectan a nuestra página web, con lo cual podemos tomar la decisión de bloquearlas o generar alguna otra acción personalizada. La ventaja de este enfoque es que el backend y el frontend son independientes y también las diferentes herramientas utilizadas, las cuales se quedan en su totalidad en contenedores Docker para facilitar el despliegue.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<a id="built-with"></a>
### Construido con

A continuación listaré las herramientas utilizadas para el proyecto.

* Kafka
* Fluent-bit
* ZooKeeper
* PostgreSQL
* CloudBeaver
* Docker
* Nginx

**Backend (Python)**
- Flask
- Gunicorn
- Kafka-Consumer
- Gevent

**Frontend (Javascript)**
- ViteJS
- Typescript
- React
- Tremor (dashboards)
- TailwindCSS

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<a id="getting-started"></a>
<!-- GETTING STARTED -->
## Iniciando

El proceso de inicialización e instalación es muy simple ya que está gestionado con Docker.


<a id="prerequisites"></a>
### Prerequisitos

Tener instalado Docker.

<a id="installation"></a>
### Instalación

Una vez generadas las variables de entorno podemos levantar la aplicación.

1. Generar la API KEY para generar consultas de cada ip, debes registrarte en [abuseipd](https://www.abuseipdb.com) y solicitarla (sin costo).

2. Clona el repositorio

   ```sh
   git clone git@github.com:richardhapb/ip-analytics.git
   ```

2. Crea las variables de entorno en la raíz del proyecto
* .env
  ```sh
    ABUSEIPDB_API_KEY=8sac8080.... # API KEY de ABUSEIPD
    ABUSEIPDB_CHECK_URL=https://api.abuseipdb.com/api/v2/check

    POSTGRES_SCHEMA=ip_analytics
    POSTGRES_DB=postgres
    POSTGRES_HOST=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_HOST_PORT=5433

    NGINX_LOG_DIR=./logs # Logs de ejemplo, ideal que apunte a directorio donde nginx almacena los logs

    FRONTEND_URL=http://localhost:8082
  ```
3. Levanta el proceso de Docker compose

   ```sh
   docker compose up --build
   ```
Una vez cargue la aplicación estará escuchando en http://localhost:8082. Si tus registros de logs son muy extensos, probablemente tarde un poco al comienzo en cargar los datos a la base de datos, ya que tiene que consultar la API por cada ip.

¡Además en el puerto 8978 tendrás CloudBeaver para administrar la base de datos! Encuéntralo en http://localhost:8978

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<a id="usage"></a>
## Uso

Una vez la aplicación funcionando se pueden observar en el dashboard los indicadores de cantidad de solicitudes, la tabla con las ips y el mapa con las ubicaciones.

La tabla contiene los siguientes datos:

1. IP - Dirección ip del registro
2. Dominio - Dominio que tiene registrado la ip
3. País - Código del país de donde procede la IP
4. Último reporte - Último reporte de actividad maliciosa en la web AbuseIPDB
5. Reportes totales - Cantidad de reportes de actividad maliciosa en la web AbuseIPDB
6. Estado - Clasificación según cantidad de reportes

<a id="next-steps"></a>
## Siguientes pasos

Posibles mejoras que se pueden implementar

- Sistema de autenticación en el backend
- Más filtros
- Más indicadores
- Capturar mayor cantidad de datos
- Conectar múltiples logs
- Bloqueo automático de ips (configuración Nginx dinámica)
- Clusterizacón de los datos
- Implementación de Airflow para orquestar trabajos de actualización y flujos de decisiones

<p align="right">(<a href="#readme-top">back to top</a>)</p>
