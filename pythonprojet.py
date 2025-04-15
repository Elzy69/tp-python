import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ====================
# 1. CRÉATION BDD & INSERTION
# ====================
conn = sqlite3.connect('ventes_magasin.db')
cursor = conn.cursor()



cursor.execute('''
CREATE TABLE IF NOT EXISTS Produits (
    id_produit INTEGER PRIMARY KEY,
    nom_produit TEXT,
    categorie TEXT,
    prix_unitaire REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Clients (
    id_client INTEGER PRIMARY KEY,
    nom_client TEXT,
    email TEXT,
    ville TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Ventes (
    id_vente INTEGER PRIMARY KEY,
    id_produit INTEGER,
    id_client INTEGER,
    date_vente TEXT,
    quantite INTEGER,
    montant_total REAL,
    FOREIGN KEY(id_produit) REFERENCES Produits(id_produit),
    FOREIGN KEY(id_client) REFERENCES Clients(id_client)
)
''')

# Produits
produits = [
    ("Pain complet", "Boulangerie", 1.5),
    ("Beurre", "Crèmerie", 2.3),
    ("Savon liquide", "Hygiène", 3.2),
    ("Dentifrice", "Hygiène", 2.8),
    ("Jus d’orange", "Boissons", 2.5),
    ("Eau minérale 1.5L", "Boissons", 0.9),
    ("Pâtes", "Épicerie", 1.1),
    ("Huile végétale", "Épicerie", 4.5),
    ("Thé vert", "Boissons", 1.9),
    ("Chocolat noir", "Confiserie", 2.7)
]
cursor.executemany("INSERT INTO Produits (nom_produit, categorie, prix_unitaire) VALUES (?, ?, ?)", produits)

# Clients
clients = [
    ("Abalo Kodjo", "abalo.kodjo@example.com", "Lomé"),
    ("Yao Akossiwa", "yao.akossiwa@example.com", "Kpalimé"),
    ("Tchalla Kossi", "tchalla.kossi@example.com", "Kara"),
    ("Mensah Ama", "mensah.ama@example.com", "Atakpamé"),
    ("Segnon Paul", "segnon.paul@example.com", "Sokodé"),
    ("Adjovi Claire", "adjovi.claire@example.com", "Dapaong"),
    ("Kouassi Jules", "kouassi.jules@example.com", "Aného")
]
cursor.executemany("INSERT INTO Clients (nom_client, email, ville) VALUES (?, ?, ?)", clients)

# Ventes
produit_ids = list(range(1, len(produits) + 1))
client_ids = list(range(1, len(clients) + 1))

for _ in range(100):
    prod_id = random.choice(produit_ids)
    client_id = random.choice(client_ids)
    date_vente = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 120))
    date_str = date_vente.strftime('%Y-%m-%d')
    quantite = random.randint(1, 6)
    cursor.execute("SELECT prix_unitaire FROM Produits WHERE id_produit = ?", (prod_id,))
    prix_unitaire = cursor.fetchone()[0]
    montant_total = round(prix_unitaire * quantite, 2)
    cursor.execute('''
        INSERT INTO Ventes (id_produit, id_client, date_vente, quantite, montant_total)
        VALUES (?, ?, ?, ?, ?)
    ''', (prod_id, client_id, date_str, quantite, montant_total))

conn.commit()
 
# ====================
# 2. EXTRACTION AVEC PANDAS
# ====================
ventes_df = pd.read_sql_query('''
    SELECT V.id_vente, V.date_vente, V.quantite, V.montant_total,
           P.nom_produit, P.categorie, C.nom_client, C.ville
    FROM Ventes V
    JOIN Produits P ON V.id_produit = P.id_produit
    JOIN Clients C ON V.id_client = C.id_client
''', conn)

conn.close()

# ====================
# 3. ANALYSES STATISTIQUES
# ====================
ventes_df['date_vente'] = pd.to_datetime(ventes_df['date_vente'])
ventes_df['mois'] = ventes_df['date_vente'].dt.to_period('M').astype(str)

ca_par_mois = ventes_df.groupby('mois')['montant_total'].sum().reset_index()
top_produits = ventes_df.groupby('nom_produit')['quantite'].sum().sort_values(ascending=False).head(5)
top_clients = ventes_df.groupby('nom_client')['montant_total'].sum().sort_values(ascending=False).head(5)

# ====================
# 4. VISUALISATIONS MODIFIÉES
# ====================
sns.set(style="whitegrid")

# ➤ 1. Courbe du CA par mois
plt.figure(figsize=(12, 6))
sns.lineplot(x="mois", y="montant_total", data=ca_par_mois, marker='o',
             color='royalblue', linewidth=2.5)
plt.title("Évolution du chiffre d’affaires par mois", fontsize=16)
plt.xlabel("Mois", fontsize=14)
plt.ylabel("CA (€)", fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()

# ➤ 2. Barres horizontales : Top 5 produits
plt.figure(figsize=(12, 6))
top_produits = top_produits.sort_values()
top_produits.plot(kind='barh', color='seagreen', edgecolor='black')
plt.title("Top 5 des produits les plus vendus (quantité)", fontsize=16)
plt.xlabel("Quantité vendue", fontsize=14)
plt.ylabel("Produit", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()

# ➤ 3. Camembert : Top 5 clients
plt.figure(figsize=(8, 8))
plt.pie(top_clients, labels=top_clients.index, autopct='%1.1f%%',
        startangle=140, colors=sns.color_palette("Oranges", len(top_clients)))
plt.title("Répartition du chiffre d’affaires par les top 5 clients", fontsize=16)
plt.axis('equal')  # Cercle parfait
plt.tight_layout()
plt.show()

