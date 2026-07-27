# ⚡ WORKFLOW : SCRIPT TO VIDEO

Ce workflow prend un **script brut** ou une **idée rédigée** et génère directement le package de production complet (Storyboard, Prompts Google Flow, Voix Off).

---

## 🛠️ Étape 1 : Analyse & découpage du script
1. Identifier la durée visée (Short 9:16 ou Vidéo HD 16:9).
2. Découper le script texte en **scènes numérotées (001, 002, 003...)**.
3. Associer à chaque scène :
   - Le texte exact de la Voix Off.
   - La durée / timecode estimé.
   - Le rôle narratif (Hook, Problem, Data, Insight, CTA).

---

## 🎨 Étape 2 : Direction Artistique & Prompts Visuels
1. Définir le style visuel général (ex: Cyberpunk Noir, Retro 90s Polaroid, Modern Minimalist Vector, Realistic Cinematic, etc.).
2. Pour chaque scène visuelle :
   - Rédiger le prompt détaillé pour Google Flow (`nano-banana-2` ou `vo3-omni-flow`).
   - Spécifier le ratio (`9:16` ou `16:9`).
   - Ajouter le texte d'annotation ou de graphique si nécessaire.

---

## 📦 Étape 3 : Package de livraison
Générer le document final de storyboard dans `creation_studio/outputs/[nom_du_projet]_storyboard.md` comprenant :
- La table des scènes et timecodes.
- Le carrousel des promts / visuels générés.
- Le script voix off formaté pour ElevenLabs.
