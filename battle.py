import random

CLASSES = {

    "Tank": {
        "hp": 900,
        "attack": 65,
        "block": 0.35,
        "speed": 1
    },

    "Support": {
        "hp": 600,
        "attack": 20,
        "speed": 2
    },

    "Archer": {
        "hp": 560,
        "attack": 110,
        "speed": 3
    },

    "Assassin": {
        "hp": 500,
        "attack": 120,
        "crit": 0.25,
        "speed": 4
    }
}


class Hero:

    def __init__(self, role):

        self.role = role

        self.max_hp = CLASSES[role]["hp"]
        self.hp = self.max_hp

        self.attack = CLASSES[role]["attack"]
        self.speed = CLASSES[role]["speed"]

        self.damage_buff = 0

        # Statistics

        self.damage_done = 0
        self.healing_done = 0
        self.damage_buff_given = 0
        self.damage_blocked = 0
        self.kills = 0
        self.turns_taken = 0

        # Archer Focus Fire
        self.focus_stacks = 0
        self.last_target_role = None

        if role == "Tank":
            self.block = CLASSES[role]["block"]

        if role == "Assassin":
            self.crit = CLASSES[role]["crit"]

    def alive(self):
        return self.hp > 0


def apply_synergies(team):

    roles = [hero.role for hero in team]

    # Double Tank
    if roles.count("Tank") >= 2:

        for hero in team:

            if hero.role == "Tank":

                hero.max_hp += 200
                hero.hp += 200

    # Double Archer
    if roles.count("Archer") >= 2:

        for hero in team:

            if hero.role == "Archer":

                hero.attack += 20

    # Double Assassin
    if roles.count("Assassin") >= 2:

        for hero in team:

            if hero.role == "Assassin":

                hero.hp += 35


NORMAL_PRIORITY = [
    "Tank",
    "Support",
    "Archer",
    "Assassin"
]

ASSASSIN_PRIORITY = [
    "Support",
    "Archer",
    "Tank",
    "Assassin"
]


def get_target(attacker, enemies):

    alive = [e for e in enemies if e.alive()]

    if not alive:
        return None

    priority = (
        ASSASSIN_PRIORITY
        if attacker.role == "Assassin"
        else NORMAL_PRIORITY
    )

    for role in priority:

        for enemy in alive:

            if enemy.role == role:
                return enemy

    return random.choice(alive)


def support_action(support, team):

    alive = [h for h in team if h.alive()]

    support_count = sum(
        1 for h in alive
        if h.role == "Support"
    )

    heal_bonus = 60 if support_count >= 2 else 0

    low_hp = [
        h for h in alive
        if h.hp < 0.5 * h.max_hp
    ]

    if low_hp:

        target = min(
            low_hp,
            key=lambda h: h.hp
        )

        heal_amount = 100 + heal_bonus

        actual_heal = min(
        heal_amount,
        target.max_hp - target.hp
        )

        target.hp += actual_heal

        support.healing_done += actual_heal

    else:

        target = max(
            alive,
            key=lambda h: h.attack
        )

        target.damage_buff += 40

        support.damage_buff_given += 40


def attack(attacker, target, target_team):

    damage = (
        attacker.attack
        + attacker.damage_buff
    )

    # Assassin Crit
    if (
        attacker.role == "Assassin"
        and random.random() < attacker.crit
    ):
        damage *= 1.5

    # Archer Focus Fire
    if attacker.role == "Archer":

        if attacker.last_target_role == target.role:
            attacker.focus_stacks += 1
        else:
            attacker.focus_stacks = 0

        damage += attacker.focus_stacks * 10

        attacker.last_target_role = target.role

    # Guardian Aura
    living_tank_exists = (
        attacker.role != "Archer"
        and any(
            hero.alive() and hero.role == "Tank"
            for hero in target_team
        )
    )

    if (
        target.role != "Tank"
        and living_tank_exists
    ):
        damage *= 0.9

    # Tank Block
    if (
        target.role == "Tank"
        and random.random() < target.block
    ):
        blocked = damage * 0.5

        target.damage_blocked += blocked

        damage *= 0.5

    target.hp -= damage

    if target.hp <= 0:
        attacker.kills += 1

    attacker.damage_done += damage

    attacker.damage_buff = 0


