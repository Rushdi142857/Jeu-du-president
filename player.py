from abc import ABC, abstractmethod

from president_game.utils import convert_sorted_hand_to_dict


class Player(ABC):
    main: list[int]
    name: str | None = None

    @abstractmethod
    def que_jouer(
        self,
        main: list[int],
        cartes_plateau: list[list[int]],
        risque_saut: bool,
        historique_jeux: list[int],
    ) -> list[int] | None:
        """
        Votre jeu ! Vous devez renvoyer une des cartes de votre main

        :param main: list[int] votre main actuelle (au cas où vous l'aurez oubliée)
        C'est un dictionnaire de numéros entre 0 et 13 avec pour valeur le nombre de cartes que vous possédez
        Par exemple, si votre main est 0.0.3.5.5.9.9.9.11.12
        (qui correspond dans le vrai jeu à 3.3.6.8.8.Q.Q.Q.A.2), je vous renvoie:
        [0,0,3,5,5,9,9,9,11,12]
        :param cartes_plateau: (list[list[int]]) les cartes qui sont actuellement au centre
        Par exemple, s'il a été joué 0.0, puis 2.2, puis 7.7, je vous renvoie:
        [[0,0], [2,2], [7,7]]
        Si rien n'a encore été joué, la liste est vide
        :param risque_saut: (bool) True si vous allez être sauté si vous ne jouez pas une carte identique. Impossible de tricher.
        :param historique_jeux: (list[int]) Ensemble des cartes qui ont déjà été jouées
        C'est du même format que votre main.
        :return: (list[int]) | None La ou les cartes de votre main que vous jouez. None si vous ne jouez rien.
        Par exemple, si vous voulez jouer 10.10.10 (Qui correspond à K.K.K dans le vrai jeu),
        vous devez renvoyer [10, 10, 10]
        """
        pass

    @staticmethod
    def mapping():
        return {
            0: "3",
            1: "4",
            2: "5",
            3: "6",
            4: "7",
            5: "8",
            6: "9",
            7: "10",
            8: "J",
            9: "Q",
            10: "K",
            11: "A",
            12: "2",
        }

    def donner_main(self, main: list[int]):
        self.main = main

    def give_cards_prez_to_trou(self, main: list[int]) -> list[int]:
        """
        Si vous êtes prez, indiquez moi les cartes que vous donnez au trou
        Par défaut, vous donnez vos 2 cartes les plus faibles

        :param main: Votre main après que vous ayez reçu les 2 cartes du trou
        """
        return main[:2]

    def give_card_vice_prez_to_vice_trou(self, main: list[int]) -> int:
        """
        Si vous êtes vice-prez, indiquez moi la carte que vous donnez au vice-trou
        Par défaut, vous donnez votre plus faible carte

        :param main: Votre main après que vous ayez reçu la carte du vice-trou
        """
        return main[0]

    def get_name(self) -> str:
        """
        Votre nom de joueur
        """
        # return "MonNomdeJoueur"
        pass


class DumbPlayer(Player):
    def get_name(self):
        return "DumbPlayer"

    def que_jouer(self, main, cartes_plateau, risque_saut, historique_jeux):
        """
        Stratégie la plus basique : On joue si on a plus fort, mais on ne casse pas les doubles ou les triples
        """
        main_dict = convert_sorted_hand_to_dict(main)
        if not cartes_plateau:
            # On considère que, si on a la main, on joue notre ou nos plus faibles cartes
            lowest_value = min(main_dict)
            return [lowest_value for _ in range(main_dict[lowest_value])]
        else:
            cartes_au_dessus = cartes_plateau[-1]
            type_jeu = len(cartes_au_dessus)
            nombre_joue = cartes_au_dessus[0]
            """
            On ne considère que les cartes supérieures et du même type que le centre
            On ne casse pas les doubles ou les triples
            """

            if not risque_saut:
                mains_possibles = [
                    el[0]
                    for el in main_dict.items()
                    if el[0] >= nombre_joue and el[1] == type_jeu
                ]
            else:
                mains_possibles = [
                    el[0]
                    for el in main_dict.items()
                    if el[0] == nombre_joue and el[1] == type_jeu
                ]
            if not mains_possibles:
                return None
            else:
                lowest_value = min(mains_possibles)
                return [lowest_value for _ in range(main_dict[lowest_value])]


class AggressivePlayer(Player):
    def get_name(self):
        return "AggressivePlayer"

    def que_jouer(self, main, cartes_plateau, risque_saut, historique_jeux):
        """
        Stratégie aggressive : On joue si on a plus fort, et on casse nos doubles et triples si besoin
        """
        main_dict = convert_sorted_hand_to_dict(main)
        if not cartes_plateau:
            # On considère que, si on a la main, on joue notre ou nos plus faibles cartes
            lowest_value = min(main_dict)
            return [lowest_value for _ in range(main_dict[lowest_value])]
        else:
            cartes_au_dessus = cartes_plateau[-1]
            type_jeu = len(cartes_au_dessus)
            nombre_joue = cartes_au_dessus[0]
            """
            On ne considère que les cartes supérieures et du même type que le centre
            """
            type_essaye = type_jeu
            # On tente les simples, puis les doubles, puis les triples
            while type_essaye <= 3:
                if not risque_saut:
                    jeux_possibles = [
                        el[0]
                        for el in main_dict.items()
                        if el[0] >= nombre_joue and el[1] == type_essaye
                    ]
                else:
                    jeux_possibles = [
                        el[0]
                        for el in main_dict.items()
                        if el[0] == nombre_joue and el[1] == type_essaye
                    ]
                if jeux_possibles:
                    lowest_value = min(jeux_possibles)
                    return [lowest_value for _ in range(type_jeu)]
                type_essaye += 1
            # On n'a rien trouvé à jouer
            return None
