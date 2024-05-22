# import os

# def create_docker_compose():
#     docker_compose_content = """
# version: '3.7'

# services:
#   redash:
#     image: redash/redash:latest
#     ports:
#       - "5000:5000"
#     environment:
#       REDASH_WEB_WORKERS: 4
#       REDASH_LOG_LEVEL: "INFO"
#     depends_on:
#       - redis
#       - postgres

#   metabase:
#     image: metabase/metabase
#     ports:
#       - "3000:3000"

#   superset:
#     image: amancevice/superset
#     environment:
#       - SUPERSET_ADMIN_USERNAME=admin
#       - SUPERSET_ADMIN_PASSWORD=admin
#       - SUPERSET_WEBSERVER_PORT=8088
#     ports:
#       - "8088:8088"

#   redis:
#     image: redis:latest

#   postgres:
#     image: postgres:latest
#     ports:
#       - "5432:5432"
#     environment:
#       POSTGRES_USER: redash
#       POSTGRES_PASSWORD: redash
#       POSTGRES_DB: redash
# """
#     with open('docker-compose.yaml', 'w') as f:
#         f.write(docker_compose_content)

# def main():
#     create_docker_compose()
#     os.system('docker-compose up -d')

# if __name__ == "__main__":
#     main()
