# Kafka Crypto Pairs Pipeline
## Требования

- **Docker**: Установленный Docker Desktop (Windows/Mac) или Docker на Linux.
- **Python**: Версия 3.10+
- Создать папку проекта и настроить для неё venv (автоматически в PyCharm)

## Установка и запуск

Следующие шаги настраивают Zookeeper, Kafka и Kafka UI для запуска в лкальной сети Docker

### 1. Создание Сети `kafka-network`
```bash
docker network create kafka-network
```

### 2. Запуск Zookeeper
```bash
docker run -d --name zookeeper --network kafka-network -p 2181:2181 zookeeper
```

### 3. Запуск Kafka
Используется два Listener - внешний и внутренний
```bash
docker run -d --name kafka --network kafka-network -p 9092:9092 -p 29092:29092 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:29092,PLAINTEXT_HOST://host.docker.internal:9092 -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT confluentinc/cp-kafka:latest
```

### 4. Создание топика для криптовалютных пар
Создаём топик для передачи данных о криптовалютных парах.

```bash
docker run --rm -it --network kafka-network confluentinc/cp-kafka:latest kafka-topics.sh --create --topic crypto-pairs --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
```
Может возникнуть ошибка, связанная с тем, что файл `kafka-topics.sh` не найден. В этом случае попробуйте прописать эту же команду, но уже без расширения - `kafka-topics`

### 5. Запуск kafka-UI (По желанию)
```bash
docker run -d --name kafka-ui --network kafka-network -p 8080:8080 -e KAFKA_CLUSTERS_0_NAME=local -e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=host.docker.internal:9092 provectuslabs/kafka-ui:latest
```
### Установка зависимостей для Python
```Bash
pip install -r requirements.txt
```
