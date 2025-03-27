import logging
import operator
from random import shuffle
from copy import deepcopy, copy
import concurrent.futures

import pandas as pd

from president_game.player import Player, DumbPlayer
from president_game.utils import (
    show_pretty_pose, show_super_pretty_hand, pretty_actions_jouees,
)
logger = logging.getLogger(__name__)

class Partie:
    # Common elements for a whole game
    nb_joueurs: int
    nb_rangs_cartes: int
    lowest_card: int
    players: list[Player]
    save_events: bool
    timeout_players: int

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
        nb_rangs_cartes=13,
        players=None,
        role_players=None,
        cards_shuffled=None,
        save_events=True,
        timeout_players=3
    ):
        self.nb_joueurs = nb_joueurs
        self.timeout_players = timeout_players
        self.save_events = save_events
        self.nb_rangs_cartes = nb_rangs_cartes
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

        self.indexed_name_players = [f"{i}_{player.get_name()}" for i, player in enumerate(players)]

        if cards_shuffled:
            self.cards_shuffled = cards_shuffled
        else:
            self.shuffle()
        self.distribute_cards()
        self.exchange_cards_classic()

    @property
    def all_cards(self):
        return [valeur for valeur in range(0, self.nb_rangs_cartes) for _ in range(4)]

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
        self.pretty_jeu(self.indexed_name_players)

    def pretty_jeu(self, name_players, init_str="Jeu initial: "):
        if not self.save_events:
            return
        events = [init_str]
        for i in range(self.nb_joueurs):
            events.append(f"{name_players[i]} ({self.role_players[i]}): {self.show_pretty_hand(i)} ")
        logger.info(" ".join(events))

    def show_pretty_hand(self, index_player) -> str:
        return show_super_pretty_hand(self.current_cards_players[index_player])
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
                    f"{self.players[joueur_superieur].get_name()}, vice-prez, a tenté de donner une carte "
                    f"qu'il n'a pas"
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
                    f"{self.players[joueur_superieur].get_name()}, prez, a tenté de donner des cartes "
                    f"qu'il n'a pas"
                )
            for card in cards:
                main_joueur_superieur.remove(card)
            self.current_cards_players[joueur_superieur] = main_joueur_superieur
            self.current_cards_players[joueur_inferieur] = sorted(
                main_joueur_inferieur + cards
            )

    def update_according_to_pose(
        self,
        pose,
        cartes_joueurs,
        joueur_actuel,
        joueurs_pas_fini,
        joueurs_en_jeu,
        classement,
        cartes_plateau
    ):
        if len(cartes_plateau):
            cartes_au_dessus = cartes_plateau[-1]
        else:
            cartes_au_dessus = None

        logger.info(f"{self.indexed_name_players[joueur_actuel]} avec la main "
                    f"{self.show_pretty_hand(joueur_actuel)} "
                    f"joue {show_pretty_pose(pose)} ")
        if pose == cartes_au_dessus:
            self.counter_same_card += len(pose)
            self.risque_saut = True
        else:
            self.counter_same_card = len(pose)
            self.risque_saut = False
        for el in pose:
            cartes_joueurs[joueur_actuel].remove(el)

        if not cartes_joueurs[joueur_actuel]:
            logger.info(f"{self.indexed_name_players[joueur_actuel]} a fini ")
            joueurs_pas_fini.remove(joueur_actuel)
            joueurs_en_jeu.remove(joueur_actuel)
            classement.append(joueur_actuel)
        cartes_plateau.append(pose)
        cartes_au_dessus = pose

        # Si les 4 dernières cartes du plateau sont identiques, le joueur a la main
        if self.counter_same_card == 4:
            self.risque_saut = False
            logger.info("Coupe !")
            joueurs_en_jeu = [joueur_actuel]

        # Si le jour a joué un 2, il a la main
        if pose[0] == self.nb_rangs_cartes - 1:
            # logger.info(f"{self.role_players[joueur_actuel]} prend la main ")
            joueurs_en_jeu = [joueur_actuel]

        # Révolution si 4 cartes identiques sont posées d'un coup
        if len(pose) == 4:
            logger.info(f"Révolution de {pose[0]} !!")
            self.risque_saut = False
            raise NotImplementedError("La révolution n'a pas encore été implémentée !!")

        return cartes_au_dessus, joueurs_en_jeu

    def dumb_play(self, cartes_joueur: list[int], cartes_plateau: list[list[int]]) -> list[int]:
        """
        Si vous ne voulez pas jouer, on joue à votre place rien, et une carte aléatoire si vous avez la main
        """
        if cartes_plateau:
            return []
        return [cartes_joueur[-1]]

    def convert_pretty_play_to_df(self):
        return

    def play_whole_game_from_cards(self):
        cartes_joueurs = self.current_cards_players
        nb_joueurs = self.nb_joueurs
        cartes_deja_jouees = []
        classement = []
        liste_tricheurs = []
        historique_jeux = []
        cartes_plateau = []
        joueurs_en_jeu = [i for i in range(nb_joueurs)]
        joueur_actuel = 0
        joueurs_pas_fini = [i for i in range(nb_joueurs)]
        total_pretty_play_joueurs = {i: [] for i in range(len(self.players))}

        for i, player in enumerate(self.players):
            player.donner_main(copy(self.current_cards_players[i]))

        events_actuel = []
        pretty_play_joueurs = {i: [] for i in range(len(self.players))}
        while len(classement + liste_tricheurs) < nb_joueurs - 1:
            prochain_joueur = joueurs_en_jeu[
                (joueurs_en_jeu.index(joueur_actuel) + 1) % len(joueurs_en_jeu)
            ]
            flag_triche = False
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    future = executor.submit(self.players[joueur_actuel].que_jouer,
                                           copy(cartes_joueurs[joueur_actuel]),
                                           copy(cartes_plateau),
                                           self.risque_saut,
                                           copy(cartes_deja_jouees)
                                           )
                    pose = future.result(timeout=self.timeout_players)
                except concurrent.futures.TimeoutError:
                    logger.error(f"Le code de {self.indexed_name_players[joueur_actuel]} a pris plus de "
                                 f"{self.timeout_players} secondes : "
                                 f"on joue à sa place")
                    pose = self.dumb_play(cartes_joueurs[joueur_actuel], cartes_plateau)

                except Exception:
                    logger.error(f"Le code de {self.indexed_name_players[joueur_actuel]} est beugué : "
                                 f"on jour à sa place",
                                 exc_info=True)
                    pose = self.dumb_play(cartes_joueurs[joueur_actuel], cartes_plateau)
                    # joueurs_pas_fini.remove(joueur_actuel)
                    # joueurs_en_jeu.remove(joueur_actuel)
                    # liste_tricheurs.append(joueur_actuel)
                else:
                    if not isinstance(pose, list) or not all(isinstance(x, int) for x in pose):
                        logger.error(f"Le joueur {self.indexed_name_players[joueur_actuel]} n'a pas renvoyé "
                                     f"le bon format: {str(pose)} : on joue à sa place")
                        pose = self.dumb_play(cartes_joueurs[joueur_actuel], cartes_plateau)
                        # joueurs_pas_fini.remove(joueur_actuel)
                        # joueurs_en_jeu.remove(joueur_actuel)
                        # liste_tricheurs.append(joueur_actuel)

            if not flag_triche:
                if pose:
                    # Le joueur a tenté de jouer une carte
                    if cartes_plateau:
                        cartes_au_dessus = cartes_plateau[-1]
                    else:
                        cartes_au_dessus = None

                    conditions_triche = [
                        (not all(el == pose[0] for el in pose)),
                        (
                                cartes_au_dessus is not None
                                and operator.lt(pose[0], cartes_au_dessus[0])
                        ),
                        self.risque_saut and pose != cartes_au_dessus,
                        not set(pose).issubset(cartes_joueurs[joueur_actuel])
                    ]
                    if any(conditions_triche):
                        # Mettre à trou le tricheur
                        logger.error(f"Le joueur {self.indexed_name_players[joueur_actuel]} "
                                     f"avec la main {self.show_pretty_hand(joueur_actuel)}"
                                     f" a essayé de jouer {show_super_pretty_hand(pose)}, "
                                     f"il triche ! ")
                        joueurs_pas_fini.remove(joueur_actuel)
                        joueurs_en_jeu.remove(joueur_actuel)
                        liste_tricheurs.append(joueur_actuel)
                        pretty_play_joueurs[joueur_actuel].append(["T"])
                    else:
                        # Ok, le joueur respecte les règles
                        pretty_play_joueurs[joueur_actuel].append([str(el) for el in pose])
                        cartes_au_dessus, joueurs_en_jeu = self.update_according_to_pose(
                            pose,
                            cartes_joueurs,
                            joueur_actuel,
                            joueurs_pas_fini,
                            joueurs_en_jeu,
                            classement,
                            cartes_plateau
                        )
                        cartes_deja_jouees = sorted(cartes_deja_jouees + pose)
                else:
                    if not cartes_plateau:
                        logger.error(f"Le joueur : {self.indexed_name_players[joueur_actuel]} a la main "
                                     f"mais ne joue pas : il va en dernier et le jeu continue")
                        joueurs_pas_fini.remove(joueur_actuel)
                        joueurs_en_jeu.remove(joueur_actuel)
                        liste_tricheurs.append(joueur_actuel)
                        pretty_play_joueurs[joueur_actuel].append(["T"])
                    if self.risque_saut:
                        logger.info(f"Le joueur : {self.indexed_name_players[joueur_actuel]} est sauté")
                        self.risque_saut = False
                        pretty_play_joueurs[joueur_actuel].append(["S"])
                    else:
                        logger.info(f"Le joueur : {self.indexed_name_players[joueur_actuel]} passe")
                        joueurs_en_jeu.remove(joueur_actuel)
                        pretty_play_joueurs[joueur_actuel].append(["P"])

            if len(joueurs_en_jeu) == 1:
                self.risque_saut = False
                if joueurs_en_jeu[0] not in joueurs_pas_fini:
                    joueurs_en_jeu = [prochain_joueur]
                logger.info(
                    f"{self.indexed_name_players[joueurs_en_jeu[0]]} a la main"
                )
                total_pretty_play_joueurs, pretty_play_joueurs = self.reset_pretty_play_joueurs(
                    total_pretty_play_joueurs, pretty_play_joueurs, joueurs_pas_fini
                )
                historique_jeux.append(copy(cartes_plateau))
                cartes_plateau = []
                self.counter_same_card = 0
                prochain_joueur = joueurs_en_jeu[0]
                joueurs_en_jeu = copy(joueurs_pas_fini)

            elif prochain_joueur < joueur_actuel:
                # On revient au début de l'indexation des joueurs
                total_pretty_play_joueurs, pretty_play_joueurs = self.reset_pretty_play_joueurs(
                    total_pretty_play_joueurs, pretty_play_joueurs, joueurs_pas_fini
                )
            joueur_actuel = prochain_joueur
            flag_triche = False

        df_pretty_play_joueurs = pd.DataFrame(total_pretty_play_joueurs)
        df_pretty_play_joueurs.to_csv("resume_partie.csv")
        logger.info(str(df_pretty_play_joueurs))

        # Ajout du joueur arrivé en dernier
        classement = classement + [
            ({i for i in range(nb_joueurs)} - set(liste_tricheurs) - set(classement)).pop()
        ] + liste_tricheurs

        logger.info(
            "Classement final: " + " ".join([self.indexed_name_players[i] for i in classement])
        )

        self.classement = classement
        self.historique_jeux = historique_jeux
        self.all_events += events_actuel
        self.cartes_deja_jouees = cartes_deja_jouees

    def reset_pretty_play_joueurs(self, total_pretty_play_joueurs, pretty_play_joueurs, joueurs_pas_fini):
        if all(not len(el) for el in pretty_play_joueurs.values()):
            a = 3
        for i in range(len(self.players)):
            action_jouee = pretty_actions_jouees([el2 for el in pretty_play_joueurs[i] for el2 in el])
            if i not in joueurs_pas_fini and action_jouee == "":
                action_jouee = "x"
            total_pretty_play_joueurs[i].append(action_jouee)
        pretty_play_joueurs = {i: [] for i in range(len(self.players))}
        return total_pretty_play_joueurs, pretty_play_joueurs

    def show_game(self):
        print("".join([el for el in self.all_events]))
