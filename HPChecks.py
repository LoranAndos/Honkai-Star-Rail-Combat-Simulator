from Enemy import Enemy
from Character import Character

def getCharHPRatio(char: Character) -> float:
    """Return a character's current HP ratio (0.0–1.0) for use in lightcones."""
    return (char.currHP / char.maxHP) if char.maxHP > 0 else 1.0


def getEnemyHPRatio(enemy: Enemy) -> float:
    """Return an enemy's current HP ratio (0.0–1.0) for use in lightcones."""
    return enemy.getHPRatio()


def getCharHPPercent(char: Character) -> float:
    """Return a character's HP as a percentage (0–100) for use in lightcones."""
    return getCharHPRatio(char) * 100.0


def getEnemyHPPercent(enemy: Enemy) -> float:
    """Return an enemy's HP as a percentage (0–100) for use in lightcones."""
    return enemy.getHPPercent()