# Jeu-du-president
Le jeu du président.

Il faut créer un dossier president_game et mettre tous les fichiers du repo dedans.

Il faut lancer etudes.py (cf son main).
On peut réaliser les études suivantes :
- avantage_president : vérifie que le président gagne plus de parties que les autres
- coherence_une_partie : vérifie le déroulement du'ne partie. En sortie, un CSV indique son déroulé
- variete_joueurs : vérifie le fonctionnement des players de base
- force_joueurs : compare la puissance de plusieurs joueurs


Pour ajouter un joueur:
Dans player.py, créer un nouveau player hérité de la classe Player et remplir les attributs et méthodes suivantes :
- name : nom du joueur (obligatoire)
- que_joueur : votre stratégie de jeu lorsque c'est votre tour. (obligatoire - le joueur de base ne joue rien)
- give_cards_prez_to_trou : qu'est-ce que vous donnez au trou si vous êtes président (facultatif)
- give_card_vice_prez_to_vice_trou : qu'est-ce que vous donnez au vice-trou si vous être vice-prez (facultatif)

