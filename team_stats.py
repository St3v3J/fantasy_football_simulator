import pandas as pd

class Team:
    def __init__(self, name, roster_df):
        self.name = name
        self.players = roster_df
        self.qb_skill = self.calculate_qb_skill()
        self.rushing_avg = self.calculate_rushing_avg()
        self.pass_yards_total = self.players['passing_yards'].sum()
        self.run_yards_total = self.players['rushing_yards'].sum()
        self.sacks = self.players['sacks'].sum()
        self.interceptions = self.players['interceptions'].sum()

    def calculate_qb_skill(self):
        qbs = self.players[self.players['position'] == 'QB']
        if len(qbs) == 0:
            return 0.03  # fallback default
        return qbs['completion_pct'].mean() / 100

    def calculate_rushing_avg(self):
        rb = self.players[self.players['position'] == 'RB']
        if len(rb) == 0:
            return 4.0  # fallback average
        return rb['rushing_yards'].sum() / max(rb['rushing_attempts'].sum(), 1)
