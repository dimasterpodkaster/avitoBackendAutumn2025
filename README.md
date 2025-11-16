# avitoBackendAutumn2025
Сервис назначения ревьюеров для Pull Request’ов

# README

## Запуск проекта

### Требования
- Docker
- Docker Compose
- Make

### Сборка контейнеров
```bash
make build
```

### Запуск сервиса
```bash
make up
```

Приложение будет доступно на:
```
http://localhost:8080
```

### Остановка контейнеров
```bash
make down
```

### Просмотр логов
```bash
make logs
```

### Запуск тестов
```bash
make test
```

### Консоль внутри контейнера
```bash
make sh
```
