# Webown - Central Scraping Application

Application Python centrale pour le scraping de sites web de recherche de logement.

## 🏗️ Architecture

L'application est construite avec :
- **Python 3.11** - Langage principal
- **PostgreSQL** - Base de données pour stocker les annonces
- **Redis** - Cache et gestion des queues (prévu pour futures fonctionnalités)
- **Docker Compose** - Orchestration des services
- **APScheduler** - Planification des tâches de scraping
- **BeautifulSoup4** - Parsing HTML
- **SQLAlchemy** - ORM pour la base de données

## 📋 Fonctionnalités

- ✅ Scraping modulaire pour plusieurs sources :
  - Leboncoin.fr
  - SeLoger.com
  - La Carte des Coloc
- ✅ Scheduler automatique pour récupérer les dernières annonces
- ✅ Base de données PostgreSQL pour la persistance
- ✅ Système de logging complet
- ✅ Gestion des doublons (basée sur source + source_id)
- ✅ Configuration via variables d'environnement

## 🚀 Installation et Démarrage

### Prérequis

- Docker et Docker Compose installés
- Git (optionnel)

### Démarrage rapide

1. **Cloner le projet** (si nécessaire)
```bash
git clone <repository-url>
cd webown
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env selon vos besoins
```

3. **Démarrer l'application**
```bash
docker-compose up -d
```

4. **Voir les logs**
```bash
docker-compose logs -f app
```

### Arrêter l'application

```bash
docker-compose down
```

Pour supprimer aussi les volumes (base de données) :
```bash
docker-compose down -v
```

## 📁 Structure du Projet

```
webown/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration de l'application
│   ├── database.py            # Connexion à la base de données
│   ├── models.py              # Modèles de données
│   ├── scheduler.py           # Gestionnaire de scheduler
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py            # Classe de base pour les scrapers
│   │   ├── leboncoin.py       # Scraper Leboncoin
│   │   ├── seloger.py         # Scraper SeLoger
│   │   ├── carte_coloc.py     # Scraper La Carte des Coloc
│   │   └── manager.py         # Gestionnaire des scrapers
│   └── services/
│       ├── __init__.py
│       └── listing_service.py # Service de gestion des annonces
├── logs/                      # Fichiers de logs
├── docker-compose.yml         # Configuration Docker Compose
├── Dockerfile                 # Image Docker de l'application
├── requirements.txt           # Dépendances Python
├── .env.example              # Exemple de configuration
└── main.py                   # Point d'entrée principal
```

## ⚙️ Configuration

Les paramètres sont configurés via le fichier `.env` :

### Base de données
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

### Redis
- `REDIS_HOST`, `REDIS_PORT`

### Scheduler
- `SCHEDULER_ENABLED` - Activer/désactiver le scheduler (true/false)
- `LEBONCOIN_INTERVAL_MINUTES` - Intervalle de scraping pour Leboncoin (en minutes)
- `SELOGER_INTERVAL_MINUTES` - Intervalle de scraping pour SeLoger
- `CARTE_COLOC_INTERVAL_MINUTES` - Intervalle de scraping pour La Carte des Coloc

### Scraping
- `USER_AGENT` - User-Agent pour les requêtes HTTP
- `REQUEST_TIMEOUT` - Timeout des requêtes (en secondes)
- `RETRY_ATTEMPTS` - Nombre de tentatives en cas d'échec

## 🔍 Utilisation

### Scraping manuel

Pour exécuter un scraping une seule fois sans scheduler :

```bash
docker-compose exec app python -c "from app.scheduler import ScrapingScheduler; s = ScrapingScheduler(); s.run_once()"
```

Pour un site spécifique :
```bash
docker-compose exec app python -c "from app.scheduler import ScrapingScheduler; s = ScrapingScheduler(); s.run_once('leboncoin')"
```

### Accéder à la base de données

```bash
docker-compose exec postgres psql -U webown -d webown
```

### Requêtes SQL utiles

```sql
-- Voir toutes les annonces
SELECT * FROM listings ORDER BY last_updated DESC LIMIT 10;

-- Compter les annonces par source
SELECT source, COUNT(*) FROM listings GROUP BY source;

-- Voir les annonces actives
SELECT * FROM listings WHERE is_active = true;

-- Voir les annonces d'une ville spécifique
SELECT * FROM listings WHERE city ILIKE '%Paris%';
```

## 🛠️ Développement

### Ajouter un nouveau scraper

1. Créer un nouveau fichier dans `app/scrapers/` (ex: `nouveau_site.py`)
2. Hériter de `BaseScraper` et implémenter les méthodes requises
3. Ajouter le scraper dans `ScraperManager` (`app/scrapers/manager.py`)
4. Ajouter un job dans le scheduler (`app/scheduler.py`)

Exemple :
```python
from app.scrapers.base import BaseScraper

class NouveauSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__("nouveau_site")
    
    def scrape_listings(self, search_params=None):
        # Implémenter le scraping
        pass
    
    def parse_listing(self, listing_data):
        # Implémenter le parsing
        pass
```

### Tests

Les tests peuvent être ajoutés dans un dossier `tests/` (à créer).

## 📝 Notes importantes

- Les sélecteurs CSS dans les scrapers peuvent nécessiter des ajustements si les sites web changent leur structure HTML
- Respectez les conditions d'utilisation des sites web scrapés
- Utilisez des intervalles raisonnables pour éviter de surcharger les serveurs
- Les logs sont sauvegardés dans `logs/` avec rotation quotidienne

## 🔒 Sécurité

- Ne commitez jamais le fichier `.env` avec des mots de passe réels
- Utilisez des mots de passe forts en production
- Configurez un firewall si nécessaire

## 📄 Licence

[À définir]

## 🤝 Contribution

[À définir]

