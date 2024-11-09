# Projet de calcul d'emission carbone selon le moyen de transport 

## Introduction

Cette API fournit diverses fonctionnalités pour aider à calculer le taux d'émission carbone pour un trajet en 
tenant compte des moyens de transport disponibles. Renvoie le moyen de transport le plus écologique et fait des recommandations.



## Guide de Déploiement sur un Serveur Ubuntu

Ce guide fournit des instructions étape par étape sur la manière de déployer l'application sur un serveur Ubuntu.

### Cloner le Projet

1. **Cloner le projet depuis GitLab :**
   ```bash
   git clone -b develop https://gitlab.com/digit-team/digit-ai-tripplanner.git
   cd digit-ai-tripplanner
   ```

### Configuration

1. **Générer une clé secrète pour `SECRET_KEY` :**
   Utilisez la commande suivante pour générer une clé secrète aléatoire sécurisée :

   ```bash
   openssl rand -hex 32
   ```

   Copiez la clé générée et remplacez la valeur de `SECRET_KEY` dans le fichier `.env`.

2. **Modifier les valeurs dans le fichier `.env`**

   - `OPENAI_API_KEY`: Clé d'API OpenAI.
   - `GOOGLE_MAPS_API_KEY`: Clé d'API Google maps
   - `GROQ_API_KEY`: Clé d'API Groq
   - `DEEPL_API_KEY`: Clé d'API Deepl
   - `SECRET_KEY`: clé secrete jwt
   - `ALGORITHM`: Algorithme de hachage.
   - `SHARED_PASSWORD`: Mot de passe partagé pour l'authentification. Vous pouvez le modifier à volonté.
   
### Déploiement avec Docker

1. **Construction de l'image Docker :**
   Utilisez la commande suivante pour construire l'image Docker :

   ```bash
   docker build -t trip .
   ```

2. **Exécution du conteneur Docker :**
   Une fois l'image construite, exécutez le conteneur Docker avec la commande suivante :

   ```bash
   docker run -d --restart=always --name carbone -p 8789:8080 trip
   ```

3. **Vérification des logs :**
   Pour consulter les logs du conteneur Docker en temps réel, utilisez la commande suivante :

   ```bash
   docker logs -f carbone
   ```

4. **Arrêt du conteneur :**
   Pour arrêter le conteneur Docker, utilisez la commande suivante :

   ```bash
   docker stop carbone
   ```

5. **Suppression des conteneurs arrêtés :**
   Pour nettoyer votre système des conteneurs Docker arrêtés, utilisez la commande suivante :
   ```bash
   docker rm $(docker ps -a -f status=exited -q)
   ```

Après avoir suivi ces étapes, l'application sera déployée et accessible à l'adresse `http://votre-serveur:8789`.

## Endpoint `/token`

### Méthode : POST

Ce point de terminaison est utilisé pour générer un jeton d'accès.

#### Entrée

- `password` (string): Mot de passe pour l'autorisation.

#### Sortie

- `access_token` (string): Jeton d'accès généré.
- `token_type` (string): Type de jeton.

---

## Endpoint `/calcul_emission`

### Méthode : POST

Ce point de terminaison est utilisé pour suggérer des activités pour un trajet donné.

#### Entrée

- `ville_depart` (string): Nom de la ville de départ
-`ville_arrivee` (string): Nom de la ville d'arrivée
- `langue` (string): Langue dans laquelle les activités doivent être suggérées. Langues possibles :
  - "FR" : Français
  - "ZH" : Chinois
  - "ES" : Espagnol
  - "RU" : Russe
  - "PT-PT" : Portugais (Portugal)
  - "DE" : Allemand
  - "EN-US" : Anglais

#### Sortie

-"meilleur_mode"(string): renvoie le moyen de  transport le plus écologique parmi les moyens disponibles.        
-"meilleur_emission" (string): renvoie l'émission carbone du moyen de  transport le plus écologique en KgCO2
-"valeurs" (dict): renvoie les moyens de transport disponibles et l'émission correspondante en KgCO2
-"details"(html): donne des détails sur les valeurs obtenus
-"recommandations" (html): fait des recommandations par rapport au meilleur moyen de transport

---

#### Réponse

