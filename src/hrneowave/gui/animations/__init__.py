# -*- coding: utf-8 -*-
"""Surface minimale pour les animations encore utilisées par la GUI active."""

from .animation_system import (
    AnimationPreset,
    AnimationType,
    MaritimeAnimator,
    animate_widget,
    get_animator,
)
from .micro_interactions import (
    InteractionState,
    MaritimeMicroInteractions,
    get_micro_interactions,
)

__version__ = "1.0.0"

__all__ = [
    "MaritimeAnimator",
    "AnimationType",
    "AnimationPreset",
    "get_animator",
    "animate_widget",
    "MaritimeMicroInteractions",
    "InteractionState",
    "get_micro_interactions",
    "setup_maritime_animations",
    "cleanup_animations",
    "get_animation_system",
]

_global_animator = None
_global_micro_interactions = None


def setup_maritime_animations(stacked_widget=None):
    """Initialise uniquement les briques encore consommées par le runtime."""
    del stacked_widget
    global _global_animator, _global_micro_interactions

    if _global_animator is None:
        _global_animator = MaritimeAnimator()
    if _global_micro_interactions is None:
        _global_micro_interactions = MaritimeMicroInteractions()

    return {
        "animator": _global_animator,
        "micro_interactions": _global_micro_interactions,
    }


def cleanup_animations():
    """Nettoie les animations encore exposées par ce paquet."""
    global _global_animator, _global_micro_interactions

    if _global_animator:
        _global_animator.stop_all_animations()
    if _global_micro_interactions:
        _global_micro_interactions.cleanup_all_interactions()


def get_animation_system():
    """Retourne les services d'animation encore supportés."""
    return {
        "animator": get_animator(),
        "micro_interactions": get_micro_interactions(),
    }
