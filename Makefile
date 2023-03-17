COMPOSE_FILE=./develop/docker-compose.yml
BUILD_NAME=netbox-plugins
PLUGINS_LIST=netbox_cmdb


cbuild:
	docker-compose -f ${COMPOSE_FILE} \
		-p ${BUILD_NAME} build

debug:
	@echo "Starting Netbox .. "
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up

start:
	@echo "Starting Netbox in detached mode.. "
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d

stop:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down

status:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} ps

logs:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} logs

logs-follow:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} logs -f

destroy:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down
	docker volume rm -f ${BUILD_NAME}_pgdata_netbox_plugins

nbshell:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py nbshell

shell:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py shell

adduser:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py createsuperuser

collectstatic:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py collectstatic

migrations:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d postgres
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} \
	run netbox python manage.py makemigrations
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down

test:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py test ${PLUGINS_LIST}

backupdb:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d postgres
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} exec postgres pg_dump --username netbox --host localhost netbox --file /tmp/backup.sql
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} cp postgres:/tmp/backup.sql ./db_backup.sql

restoredb: cleandb
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} cp ./db_backup.sql postgres:/tmp/backup.sql
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} exec postgres sh -c "psql --username netbox --host localhost netbox < /tmp/backup.sql >/dev/null"
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d

cleandb:
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d postgres
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} exec postgres dropdb --username netbox --host localhost netbox --if-exists
	docker-compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} exec postgres createdb --username netbox --host localhost netbox