```json
{
  "meilleur_mode": "avion",
  "meilleur_emission": "1224.394 kgCO2 ",
  "valeurs": {
    "avion": 1224.394
  },
  "details": "<body>\n    <br />La valeur donnée représente la quantité d'émissions de carbone associée au transport par avion. L'unité \"kgCO2\" signifie kilogramme de dioxyde de carbone, qui est une mesure universelle de l'empreinte carbone.\n   </p> <p>Dans ce cas précis, \"avion\" : 1224,394 signifie qu'un avion produit 1224,394 kilogrammes de dioxyde de carbone sous forme d'émissions. Ce chiffre pourrait être basé sur une distance particulière parcourue, ou une période spécifique, bien que le contexte n'ait pas fourni ce détail.</p> <p>L'avion : 1224,394 signifie qu'un avion produit 1224,394 kilogrammes de dioxyde de carbone en tant qu'émissions.\n    <Il convient de noter que l'aviation contribue de manière significative aux émissions de gaz à effet de serre, ce qui est un facteur important du réchauffement de la planète et du changement climatique. Le niveau élevé d'émissions des avions est dû à la forte consommation de combustibles fossiles pendant les vols.\n    <Toutefois, il s'agit d'une estimation générale. Les émissions réelles peuvent varier en fonction de facteurs tels que la marque et le modèle de l'avion, le degré de remplissage du vol, l'efficacité de l'avion, etc.\n</body>",
  "recommandations": "<html>\n  <body>\n    <h2>Réduire l'impact environnemental du voyage Cotonou-Paris</h2>\n    <p>L'empreinte carbone pour un voyage de Cotonou à Paris est de 1224,394 kgCO2 par avion.</p> <p>Pour réduire l'impact environnemental de ce voyage, envisagez les options suivantes :</p> <p>L'empreinte carbone pour un voyage de Cotonou à Paris est de 1224,394 kgCO2 par air.</p>\n    </p> <p>Pour réduire l'impact environnemental de ce voyage, envisagez les options suivantes :</p> <p>L'empreinte carbone d'un voyage de Cotonou à Paris est de 1224,394 kgCO2.\n    <ol>\n      <li><strong>Compensation carbone:</strong>Investissez dans des projets de compensation carbone tels que des initiatives de reforestation ou d'énergie renouvelable. Cela peut aider à compenser les émissions de carbone de votre vol.</li>\n      <li><strong>Modes de transport alternatifs:</strong> Même si cela n'est pas toujours possible, explorer des modes de transport alternatifs comme le train ou l'autobus permettrait de réduire considérablement l'empreinte carbone. Cependant, veuillez noter que ces options peuvent ne pas être disponibles ou pratiques pour cet itinéraire spécifique.</li>\n      <li><strong أكثر Efficient Aircraft:</strong> Si le voyage en avion est inévitable, envisagez de voler avec des compagnies aériennes qui utilisent des avions plus économes en carburant. Certaines compagnies aériennes investissent dans des avions plus récents et plus efficaces qui réduisent les émissions de carbone.</li>\n      <li><strong>Changements de comportement en matière de voyage:</strong> La réduction du nombre de vols effectués au cours d'une année, la combinaison de voyages ou l'allongement de la durée des voyages peuvent également contribuer à réduire l'empreinte carbone globale.</li>\n      <li><strong>Carburants d'aviation durables (SAF):</strong> Soutenir les compagnies aériennes qui utilisent des carburants d'aviation durables, qui peuvent réduire les émissions de gaz à effet de serre jusqu'à 80 %. Bien que leur adoption n'en soit qu'à ses débuts, les carburants durables peuvent avoir un impact significatif sur l'empreinte carbone de l'industrie aéronautique.</li>\n    </ol>\n    </p> <p>Bien que certaines de ces options ne soient pas facilement disponibles pour l'itinéraire Cotonou-Paris, elles peuvent néanmoins contribuer à réduire votre empreinte carbone globale à long terme.\n  </body>\n</html>"
}
```

#### Récupération des Valeurs

- **`status`**: Indique le statut de la requête. Récupérez cette valeur en accédant à `response.status`.

- **`activity_suggest`**:

  - **`images_5`**: Contient les 5 principales images associées à l'activité suggérée.
    - **`principales_images_of`**: Liste des URLs des images principales. Récupérez ces URLs en accédant à `response.activity_suggest.images_5.principales_images_of`.
  - **`activity_of_`**: Contient l'activité suggérée dans la langue spécifiée (par exemple, Russe).
    - **`RU`**: Contient le texte de l'activité suggérée en Russe. Récupérez ce texte en accédant à `response.activity_suggest.activity_of_.RU`.

- **`list_of_places`**: Contient une liste de lieux touristiques avec leurs coordonnées et URLs d'image associées.
  - Pour chaque lieu, vous pouvez récupérer les informations comme suit :
    - **`Latitude`**: Latitude du lieu. Accédez à cette valeur en utilisant `response.list_of_places[Nom_du_Lieu].Latitude`.
    - **`Longitude`**: Longitude du lieu. Accédez à cette valeur en utilisant `response.list_of_places[Nom_du_Lieu].Longitude`.
    - **`image_url`**: URL de l'image associée au lieu. Accédez à cette valeur en utilisant `response.list_of_places[Nom_du_Lieu].image_url`.