def apply_death_zone(team1, team2, round_num):

    if round_num <= 10:
        return

    zone_damage = (
        ((round_num - 1) // 10)
        * 10
    )

    for hero in team1 + team2:

        if hero.alive():
            hero.hp -= zone_damage


def simulate_battle(team1_roles, team2_roles):

    team1 = [Hero(r) for r in team1_roles]
    team2 = [Hero(r) for r in team2_roles]
    
    apply_synergies(team1)
    apply_synergies(team2)

    battle_info = {
    "team1": team1,
    "team2": team2,
    "rounds": 0
    }

    rounds = 0

    while True:

        battle_info["rounds"] = rounds

        apply_death_zone(
            team1,
            team2,
            rounds
        )

        if not any(h.alive() for h in team1):
            return (
                "Team2",
                battle_info
            )

        if not any(h.alive() for h in team2):
            return (
                "Team1",
                battle_info
            )
        
        rounds += 1

        if rounds > 250:

            team1_hp = sum(
                max(0, h.hp)
                for h in team1
            )

            team2_hp = sum(
                max(0, h.hp)
                for h in team2
            )

            if team1_hp > team2_hp:
                return (
                    "Team1",
                    battle_info
                )
            else:
                return (
                    "Team2",
                    battle_info
                )

        turn_order = []

        for hero in team1:

            if hero.alive():
                turn_order.append(
                    (
                        hero.speed + random.uniform(0,1),
                        hero,
                        team1,
                        team2
                    )
                )

        for hero in team2:

            if hero.alive():
                turn_order.append(
                    (
                        hero.speed + random.uniform(0, 1),
                        hero,
                        team2,
                        team1
                    )
                )
        

        turn_order.sort(
            key=lambda x: x[0],
            reverse=True
        )

        for _, hero, own_team, enemy_team in turn_order:

            if not hero.alive():
                continue

            hero.turns_taken += 1

            if hero.role == "Support":

                support_action(
                    hero,
                    own_team
                )

                continue

            target = get_target(
                hero,
                enemy_team
            )

            if target:

                attack(
                    hero,
                    target,
                    enemy_team
                )


def get_team_stats(team):

    stats = {
        "damage": {},
        "healing": {},
        "blocked": {},
        "kills": {},
        "turns": {}
    }

    for hero in team:

        stats["damage"][hero.role] = (
            stats["damage"].get(hero.role, 0)
            + round(hero.damage_done, 1)
        )

        stats["healing"][hero.role] = (
            stats["healing"].get(hero.role, 0)
            + round(hero.healing_done, 1)
        )

        stats["blocked"][hero.role] = (
            stats["blocked"].get(hero.role, 0)
            + round(hero.damage_blocked, 1)
        )

        stats["kills"][hero.role] = (
            stats["kills"].get(hero.role, 0)
            + hero.kills
        )

        stats["turns"][hero.role] = (
            stats["turns"].get(hero.role, 0)
            + hero.turns_taken
        )

    return stats


def get_mvp(team):

    return max(
        team,
        key=lambda h:
        h.damage_done
        + h.healing_done
        + h.damage_blocked
        + h.damage_buff_given
        + (h.kills * 100)
    )


def win_rate(team1, team2, n=100):

    wins = 0

    for _ in range(n):

        result, _ = simulate_battle(
            team1,
            team2
        )

        if result == "Team1":
            wins += 1

    return wins / n


def matchup_probability(team1, team2):

    return win_rate(
        team1,
        team2,
        n=500
    )