# Docker Setup Guide

Questa guida spiega come eseguire l'applicazione FastAPI Legal Backend usando Docker e Docker Compose con ngrok per l'esposizione pubblica.

## Prerequisiti

- Docker Desktop installato ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose (incluso in Docker Desktop)
- Account ngrok (gratuito) per ottenere l'auth token

## Architettura

Il setup Docker include due servizi:

1. **web**: Il backend FastAPI che ascolta sulla porta 8000
2. **tunnel**: Ngrok che espone il servizio web pubblicamente

```
┌─────────────────────────────────────────┐
│         Docker Compose                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   web:8000   │◄───│    ngrok     │  │
│  │   FastAPI    │    │   tunnel     │  │
│  └──────────────┘    └──────┬───────┘  │
│                              │          │
└──────────────────────────────┼──────────┘
                               │
                               ▼
                    https://xxxxx.ngrok.io
                    (URL pubblico)
```

## Setup Rapido

### 1. Ottieni il Token Ngrok

1. Registrati su [ngrok.com](https://ngrok.com)
2. Vai alla dashboard: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copia il tuo auth token

### 2. Configura le Variabili d'Ambiente

Modifica il file `.env`:

```env
# Aggiungi il tuo token ngrok
NGROK_AUTHTOKEN=your_actual_token_here

# CORS - Aggiungerai l'URL ngrok dopo l'avvio
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Avvia i Servizi

```bash
# Build e avvia tutti i servizi
docker-compose up --build

# Oppure in background
docker-compose up -d --build
```

### 4. Ottieni l'URL Pubblico

Dopo l'avvio, ci sono due modi per ottenere l'URL pubblico di ngrok:

**Opzione A: Dashboard Ngrok (Raccomandato)**
```bash
# Apri nel browser
open http://localhost:4040
```

La dashboard mostra:
- URL pubblico (es. `https://abc123.ngrok.io`)
- Tutte le richieste in tempo reale
- Headers e body delle richieste

**Opzione B: API Ngrok**
```bash
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

### 5. Aggiorna CORS

Una volta ottenuto l'URL ngrok (es. `https://abc123.ngrok.io`), aggiungilo al file `.env`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://abc123.ngrok.io
```

Riavvia il servizio web:
```bash
docker-compose restart web
```

### 6. Testa l'API

```bash
# Test locale
curl http://localhost:8000/health

# Test pubblico (usa il tuo URL ngrok)
curl https://abc123.ngrok.io/health
```

## Comandi Utili

### Gestione Servizi

```bash
# Avvia i servizi
docker-compose up

# Avvia in background
docker-compose up -d

# Ferma i servizi
docker-compose down

# Riavvia un servizio specifico
docker-compose restart web
docker-compose restart tunnel

# Visualizza i log
docker-compose logs -f

# Log di un servizio specifico
docker-compose logs -f web
docker-compose logs -f tunnel
```

### Build e Pulizia

```bash
# Rebuild delle immagini
docker-compose build

# Rebuild forzato (no cache)
docker-compose build --no-cache

# Rimuovi tutto (servizi, volumi, network)
docker-compose down -v

# Rimuovi immagini non utilizzate
docker image prune -a
```

### Debug

```bash
# Entra nel container web
docker-compose exec web bash

# Verifica le variabili d'ambiente
docker-compose exec web env

# Verifica lo stato dei servizi
docker-compose ps

# Verifica i log in tempo reale
docker-compose logs -f --tail=100
```

## Accesso ai Servizi

Una volta avviati i servizi:

| Servizio | URL Locale | URL Pubblico |
|----------|------------|--------------|
| API | http://localhost:8000 | https://xxxxx.ngrok.io |
| Health Check | http://localhost:8000/health | https://xxxxx.ngrok.io/health |
| API Docs | http://localhost:8000/docs | https://xxxxx.ngrok.io/docs |
| ReDoc | http://localhost:8000/redoc | https://xxxxx.ngrok.io/redoc |
| Ngrok Dashboard | http://localhost:4040 | - |

## Configurazione Avanzata

### Custom Domain (Piano Ngrok a Pagamento)

Se hai un dominio personalizzato ngrok:

```yaml
# docker-compose.yml
tunnel:
  image: ngrok/ngrok:latest
  command:
    - "http"
    - "web:8000"
    - "--domain=your-custom-domain.ngrok.app"
```

### Variabili d'Ambiente Aggiuntive

Puoi passare variabili d'ambiente aggiuntive al servizio web:

```yaml
# docker-compose.yml
web:
  environment:
    - DEBUG=true
    - LOG_LEVEL=DEBUG
```

### Volume per Sviluppo

Per lo sviluppo locale con hot-reload:

```yaml
# docker-compose.yml
web:
  volumes:
    - .:/app
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

### Problema: "Port 8000 already in use"

```bash
# Trova il processo che usa la porta
lsof -i :8000

# Oppure ferma tutti i container
docker-compose down
```

### Problema: "Ngrok tunnel not starting"

1. Verifica che il token sia corretto nel `.env`
2. Controlla i log: `docker-compose logs tunnel`
3. Verifica che il servizio web sia avviato: `docker-compose ps`

### Problema: "CORS error"

1. Verifica che l'URL ngrok sia in `CORS_ALLOWED_ORIGINS`
2. Riavvia il servizio web: `docker-compose restart web`
3. Controlla i log: `docker-compose logs web`

### Problema: "Container keeps restarting"

```bash
# Verifica lo stato
docker-compose ps

# Controlla i log per errori
docker-compose logs web

# Verifica l'health check
docker-compose exec web curl http://localhost:8000/health
```

## Produzione

Per il deployment in produzione:

1. **Non usare ngrok** - Usa un dominio reale con HTTPS
2. **Rimuovi il volume di sviluppo** dal docker-compose.yml
3. **Usa variabili d'ambiente sicure** (non committare `.env`)
4. **Configura un reverse proxy** (nginx, traefik)
5. **Abilita HTTPS** con Let's Encrypt
6. **Usa un orchestratore** (Kubernetes, Docker Swarm)

## Integrazione con Google AI Studio

Per usare l'API con Google AI Studio:

1. Avvia i servizi: `docker-compose up -d`
2. Ottieni l'URL ngrok dalla dashboard: http://localhost:4040
3. Aggiungi l'URL a CORS e riavvia: `docker-compose restart web`
4. Usa l'URL ngrok in Google AI Studio
5. Testa con: `https://your-ngrok-url.ngrok.io/docs`

## Risorse

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
