# Quick Start Guide - FastAPI Legal Backend

Guida rapida per avviare l'applicazione con Docker e ngrok per esposizione pubblica.

## 🚀 Setup in 5 Minuti

### 1. Prerequisiti

- Docker Desktop installato
- Account ngrok gratuito

### 2. Ottieni il Token Ngrok

```bash
# Registrati su ngrok.com e ottieni il token
open https://dashboard.ngrok.com/get-started/your-authtoken
```

### 3. Configura l'Ambiente

```bash
# Copia il file di esempio
cp .env.example .env

# Modifica .env e aggiungi il tuo token ngrok
# NGROK_AUTHTOKEN=your_actual_token_here
```

### 4. Avvia i Servizi

```bash
# Build e avvia FastAPI + ngrok
docker-compose up -d --build

# Verifica che i servizi siano attivi
docker-compose ps
```

### 5. Ottieni l'URL Pubblico

```bash
# Apri la dashboard ngrok
open http://localhost:4040

# Oppure usa curl
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

Vedrai qualcosa come: `https://abc123-456-789.ngrok-free.app`

### 6. Aggiorna CORS

Aggiungi l'URL ngrok al file `.env`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://abc123-456-789.ngrok-free.app
```

Riavvia il servizio web:

```bash
docker-compose restart web
```

### 7. Testa l'API

```bash
# Test locale
curl http://localhost:8000/health

# Test pubblico (usa il tuo URL ngrok)
curl https://abc123-456-789.ngrok-free.app/health

# Apri la documentazione
open https://abc123-456-789.ngrok-free.app/docs
```

## 📊 Dashboard e Monitoring

- **API Docs**: https://your-ngrok-url.ngrok.io/docs
- **Ngrok Dashboard**: http://localhost:4040
- **Health Check**: https://your-ngrok-url.ngrok.io/health

## 🛠️ Comandi Utili

```bash
# Visualizza i log
docker-compose logs -f

# Ferma i servizi
docker-compose down

# Riavvia un servizio
docker-compose restart web

# Rebuild completo
docker-compose down && docker-compose up -d --build
```

## 🔧 Troubleshooting

### Problema: "Port 8000 already in use"

```bash
docker-compose down
# Oppure
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Problema: "Ngrok tunnel not starting"

1. Verifica il token in `.env`
2. Controlla i log: `docker-compose logs tunnel`
3. Riavvia: `docker-compose restart tunnel`

### Problema: "CORS error"

1. Verifica che l'URL ngrok sia in `CORS_ALLOWED_ORIGINS`
2. Riavvia: `docker-compose restart web`
3. Controlla i log: `docker-compose logs web`

## 📚 Documentazione Completa

- [Docker Setup](docs/DOCKER_SETUP.md) - Guida completa Docker
- [README](README.md) - Documentazione generale
- [API Docs](http://localhost:8000/docs) - Documentazione API interattiva

## 🎯 Uso con Google AI Studio

1. Avvia i servizi: `docker-compose up -d`
2. Ottieni l'URL ngrok dalla dashboard
3. Aggiungi l'URL a CORS e riavvia
4. Usa l'URL in Google AI Studio
5. Testa con: `https://your-ngrok-url/docs`

## 🔒 Note di Sicurezza

- ⚠️ Ngrok è per sviluppo/testing, non per produzione
- 🔐 Non committare il file `.env` con token reali
- 🚫 Non esporre dati sensibili tramite tunnel pubblici
- ✅ In produzione, usa un dominio reale con HTTPS

## 💡 Tips

- L'URL ngrok cambia ad ogni riavvio (piano gratuito)
- Usa `docker-compose logs -f` per debug in tempo reale
- La dashboard ngrok mostra tutte le richieste HTTP
- Puoi testare l'API direttamente dalla dashboard ngrok

## 🆘 Supporto

Se hai problemi:
1. Controlla i log: `docker-compose logs`
2. Verifica lo stato: `docker-compose ps`
3. Consulta [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)
4. Apri un issue su GitHub
