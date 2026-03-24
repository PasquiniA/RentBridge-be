# Migration Guide: From pyngrok to Docker Compose

Questa guida spiega le modifiche apportate al sistema di tunneling e come migrare.

## Cosa è Cambiato

### Prima (pyngrok integrato)

```python
# app/main.py
from app.utils.tunnel import tunnel_manager

# Tunnel avviato nel codice Python
if settings.enable_tunnel:
    tunnel_url = tunnel_manager.start_tunnel(...)
    
# CORS configurato dinamicamente
CORSConfig.configure_cors(app, ..., tunnel_url=tunnel_url)
```

**Problemi:**
- ❌ Bloccava il middleware FastAPI
- ❌ Errori SSL con certificati
- ❌ Logica infrastrutturale nel codice applicativo
- ❌ Difficile da debuggare

### Dopo (Docker Compose)

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports: ["8000:8000"]
  
  tunnel:
    image: ngrok/ngrok:latest
    command: ["http", "web:8000"]
```

**Vantaggi:**
- ✅ Separazione pulita app/infrastruttura
- ✅ Nessun problema SSL
- ✅ Dashboard ngrok integrata
- ✅ Facile da debuggare
- ✅ Production-ready

## Modifiche al Codice

### File Rimossi

```
app/utils/tunnel.py          ❌ Eliminato
tests/test_tunnel.py          ❌ Eliminato
docs/TUNNEL_SETUP.md          ❌ Obsoleto
docs/NGROK_SSL_FIX.md         ❌ Obsoleto
docs/ARCHITECTURE_NOTES.md    ❌ Obsoleto
```

### File Modificati

#### requirements.txt
```diff
- pyngrok==7.0.5
```

#### app/config.py
```diff
- enable_tunnel: bool = False
- ngrok_auth_token: Optional[str] = None
- tunnel_domain: Optional[str] = None
```

#### app/main.py
```diff
- from app.utils.tunnel import tunnel_manager
- tunnel_url = tunnel_manager.start_tunnel(...)
- CORSConfig.configure_cors(app, ..., tunnel_url=tunnel_url)
+ CORSConfig.configure_cors(app, ...)
```

#### app/middleware/cors.py
```diff
- def configure_cors(..., tunnel_url: str = None):
+ def configure_cors(...):
-     if tunnel_url:
-         origins.append(tunnel_url)
```

### File Aggiunti

```
Dockerfile                    ✅ Nuovo
docker-compose.yml            ✅ Nuovo
.dockerignore                 ✅ Nuovo
docs/DOCKER_SETUP.md          ✅ Nuovo
QUICKSTART.md                 ✅ Nuovo
```

## Come Migrare

### 1. Aggiorna il Codice

```bash
# Pull le ultime modifiche
git pull origin main

# Reinstalla le dipendenze (pyngrok rimosso)
pip install -r requirements.txt
```

### 2. Configura Docker

```bash
# Copia il file di esempio
cp .env.example .env

# Aggiungi il tuo token ngrok
# NGROK_AUTHTOKEN=your_token_here
```

### 3. Avvia con Docker

```bash
# Invece di: python -m app.main
docker-compose up -d --build
```

### 4. Ottieni l'URL Ngrok

```bash
# Apri la dashboard
open http://localhost:4040

# Oppure usa l'API
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

### 5. Aggiorna CORS

```env
# .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-ngrok-url.ngrok.io
```

```bash
# Riavvia il servizio web
docker-compose restart web
```

## Variabili d'Ambiente

### Rimosse

```env
ENABLE_TUNNEL=true           ❌ Non più necessaria
NGROK_AUTH_TOKEN=...         ❌ Rinominata
TUNNEL_DOMAIN=...            ❌ Non più necessaria
```

### Aggiunte/Modificate

```env
NGROK_AUTHTOKEN=...          ✅ Usata da docker-compose
CORS_ALLOWED_ORIGINS=...     ✅ Aggiungi manualmente l'URL ngrok
```

## Workflow di Sviluppo

### Prima

```bash
# 1. Configura .env
ENABLE_TUNNEL=true
NGROK_AUTH_TOKEN=...

# 2. Avvia app (tunnel si avvia automaticamente)
python -m app.main

# 3. Leggi l'URL dai log
# INFO - ✓ Public tunnel URL: https://...

# 4. CORS configurato automaticamente
```

### Dopo

```bash
# 1. Configura .env
NGROK_AUTHTOKEN=...

# 2. Avvia servizi
docker-compose up -d

# 3. Ottieni URL dalla dashboard
open http://localhost:4040

# 4. Aggiungi URL a CORS manualmente
# CORS_ALLOWED_ORIGINS=...,https://your-url.ngrok.io

# 5. Riavvia web
docker-compose restart web
```

## Comandi Equivalenti

| Prima | Dopo |
|-------|------|
| `python -m app.main` | `docker-compose up -d` |
| Leggi log per URL | `open http://localhost:4040` |
| CORS automatico | Aggiungi URL a `.env` manualmente |
| Ferma app | `docker-compose down` |
| Riavvia app | `docker-compose restart web` |

## Testing

### Prima

```bash
# Test con tunnel abilitato
ENABLE_TUNNEL=true pytest tests/

# Test senza tunnel
ENABLE_TUNNEL=false pytest tests/
```

### Dopo

```bash
# Test sempre senza tunnel (più semplice)
pytest tests/

# Tunnel è un servizio separato, non influenza i test
```

## Troubleshooting

### "Non vedo più l'URL del tunnel nei log"

✅ **Soluzione**: Apri la dashboard ngrok
```bash
open http://localhost:4040
```

### "CORS non funziona con ngrok"

✅ **Soluzione**: Aggiungi manualmente l'URL a `.env`
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-url.ngrok.io
```
Poi riavvia: `docker-compose restart web`

### "Voglio usare l'app senza Docker"

✅ **Soluzione**: Puoi ancora usare Python direttamente
```bash
# Avvia l'app
uvicorn app.main:app --reload

# In un altro terminale, avvia ngrok manualmente
ngrok http 8000
```

### "L'URL ngrok cambia sempre"

✅ **Normale**: Il piano gratuito genera URL casuali
✅ **Soluzione**: Usa un auth token per sessioni più stabili
✅ **Alternativa**: Piano a pagamento per domini fissi

## Vantaggi della Nuova Architettura

1. **Separazione delle Responsabilità**
   - App: Solo logica di business
   - Infrastruttura: Docker Compose

2. **Nessun Problema SSL**
   - Ngrok container gestisce tutto
   - Nessun errore di certificati

3. **Debugging Migliore**
   - Dashboard ngrok: http://localhost:4040
   - Vedi tutte le richieste in tempo reale
   - Replay delle richieste

4. **Production-Ready**
   - Dockerfile ottimizzato
   - Health checks integrati
   - Facile da deployare

5. **Flessibilità**
   - Cambia facilmente il tunnel provider
   - Aggiungi altri servizi (database, cache, etc.)
   - Scala facilmente

## Risorse

- [QUICKSTART.md](../QUICKSTART.md) - Setup rapido
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Guida completa Docker
- [README.md](../README.md) - Documentazione generale
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Ngrok Docs](https://ngrok.com/docs)
