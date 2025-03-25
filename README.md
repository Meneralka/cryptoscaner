# Kafka Crypto Pairs Pipeline
## Требования

- **Docker**: Установленный Docker Desktop (Windows/Mac) или Docker на Linux.
- **Python**: Версия 3.7+ с установленными зависимостями (`aiohttp`, `confluent-kafka`, `sqlalchemy`, `asyncpg`).
- **Сеть Docker**: Сеть `kafka-network` (создаётся автоматически или уже существует).

## Установка и запуск

Следующие шаги настраивают Zookeeper, Kafka и Kafka UI в Docker, а также создают топик `crypto-pairs`.

### 1. Запуск Zookeeper

Zookeeper используется как координатор для Kafka.

```bash
docker run -d --name zookeeper --network kafka-network -p 2181:2181 zookeeper```
