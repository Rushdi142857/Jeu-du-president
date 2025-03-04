import logging

import pandas as pd

from president_game.logger import init_logger
# pd.options.plotting.backend = "plotly"

from president_game.player import DumbPlayer, AggressivePlayer, CheatPlayer, SlowPlayer
from president_game.partie import Partie
import plotly.express as px
from itertools import permutations


logger = logging.getLogger()

class Etudes:
    @staticmethod
    def priorite_joueur_1():
        """
        Quantifie l'avantage de jouer en premier joueur
        """
        nb_joueurs = 5
        players = [DumbPlayer() for _ in range(nb_joueurs)]
        scores_joueurs = [0 for _ in range(nb_joueurs)]
        # role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez"]
        role_players = ["Joueur1", "Joueur2", "Joueur3", "Joueur4", "Joueur5"]
        total_parties = 500
        total_parties_played = 0
        for _ in range(total_parties):
            try:
                p = Partie(
                    nb_joueurs=nb_joueurs,
                    nb_rangs_cartes=13,
                    players=players,
                    role_players=role_players,
                    save_events=False,
                )
                p.play_whole_game_from_cards()
                # print(p.classement)
                for i, ind_joueur in enumerate(p.classement):
                    # scores_joueurs[ind_joueur].append(scores_joueurs[ind_joueur][-1] + 3-i)
                    # scores_joueurs[ind_joueur] += 3-i
                    if i == 0:
                        scores_joueurs[ind_joueur] += 1
                    # scores_joueurs[ind_joueur] += 3-i
                total_parties_played += 1
            except NotImplementedError:
                continue

        dic_indics = {}
        # columns_df = ["ScoreTrou", "ScorePrez", "Score"]
        columns_df = ["Score"]
        for ind_player in range(nb_joueurs):
            dic_indics[role_players[ind_player]] = [
                scores_joueurs[ind_player] / total_parties
            ]
        df = pd.DataFrame.from_dict(dic_indics, orient="index", columns=columns_df)
        # df = df.reindex(["Prez", "Vice-Prez", "Vice-Trou", "Trou"])
        fig = px.line(df)
        fig.show()

    @staticmethod
    def avantage_president():
        """
        Quantifie l'avantage du président
        """
        nb_joueurs = 5
        players = [DumbPlayer() for _ in range(nb_joueurs)]
        scores_joueurs = [0 for _ in range(nb_joueurs)]
        role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez", "Neutre"]
        total_parties = 2
        total_parties_played = 0
        for _ in range(total_parties):
            try:
                p = Partie(
                    nb_joueurs=nb_joueurs,
                    nb_rangs_cartes=13,
                    players=players,
                    role_players=role_players,
                    save_events=False,
                )
                p.play_whole_game_from_cards()
                for i, ind_joueur in enumerate(p.classement):
                    scores_joueurs[ind_joueur] += 4 - i
                total_parties_played += 1
            except NotImplementedError:
                continue

        dic_indics = {}
        columns_df = ["Score"]
        for ind_player in range(nb_joueurs):
            dic_indics[role_players[ind_player]] = [scores_joueurs[ind_player]]
        df = pd.DataFrame.from_dict(dic_indics, orient="index", columns=columns_df)
        df = df.reindex(["Prez", "Vice-Prez", "Neutre", "Vice-Trou", "Trou"])
        fig = px.line(df)
        fig.show()

    @staticmethod
    def coherence_une_partie():
        """
        Affiche le déroulé d'une partie
        """
        logger.info("Lancement d'une partie")
        nb_joueurs = 5
        players = [AggressivePlayer() for _ in range(nb_joueurs)]
        role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez", "Neutre"]
        # role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez", "Neutre"]
        p = Partie(
            nb_joueurs=nb_joueurs,
            nb_rangs_cartes=13,
            players=players,
            role_players=role_players,
            save_events=True,
        )
        p.play_whole_game_from_cards()
        p.show_game()

    @staticmethod
    def force_joueurs():
        """
        Compare la force de plusieurs joueurs (2 ou plus)
        """
        classe_joueurs = [DumbPlayer, AggressivePlayer]
        name_players = [el().get_name() for el in classe_joueurs]
        nb_joueurs = 2 * len(classe_joueurs)
        players = [
            classe_joueurs[i]()
            for i in range(nb_joueurs // len(classe_joueurs))
            for _ in range(2)
        ]
        arrangements_joueurs = list(set(permutations(players)))

        roles = ["Prez", "Vice-Prez", "Vice-Trou", "Trou"] + ["Neutre"] * (
            nb_joueurs - 4
        )
        arrangement_roles = list(set(permutations(roles)))

        nb_iters = 2
        score_joueurs = [0 for _ in range(len(classe_joueurs))]
        total_parties_played = 0
        for _ in range(nb_iters):
            for arrangement_joueur in arrangements_joueurs:
                for arrangement_role in arrangement_roles:
                    try:
                        p = Partie(
                            nb_joueurs=nb_joueurs,
                            nb_rangs_cartes=13,
                            players=arrangement_joueur,
                            role_players=arrangement_role,
                            save_events=False,
                        )
                        p.play_whole_game_from_cards()
                        for i, ind_joueur in enumerate(p.classement):
                            real_index_joueur = name_players.index(
                                arrangement_joueur[ind_joueur].get_name()
                            )
                            score_joueurs[real_index_joueur] += 4 - i
                        total_parties_played += 1
                    except NotImplementedError:
                        continue

        dic_indics = {}
        columns_df = ["Score"]
        for ind_player, name_player in enumerate(name_players):
            dic_indics[name_player] = [score_joueurs[ind_player]]
        df = pd.DataFrame.from_dict(dic_indics, orient="index", columns=columns_df)
        fig = px.line(df)
        fig.show()

    @staticmethod
    def variete_joueurs():
        """
        Teste différents joueurs
        """
        logger.info("Lancement d'une partie")
        nb_joueurs = 5
        players = [DumbPlayer(), CheatPlayer(), SlowPlayer(), AggressivePlayer(), AggressivePlayer()]
        # role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez", "Neutre"]
        role_players = ["Neutre"]*5
        # role_players = ["Trou", "Prez", "Vice-Trou", "Vice-Prez", "Neutre"]
        p = Partie(
            nb_joueurs=nb_joueurs,
            nb_rangs_cartes=13,
            players=players,
            role_players=role_players,
            save_events=True,
        )
        p.play_whole_game_from_cards()
        p.show_game()

    def partie_reelle(nb_joueurs):
        # A écrire
        pass


if __name__ == "__main__":
    # TODO : vision stylisée d'une partie
    init_logger()
    # Etudes.avantage_president()
    Etudes.coherence_une_partie()
    # Etudes.variete_joueurs()
    # Etudes.force_joueurs()
