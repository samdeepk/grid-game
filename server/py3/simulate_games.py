"""Simulation script for concurrent grid-based games.

This script simulates multiple concurrent games across multiple players,
asserts correctness of game outcomes, and outputs top 3 players by win ratio.
"""
import asyncio
import argparse
import random
from typing import List, Dict, Tuple
from collections import defaultdict
import httpx


# Default configuration
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_NUM_PLAYERS = 10
DEFAULT_NUM_GAMES = 50
DEFAULT_CONCURRENCY = 5


class GameSimulator:
    """Simulates concurrent games."""
    
    def __init__(self, base_url: str, num_players: int, num_games: int, concurrency: int):
        self.base_url = base_url
        self.num_players = num_players
        self.num_games = num_games
        self.concurrency = concurrency
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.players: List[Dict] = []
        self.stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0})
    
    async def create_player(self, player_num: int) -> Dict:
        """Create a player and return player data."""
        response = await self.client.post(
            "/users",
            json={"name": f"Player{player_num}", "icon": "🎮"}
        )
        if response.status_code != 201:
            raise Exception(f"Failed to create player: {response.status_code} {response.text}")
        return response.json()
    
    async def create_session(self, host: Dict) -> Dict:
        """Create a game session."""
        response = await self.client.post(
            "/sessions",
            json={
                "hostId": host["id"],
                "hostName": host["name"],
                "gameIcon": "🎯",
                "gameType": "tic_tac_toe"
            }
        )
        if response.status_code != 201:
            raise Exception(f"Failed to create session: {response.status_code} {response.text}")
        return response.json()
    
    async def join_session(self, session_id: str, player: Dict) -> Dict:
        """Join a session as guest."""
        response = await self.client.post(
            f"/sessions/{session_id}/join",
            json={"playerId": player["id"]}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to join session: {response.status_code} {response.text}")
        return response.json()
    
    async def make_move(self, session_id: str, player_id: str, row: int, col: int) -> Dict:
        """Make a move in a session."""
        response = await self.client.post(
            f"/sessions/{session_id}/move",
            json={"playerId": player_id, "row": row, "col": col}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to make move: {response.status_code} {response.text}")
        return response.json()
    
    async def get_session(self, session_id: str) -> Dict:
        """Get current session state."""
        response = await self.client.get(f"/sessions/{session_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get session: {response.status_code} {response.text}")
        return response.json()
    
    def get_available_cell(self, board: List[List]) -> Tuple[int, int]:
        """Get a random available cell from the board."""
        available = []
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] is None:
                    available.append((row, col))
        if not available:
            return None
        return random.choice(available)
    
    async def play_game(self, host: Dict, guest: Dict) -> Dict:
        """Play a complete game between two players."""
        try:
            # Create session
            session = await self.create_session(host)
            session_id = session["id"]
            
            # Join session
            session = await self.join_session(session_id, guest)
            
            # Assert: Session should be ACTIVE after both players join
            assert session["status"] == "ACTIVE", f"Session should be ACTIVE, got {session['status']}"
            assert len(session["players"]) == 2, f"Should have 2 players, got {len(session['players'])}"
            assert session["currentTurn"] is not None, "currentTurn should be set"
            
            # Play game
            move_count = 0
            max_moves = 9  # 3x3 grid
            
            while session["status"] == "ACTIVE" and move_count < max_moves:
                current_player_id = session["currentTurn"]
                board = session["board"]
                
                # Get available cell
                cell = self.get_available_cell(board)
                if cell is None:
                    break
                
                row, col = cell
                
                # Make move
                session = await self.make_move(session_id, current_player_id, row, col)
                move_count += 1
                
                # Assert: Move should be recorded
                assert len(session["moves"]) == move_count, f"Expected {move_count} moves, got {len(session['moves'])}"
                assert session["board"][row][col] == current_player_id, "Board should be updated"
            
            # Assert: Game should be finished
            assert session["status"] == "FINISHED", f"Game should be FINISHED, got {session['status']}"
            
            # Record stats
            winner = session.get("winner")
            is_draw = session.get("draw", False)
            
            if is_draw:
                self.stats[host["id"]]["draws"] += 1
                self.stats[guest["id"]]["draws"] += 1
            elif winner:
                if winner == host["id"]:
                    self.stats[host["id"]]["wins"] += 1
                    self.stats[guest["id"]]["losses"] += 1
                else:
                    self.stats[guest["id"]]["wins"] += 1
                    self.stats[host["id"]]["losses"] += 1
            
            self.stats[host["id"]]["games"] += 1
            self.stats[guest["id"]]["games"] += 1
            
            return {
                "session_id": session_id,
                "winner": winner,
                "draw": is_draw,
                "moves": move_count,
                "status": "success"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def simulate_concurrent_games(self):
        """Simulate multiple concurrent games."""
        print(f"Creating {self.num_players} players...")
        
        # Create players
        create_tasks = [self.create_player(i) for i in range(self.num_players)]
        self.players = await asyncio.gather(*create_tasks)
        print(f"✓ Created {len(self.players)} players")
        
        print(f"\nSimulating {self.num_games} games with concurrency={self.concurrency}...")
        
        # Create game tasks
        game_tasks = []
        for _ in range(self.num_games):
            host = random.choice(self.players)
            guest = random.choice([p for p in self.players if p["id"] != host["id"]])
            game_tasks.append(self.play_game(host, guest))
        
        # Execute games with concurrency limit
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def bounded_game(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[bounded_game(task) for task in game_tasks])
        
        # Count successes and errors
        successes = sum(1 for r in results if r.get("status") == "success")
        errors = sum(1 for r in results if r.get("status") == "error")
        
        print(f"✓ Completed {successes} games successfully")
        if errors > 0:
            print(f"⚠ {errors} games had errors")
            for r in results:
                if r.get("status") == "error":
                    print(f"  Error: {r.get('error')}")
        
        await self.client.aclose()
    
    def print_leaderboard(self):
        """Print top 3 players by win ratio."""
        print("\n" + "="*60)
        print("LEADERBOARD - Top 3 Players by Win Ratio")
        print("="*60)
        
        # Calculate win ratios
        player_ratios = []
        for player_id, stats in self.stats.items():
            if stats["games"] > 0:
                win_ratio = stats["wins"] / stats["games"]
                player_ratios.append({
                    "player_id": player_id,
                    "name": next((p["name"] for p in self.players if p["id"] == player_id), player_id),
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "draws": stats["draws"],
                    "games": stats["games"],
                    "win_ratio": win_ratio
                })
        
        # Sort by win ratio (descending)
        player_ratios.sort(key=lambda x: x["win_ratio"], reverse=True)
        
        # Print top 3
        for i, player in enumerate(player_ratios[:3], 1):
            print(f"\n{i}. {player['name']} (ID: {player['player_id'][:8]}...)")
            print(f"   Win Ratio: {player['win_ratio']:.2%}")
            print(f"   Wins: {player['wins']}, Losses: {player['losses']}, Draws: {player['draws']}")
            print(f"   Total Games: {player['games']}")
        
        if len(player_ratios) == 0:
            print("\nNo players with completed games.")
        
        print("\n" + "="*60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simulate concurrent grid-based games")
    parser.add_argument(
        "--base-url",
        type=str,
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--players",
        type=int,
        default=DEFAULT_NUM_PLAYERS,
        help=f"Number of players (default: {DEFAULT_NUM_PLAYERS})"
    )
    parser.add_argument(
        "--games",
        type=int,
        default=DEFAULT_NUM_GAMES,
        help=f"Number of games to simulate (default: {DEFAULT_NUM_GAMES})"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent games (default: {DEFAULT_CONCURRENCY})"
    )
    
    args = parser.parse_args()
    
    simulator = GameSimulator(
        base_url=args.base_url,
        num_players=args.players,
        num_games=args.games,
        concurrency=args.concurrency
    )
    
    try:
        await simulator.simulate_concurrent_games()
        simulator.print_leaderboard()
    except Exception as e:
        print(f"Simulation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

