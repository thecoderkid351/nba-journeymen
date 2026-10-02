import itertools
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

#Loading and cleaning 
data = pd.read_csv("nba_player_stats.csv")
rosters = data[~data["team"].str.contains("TM")]     

#Building network 
network = nx.Graph()
for (season, team), roster in rosters.groupby(["season", "team"]):
    players = roster["player"].tolist()
    for player1, player2 in itertools.combinations(players, 2):
        network.add_edge(player1, player2)
        
print("Players in network:", network.number_of_nodes())
print("Teammates in network:", network.number_of_edges())
 
teammates = dict(network.degree)
betweenness = nx.betweenness_centrality(network)
teams = rosters.groupby("player")["team"].nunique().to_dict()

results = pd.DataFrame({
    "teammates": pd.Series(teammates),
    "betweenness": pd.Series(betweenness),
    "team_size": pd.Series(teams)
})

results["journeyman"] = results["team_size"] >= 5

high_connections = results.sort_values("teammates", ascending=False)
network_connections = results.sort_values("betweenness", ascending=False)

print("\nTop 10 players with the most teammates:")
print(high_connections.head(10))
print("\nTop 10 players with the highest betweenness:")
print(network_connections.head(10))

journeyman_players = results[results["journeyman"]]
others = results[~results["journeyman"]]

print("\nJourneymen:", len(journeyman_players), "of", len(results), "players")
def average_teammates(players):
    average = players["teammates"].mean()
    return round(average) if pd.notna(average) else "N/A (no players)"


print("Average teammates (journeymen):", average_teammates(journeyman_players))
print("Average teammates (everyone else):", average_teammates(others))
print("Journeymen in top 50 most-connected:", high_connections.head(50)["journeyman"].sum())
print("Journeymen in top 50 bridges:", network_connections.head(50)["journeyman"].sum())

results.to_csv("player_results.csv")

#Top 15 Players with the most teammates
top15 = high_connections.head(15)
plt.figure(figsize=(9, 6))
plt.barh(top15.index, top15["teammates"], color="green")
plt.gca().invert_yaxis()  
plt.title("Top 15 Players with the Most Teammates ( From 2015-16 to 2025-26)")
plt.xlabel("Number of Teammates")
plt.ylabel("Player")
plt.savefig("top15_teammates.png")
plt.show()

#Average teammates by number of teams
avg_teammates = results.groupby("team_size")["teammates"].mean()
colors = ["brown" if size >= 5 else "blue" for size in avg_teammates.index]
plt.figure(figsize=(9, 6))
plt.bar(avg_teammates.index, avg_teammates.values, color=colors)
plt.title("Average Number of Teammates by Number of Teams Played For")
plt.xlabel("Number of Teams Played For")
plt.ylabel("Average Number of Teammates")
plt.savefig("avg_teammates.png")
plt.show()

#Network of 25 biggest connections
top25 = network_connections.head(25).index
bridge=network.subgraph(top25)
plt.figure(figsize=(12, 8))
ax = plt.gca()
nx.draw(bridge, pos=nx.spring_layout(bridge, seed=42, k=2), with_labels=True, node_color="skyblue", edge_color="gray", node_size=800, font_size=9)
ax.set_title("Network of 25 Players with the Highest Betweenness")
plt.savefig("top25_bridges.png")
plt.show()
