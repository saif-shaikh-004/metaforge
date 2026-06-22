import streamlit as st
import pandas as pd
import random
import base64
import os
from collections import Counter
from sheets import save_battle
from datetime import datetime

from battle import (
    simulate_battle,
    matchup_probability,
    get_team_stats,
    get_mvp
)

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="MetaForge",
    page_icon="⚔️",
    layout="wide"
)


# ----------------------------------
# SIDEBAR
# ----------------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Play Trial",
        "Characters & Synergies",
        "Rules",
        "Statistics",
        "Future Content"
    ]
)

# ----------------------------------
# HOME
# ----------------------------------

if page == "Home":

    st.image(
        "background_image.png",
        use_container_width=True
    )

    st.title("⚔️ MetaForge ⚔️")

    st.markdown("""
    ### Welcome Challenger

    Build a team of 3 heroes.

    Defeat powerful boss teams.

    Discover winning strategies and hidden synergies.

    ---
    """)

    st.info(
        "This Trial Version is designed to teach the mechanics before the full tournament version."
    )


# ----------------------------------
# PLAY TRIAL
# ----------------------------------

elif page == "Play Trial":

    st.header("⚔️ Trial Battle")

    st.write(
        "Select your team and challenge a random boss."
    )

    hero_pool = [
        "Tank",
        "Support",
        "Archer",
        "Assassin"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        hero1 = st.selectbox(
            "Hero 1",
            hero_pool,
            key="h1"
        )

    with col2:
        hero2 = st.selectbox(
            "Hero 2",
            hero_pool,
            key="h2"
        )

    with col3:
        hero3 = st.selectbox(
            "Hero 3",
            hero_pool,
            key="h3"
        )

    player_team = [
        hero1,
        hero2,
        hero3
    ]

    bosses = [
        ["Tank","Archer","Support"],
        ["Tank","Assassin","Archer"],
        ["Assassin","Assassin","Tank"],
        ["Tank","Tank","Assassin"],
        ["Tank","Archer","Archer"]
    ]

    if st.button("Fight Boss"):

        boss = random.choice(bosses)

        st.subheader("Boss Team")

        st.write(boss)

        result, battle_info = simulate_battle(
            player_team,
            boss
        )

        chance = matchup_probability(
            player_team,
            boss
        )

        if result == "Team1":

            st.success("🏆 Victory!")

            if chance < 0.50:

                st.balloons()

                st.write(
                    "You won despite being the underdog!"
                )

        else:

            st.error("☠️ Defeat!")
        
        player_stats = battle_info["team1"]

        mvp = get_mvp(player_stats)

        st.subheader("🏆 MVP")

        st.success(mvp.role)

        st.subheader("⏱ Battle Length")

        st.info(
            f"{battle_info['rounds']} rounds"
        )

        st.subheader("📊 Character Performance")

        for hero in player_stats:

            st.write(
                f"""
                **{hero.role}**

                Damage Dealt: {round(hero.damage_done)}

                Healing Done: {round(hero.healing_done)}

                Damage Buff Given: {round(hero.damage_buff_given)}
                
                Damage Blocked: {round(hero.damage_blocked)}

                Kills: {hero.kills}

                Turns Taken: {hero.turns_taken}
                """
            )

        st.subheader("Battle Analysis")

        st.write(
            f"Estimated Win Chance: {round(chance*100,1)}%"
        )

        if chance >= 0.70:

            st.write(
                "Your team was heavily favored."
            )

        elif chance >= 0.50:

            st.write(
                "Your team had a slight advantage."
            )

        elif chance >= 0.30:

            st.write(
                "This was a difficult matchup."
            )

        else:

            st.write(
                "This was an extremely difficult matchup."
            )

        # SAVE RESULT

        save_battle([

            datetime.now().isoformat(),

            str(player_team),

            str(boss),

                "Win"
                if result == "Team1"
                else "Loss"
            ,

                battle_info["rounds"]
            ,

            mvp.role,

            # DAMAGE

                round(
                    sum(
                        h.damage_done
                        for h in player_stats
                        if h.role == "Tank"
                    )
                )
            ,

                round(
                    sum(
                        h.damage_done
                        for h in player_stats
                        if h.role == "Archer"
                    )
                )
            ,

                round(
                    sum(
                        h.damage_done
                        for h in player_stats
                        if h.role == "Assassin"
                    )
                )
            ,

            # SUPPORT

                round(
                    sum(
                        h.healing_done
                        for h in player_stats
                        if h.role == "Support"
                    )
                )
            ,

                round(
                    sum(
                        h.damage_buff_given
                        for h in player_stats
                        if h.role == "Support"
                    )
                )
            ,

            # BLOCKED DAMAGE

                round(
                    sum(
                        h.damage_blocked
                        for h in player_stats
                        if h.role == "Tank"
                    )
                )
            ,

            # KILLS

                sum(
                    h.kills
                    for h in player_stats
                    if h.role == "Tank"
                )
            ,

                sum(
                    h.kills
                    for h in player_stats
                    if h.role == "Archer"
                )
            ,

                sum(
                    h.kills
                    for h in player_stats
                    if h.role == "Assassin"
                )
            ,

                sum(
                    h.kills
                    for h in player_stats
                    if h.role == "Support"
                )
            ,

            # TURNS TAKEN

                sum(
                    h.turns_taken
                    for h in player_stats
                    if h.role == "Tank"
                )
            ,

                sum(
                    h.turns_taken
                    for h in player_stats
                    if h.role == "Archer"
                )
            ,

                sum(
                    h.turns_taken
                    for h in player_stats
                    if h.role == "Assassin"
                )
            ,

                sum(
                    h.turns_taken
                    for h in player_stats
                    if h.role == "Support"
                )
            
        ])

# ----------------------------------
# CHARACTERS & SYNERGIES
# ----------------------------------

elif page == "Characters & Synergies":

    st.header("⚔️ Characters")

    col1, col2 = st.columns(2)

    with col1:
        st.image("tank_card.png")
        st.markdown("""
        ## 🛡 Tank

        HP: 900,
        Attack: 65,
        Speed: 1

        Ability:
        - 35% chance to block damage
        - Guardian Aura reduces damage taken by allies

        Role:
        Frontline protector.
        """)
        st.image("archer_card.png")
        st.markdown("""
        ## 🏹 Archer

        HP: 560,
        Attack: 110,
        Speed: 3

        Ability:
        - Focus Fire
        - Gains bonus damage when repeatedly attacking the same role

        Role:
        Sustained damage dealer.
        """)

    with col2:
        st.image("support_card.png")
        st.markdown("""
        ## 💚 Support

        HP: 600,
        Attack: 20,
        Speed: 2

        Ability:
        - Heals allies below 50% HP
        - Buffs ally damage when healing is not needed

        Role:
        Team sustain and utility.
        """)
        st.image("assassin_card.png")
        st.markdown("""
        ## 🗡 Assassin

        HP: 500,
        Attack: 120,
        Speed: 4

        Ability:
        - Targets enemy backline
        - 25% Critical Strike chance
        - Critical hits deal 1.5× damage

        Role:
        Eliminate Supports and Archers quickly.
        """)

    st.header("Coming Soon")

    st.image("mage_card.png")

    st.header("🤝 Synergies")

    st.markdown("""
        ## Double Tank

        Requirement:
        - 2 Tanks

        Bonus:
        - +200 HP to each Tank

        Purpose:
        Creates an extremely durable frontline.
        """)
    
    st.markdown("""
        ## Double Archer

        Requirement:
        - 2 Archers

        Bonus:
        - +20 Attack to each Archer

        Purpose:
        Strong sustained damage and tank breaking.
        """)
    
    st.markdown("""
        ## Double Assassin

        Requirement:
        - 2 Assassins

        Bonus:
        - +35 HP to each Assassin

        Purpose:
        Improves survivability while diving enemy backlines.
        """)
    
    st.markdown("""
        ## Double Support

        Requirement:
        - 2 Supports

        Bonus:
        - Healing increased by 60

        Purpose:
        - Creates an extremely durable team capable of surviving long fights.
        """)

# ----------------------------------
# RULES
# ----------------------------------

elif page == "Rules":

    st.header("Rules")

    st.markdown("""
    ## Objective

    Build a team of 3 heroes.

    Defeat the opposing team.

    ---

    ## Roles

    ### Tank
    Protects allies.

    ### Archer
    Sustained damage dealer.

    ### Assassin
    Backline hunter.

    ### Support
    Heals and buffs allies.

    ---

    ## Synergies

    Some duplicate class combinations receive bonuses.

    Experiment to discover strong team compositions.

    ---

    ## Death Zone

    After Round 10, environmental damage begins.

    Long battles become increasingly dangerous.

    ---

    ## Victory

    Eliminate all enemy heroes.
    """)

# ----------------------------------
# STATISTICS
# ----------------------------------

elif page == "Statistics":

    st.header("📊 Global Statistics")

    try:

        df = pd.read_csv("results.csv")

        st.metric(
            "Total Battles",
            len(df)
        )

        win_rate = (
            (df["result"] == "Win").mean()
            * 100
        )

        st.metric(
            "Overall Player Win Rate",
            f"{round(win_rate,1)}%"
        )

        st.divider()

        st.subheader(
            "Most Popular Teams"
        )

        teams = Counter(
            df["team"]
        )

        top_teams = teams.most_common(10)

        for team, count in top_teams:

            st.write(
                f"{team} — {count} battles"
            )

    except:

        st.warning(
            "No battle data found yet."
        )

# ----------------------------------
# FUTURE CONTENT
# ----------------------------------

elif page == "Future Content":

    st.header("🚀 Future Content")

    st.markdown("""
    The Trial Version is only the beginning.

    ## 🧙 New Characters

    Future heroes are planned, including:

    - Mage
    - Berserker
    - Necromancer

    Each hero will introduce new mechanics,
    synergies and team compositions.

    ---

    ## 🎒 Items

    Equip heroes with powerful items.

    Examples:

    - Critical Strike Dagger
    - Guardian Shield
    - Healing Staff
    - Hunter's Bow

    Items will allow multiple playstyles
    for the same hero.

    ---

    ## 🏰 Dungeon Mode

    Fight through multiple battles and 
    get rewarded for every successful encounter.

    Features:

    - Random enemy teams
    - Elite encounters
    - Boss fights
    - Increasing difficulty

    Can you survive the entire dungeon?

    ---

    ## 🏆 Tournament Mode

    Build the strongest team and compete.

    Features:

    - Leaderboards
    - Meta tracking
    - Seasonal tournaments
    - Community statistics

    Discover which strategies dominate
    the battlefield.

    ---

    ## 📊 Advanced Analytics

    Future versions will include:

    - Character pick rates
    - Team popularity
    - Global win rates
    - Matchup statistics
    - Meta reports
    - Updated UI
    - Adaptive AI Bosses

    Become a true RPG strategist.

    ---

    Thank you for playing the Trial Version!
    """)