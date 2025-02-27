import operator
from random import shuffle
from copy import deepcopy, copy


from president_game.player import Player, DumbPlayer
from president_game.utils import (
    show_pretty_pose,
    show_pretty_hand,
)


class Partie:
    # Common elements for a whole game
    nb_joueurs: int
    highest_card: int
    lowest_card: int
    players: list[Player]
    save_events: bool

    # Common elements before the start of a round
    cards_shuffled: list[int] | None = None
    initial_cards_players: list[list[int]] | None = None
    role_players: list[str] | None = None

    # Variables varying thoughout a round
    current_cards_players: list[list[int]] | None = None
    counter_same_card: int = 0
    current_card_over: int | None = None
    is_revolution: bool = False
    risque_saut: bool = False

    # Elements of output summarizing the game
    classement: list[int] | None = None
    historique_jeux: list[list[list[int]]] = None
    all_events: list[str] = []

    def __init__(
        self,
        nb_joueurs=4,
        highest_card=13,
        players=None,
        role_players=None,
        cards_shuffled=None,
        save_events=True,
    ):
        self.nb_joueurs = nb_joueurs
        self.save_events = save_events
        self.highest_card = highest_card
        self.lowest_card = 0
        if players is None:
            self.players = [DumbPlayer() for _ in range(nb_joueurs)]
        else:
            self.players = players

        if role_players is None:
            if self.nb_joueurs >= 4:
                self.role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez"] + [
                    "Neutre" for _ in range(0, self.nb_joueurs - 4)
                ]
            else:
                self.role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez"][
                    : self.nb_joueurs
                ]
        else:
            self.role_players = role_players
        if cards_shuffled:
            self.cards_shuffled = cards_shuffled
        else:
            self.shuffle()
        self.distribute_cards()
        self.exchange_cards_classic()

    @property
    def all_cards(self):
        return [valeur for valeur in range(0, self.highest_card) for _ in range(4)]

    def shuffle(self):
        self.cards_shuffled = copy(self.all_cards)
        shuffle(self.cards_shuffled)

    def distribute_cards(self):
        self.initial_cards_players = []
        for i in range(self.nb_joueurs):
            cartes_distrib = sorted(
                self.cards_shuffled[
                    i * len(self.all_cards) // self.nb_joueurs : (i + 1)
                    * len(self.all_cards)
                    // self.nb_joueurs
                ]
            )
            self.initial_cards_players.append(cartes_distrib)
            self.players[i].donner_main(cartes_distrib)
        self.current_cards_players = deepcopy(self.initial_cards_players)
        self.pretty_jeu()

    def pretty_jeu(self, init_str="Jeu initial: "):
        if not self.save_events:
            return
        events = [init_str]
        for i in range(self.nb_joueurs):
            events.append(f"{self.role_players[i]}: {self.show_pretty_hand(i)} ")
        events.append("\n")
        self.all_events += events

    def show_pretty_hand(self, index_player) -> str:
        return show_pretty_hand(self.current_cards_players[index_player])
        # return "".join([mapping_cards_real_game(el) for el in )

    def exchange_cards_classic(self):
        if {"Trou", "Prez", "Vice-Trou", "Vice-Prez"}.issubset(set(self.role_players)):
            self.exchange_cards(
                self.role_players.index("Trou"), self.role_players.index("Prez"), 2
            )
            self.exchange_cards(
                self.role_players.index("Vice-Trou"),
                self.role_players.index("Vice-Prez"),
                1,
            )
            self.pretty_jeu("Jeu après échange: ")
        elif len({"Trou", "Prez", "Vice-Trou", "Vice_Prez"} & set(self.role_players)):
            raise ValueError(f"Ces rôles : {self.role_players} sont illogiques")

    def exchange_cards(self, joueur_inferieur, joueur_superieur, nb_cards_to_exchange):
        # Le joueur inférieur donne ses meilleures cartes au joueur supérieur
        main_joueur_inferieur = copy(self.current_cards_players[joueur_inferieur])
        main_joueur_superieur = copy(self.current_cards_players[joueur_superieur])
        self.current_cards_players[joueur_inferieur] = main_joueur_inferieur[
            :-nb_cards_to_exchange
        ]
        self.current_cards_players[joueur_superieur] = sorted(
            main_joueur_superieur + main_joueur_inferieur[-nb_cards_to_exchange:]
        )

        # Cartes avant échange
        main_joueur_inferieur = copy(self.current_cards_players[joueur_inferieur])
        main_joueur_superieur = copy(self.current_cards_players[joueur_superieur])

        if nb_cards_to_exchange == 1:
            # Le Vice Prez choisit sa carte
            card = self.players[joueur_superieur].give_card_vice_prez_to_vice_trou(
                main_joueur_superieur
            )
            if card not in self.current_cards_players[joueur_superieur]:
                raise ValueError(
                    "{self.players[joueur_superieur].get_name()}, vice-prez, a tenté de donner une carte qu'il n'a pas"
                )
            main_joueur_superieur.remove(card)
            self.current_cards_players[joueur_superieur] = main_joueur_superieur
            self.current_cards_players[joueur_inferieur] = sorted(
                main_joueur_inferieur + [card]
            )
        else:
            # Le Prez chosit sa carte
            cards = self.players[joueur_superieur].give_cards_prez_to_trou(
                main_joueur_superieur
            )
            if not set(cards).issubset(self.current_cards_players[joueur_superieur]):
                raise ValueError(
                    f"{self.players[joueur_superieur].get_name()}, prez, a tenté de donner des cartes qu'il n'a pas"
                )
            for card in cards:
                main_joueur_superieur.remove(card)
            self.current_cards_players[joueur_superieur] = main_joueur_superieur
            self.current_cards_players[joueur_inferieur] = sorted(
                main_joueur_inferieur + cards
            )

    def update_according_to_pose(
        self,
        events_actuel,
        pose,
        cartes_joueurs,
        joueur_actuel,
        joueurs_pas_fini,
        joueurs_en_jeu,
        classement,
        cartes_plateau,
    ):
        if len(cartes_plateau):
            cartes_au_dessus = cartes_plateau[-1]
        else:
            cartes_au_dessus = None
        events_actuel.append(f"Joue {show_pretty_pose(pose)} ")
        conditions_triche = [
            (not all(el == pose[0] for el in pose)),
            (
                cartes_au_dessus is not None
                and operator.lt(pose[0], cartes_au_dessus[0])
            ),
            self.risque_saut and pose != cartes_au_dessus,
            not set(pose).issubset(cartes_joueurs[joueur_actuel]),
        ]
        if any(conditions_triche):
            # Mettre trou le tricheur
            raise ValueError(f"Le joueur {self.players[joueur_actuel]} a triché ! ")
        if pose == cartes_au_dessus:
            self.counter_same_card += len(pose)
            self.risque_saut = True
        else:
            self.counter_same_card = len(pose)
            self.risque_saut = False
        for el in pose:
            cartes_joueurs[joueur_actuel].remove(el)

        if not cartes_joueurs[joueur_actuel]:
            events_actuel.append(f"{self.role_players[joueur_actuel]} a fini ")
            joueurs_pas_fini.remove(joueur_actuel)
            joueurs_en_jeu.remove(joueur_actuel)
            classement.append(joueur_actuel)
        cartes_plateau.append(pose)
        cartes_au_dessus = pose

        # Si les 4 dernières cartes du plateau sont identiques, le joueur a la main
        if self.counter_same_card == 4:
            self.risque_saut = False
            # events_actuel.append(f"\n Coupe de {self.role_players[joueur_actuel]} !! ")
            events_actuel.append("Coupe !")
            joueurs_en_jeu = [joueur_actuel]

        # Si le jour a joué un 2, il a la main
        if pose[0] == self.highest_card - 1:
            # events_actuel.append(f"{self.role_players[joueur_actuel]} prend la main ")
            joueurs_en_jeu = [joueur_actuel]

        # Révolution si 4 cartes identiques sont posées d'un coup
        if len(pose) == 4:
            events_actuel.append(f"\n Révolution de {pose[0]} !! \n")
            self.risque_saut = False
            raise NotImplementedError("La révolution n'a pas encore été implémentée !!")

        return cartes_au_dessus, joueurs_en_jeu

    def play_whole_game_from_cards(self):
        cartes_joueurs = self.current_cards_players
        nb_joueurs = self.nb_joueurs
        cartes_deja_jouees = []
        classement = []
        historique_jeux = []
        cartes_plateau = []
        joueurs_en_jeu = [i for i in range(nb_joueurs)]
        joueur_actuel = 0
        joueurs_pas_fini = [i for i in range(nb_joueurs)]

        for i, player in enumerate(self.players):
            player.donner_main(self.current_cards_players[i])

        events_actuel = []
        while len(classement) < nb_joueurs - 1:
            prochain_joueur = joueurs_en_jeu[
                (joueurs_en_jeu.index(joueur_actuel) + 1) % len(joueurs_en_jeu)
            ]
            events_actuel.append(
                f"{self.role_players[joueur_actuel]} "
                f"{self.show_pretty_hand(joueur_actuel)} "
            )

            pose = self.players[joueur_actuel].que_jouer(
                copy(cartes_joueurs[joueur_actuel]),
                copy(cartes_plateau),
                self.risque_saut,
                copy(cartes_deja_jouees),
            )

            if pose is not None:
                cartes_au_dessus, joueurs_en_jeu = self.update_according_to_pose(
                    events_actuel,
                    pose,
                    cartes_joueurs,
                    joueur_actuel,
                    joueurs_pas_fini,
                    joueurs_en_jeu,
                    classement,
                    cartes_plateau,
                )
                cartes_deja_jouees = sorted(cartes_deja_jouees + pose)
            else:
                if self.risque_saut:
                    events_actuel.append("est sauté")
                    self.risque_saut = False
                else:
                    events_actuel.append("Passe ")
                    joueurs_en_jeu.remove(joueur_actuel)

            if len(joueurs_en_jeu) == 1:
                self.risque_saut = False
                if joueurs_en_jeu[0] not in joueurs_pas_fini:
                    joueurs_en_jeu = [prochain_joueur]
                events_actuel.append(
                    f"{self.role_players[joueurs_en_jeu[0]]} a la main"
                )
                historique_jeux.append(copy(cartes_plateau))
                cartes_plateau = []
                self.counter_same_card = 0
                prochain_joueur = joueurs_en_jeu[0]
                joueurs_en_jeu = copy(joueurs_pas_fini)

            joueur_actuel = prochain_joueur
            events_actuel.append("\n")

        # Ajout du joueur arrivé en dernier
        classement = classement + [
            ({i for i in range(nb_joueurs)} - set(classement)).pop()
        ]

        events_actuel.append(
            "Classement final: " + " ".join([self.role_players[i] for i in classement])
        )

        self.classement = classement
        self.historique_jeux = historique_jeux
        self.all_events += events_actuel
        self.cartes_deja_jouees = cartes_deja_jouees

    def show_game(self):
        print("".join([el for el in self.all_events]))
